import logging
from typing import List, Dict, Any, Optional, Tuple
from app.agents.telemetry.transfer_builder import SemanticTransfer
from app.agents.pattern_discovery.mapping_memory import global_mapping_memory

logger = logging.getLogger("ghosttrace.pattern_discovery.deviation_detector")


def format_clean_entity_label(raw_sel: str = "", entity_key: str = "") -> str:
    """Formats raw selectors or semantic entity keys into clean human-readable field labels without raw DOM IDs or static alias tables."""
    target = (entity_key or raw_sel or "").lower()
    token = target.split(":")[-1] if ":" in target else target
    token = token.replace("lbl_", "").replace("hdg_", "").replace("elem_", "").replace("#", "").replace(".", " ").strip()
    token = token.replace("source-", "").replace("target-", "").replace("source_", "").replace("target_", "")

    clean = token.replace("_", " ").replace("-", " ").strip().title()
    return clean if clean else "Field"



class DeviationDetector:
    """
    Expected vs Observed Mapping & Step Sequence Deviation Detector.
    
    Detects:
    1. Wrong destination field (e.g. pasting Invoice ID into Amount field)
    2. Missing step (e.g. skipping Amount step)
    3. Reordered step (e.g. pasting Vendor before Amount)
    """
    def __init__(self):
        self.baseline_sequence: List[Tuple[str, str]] = []
        self.resolved_selectors: Set[str] = set()

    def clear(self):
        """Resets detector state."""
        self.baseline_sequence.clear()
        self.resolved_selectors.clear()

    def resolve_selectors(self, selectors: List[str]):
        """Marks specific selectors as resolved to prevent re-flagging after HITL review."""
        for sel in selectors:
            if sel:
                clean_sel = sel.lower().replace("#", "").replace(".", "").replace("target-", "").replace("source-", "").strip()
                self.resolved_selectors.add(sel.lower().strip())
                self.resolved_selectors.add(clean_sel)

    def resolve_all_current(self):
        """Marks all active baseline destination selectors as resolved."""
        for s, d in self.baseline_sequence:
            clean_d = d.split(":")[-1].replace("elem_", "").replace("target_", "").lower().strip()
            self.resolved_selectors.add(d.lower().strip())
            self.resolved_selectors.add(clean_d)

    def set_sequence_template(self, transfers: List[SemanticTransfer]):
        """Sets the established baseline sequence template from the FIRST complete cycle only.
        Stops capturing when a source entity repeats, indicating the start of a new cycle."""
        seen_sources: set = set()
        one_cycle: List[Tuple[str, str]] = []
        for x in transfers:
            if x.is_immediate_correction:
                continue
            src_key = x.source_entity.lower()
            if src_key in seen_sources:
                break  # Source repeated — new cycle started, stop
            seen_sources.add(src_key)
            one_cycle.append((x.source_entity, x.destination_entity))
        self.baseline_sequence = one_cycle

    def detect_deviations(self, transfers: List[SemanticTransfer]) -> List[Dict[str, Any]]:
        """Detects deviations by comparing expected stable mappings & baseline sequences against observed transfers per cycle."""
        deviations: List[Dict[str, Any]] = []
        # Filter valid transfers (exclude immediate corrections and automated agent executions)
        valid_transfers = [
            x for x in transfers
            if not x.is_immediate_correction and not getattr(x, "is_automated", False)
        ]

        if not valid_transfers:
            return deviations

        # Group transfers into cycles, partitioning on source entity repetition if cycle_id is generic
        from collections import defaultdict
        cycles_map: Dict[str, List[SemanticTransfer]] = defaultdict(list)
        current_cyc_idx = 1
        seen_src_in_cyc = set()

        has_distinct_cycles = any(getattr(x, "cycle_id", None) and getattr(x, "cycle_id") != "cycle-1" for x in valid_transfers)

        for xfer in valid_transfers:
            raw_cyc = getattr(xfer, "cycle_id", None)
            if has_distinct_cycles and raw_cyc:
                cyc = raw_cyc
            else:
                sk = xfer.source_entity.lower()
                if sk in seen_src_in_cyc:
                    current_cyc_idx += 1
                    seen_src_in_cyc.clear()
                seen_src_in_cyc.add(sk)
                cyc = f"cycle-{current_cyc_idx}"

            cycles_map[cyc].append(xfer)

        # Establish baseline sequence from cycle-1 only when at least 2 cycles are present
        if len(cycles_map.keys()) >= 2 and "cycle-1" in cycles_map:
            self.set_sequence_template(cycles_map["cycle-1"])
        else:
            self.baseline_sequence = []

        if not self.baseline_sequence:
            return deviations

        baseline_len = len(self.baseline_sequence)

        # Evaluate each cycle AFTER cycle-1 against baseline sequence template
        for cyc_id, cyc_transfers in cycles_map.items():
            if cyc_id == "cycle-1":
                continue  # Cycle 1 is the canonical learning baseline, never an outlier

            # 1. Check for Wrong Destination or Unexpected Source per step position in cycle
            for pos, xfer in enumerate(cyc_transfers):
                src = xfer.source_entity
                obs_dest = xfer.destination_entity.lower()
                expected_dest = global_mapping_memory.get_expected_destination(src)

                positional_dest = None
                positional_src = None
                if pos < baseline_len:
                    positional_src = self.baseline_sequence[pos][0]
                    positional_dest = self.baseline_sequence[pos][1]

                target_expected = expected_dest or positional_dest

                src_clean = format_clean_entity_label("", src)
                exp_clean = format_clean_entity_label("", target_expected or "")
                obs_clean = format_clean_entity_label("", obs_dest)

                # Wrong Destination check
                if target_expected and target_expected.lower() != obs_dest:
                    logger.info(
                        f"🚨 [DEVIATION DETECTED] Wrong Destination Field | Cycle={cyc_id} Step={pos+1} | Source='{src}' | "
                        f"Expected='{target_expected}' != Observed='{obs_dest}'"
                    )
                    deviations.append({
                        "id": f"dev-wrong-dest-{cyc_id}-{pos+1}",
                        "cycle_id": cyc_id,
                        "source_entity": src,
                        "expected_destination": target_expected,
                        "observed_destination": obs_dest,
                        "label": f"Field ({src_clean}) pasted into Field ({obs_clean}) in {cyc_id}",
                        "reason": f"Expected destination '{exp_clean}' but observed '{obs_clean}'",
                        "selector": obs_clean,
                        "transfer_id": xfer.transfer_id,
                        "group": "Wrong Field Target"
                    })
                # Positional Source Mismatch check (e.g. Field C pasted where Field B expected)
                elif positional_src and positional_src.lower() != src.lower():
                    exp_src_clean = format_clean_entity_label("", positional_src)
                    logger.info(
                        f"🚨 [DEVIATION DETECTED] Positional Step Mismatch | Cycle={cyc_id} Step={pos+1} | "
                        f"Expected Source='{positional_src}' != Observed='{src}'"
                    )
                    deviations.append({
                        "id": f"dev-mismatched-step-{cyc_id}-{pos+1}",
                        "cycle_id": cyc_id,
                        "source_entity": src,
                        "expected_destination": positional_dest or "",
                        "observed_destination": obs_dest,
                        "label": f"Unexpected Step Order in {cyc_id}: Field ({src_clean}) where Field ({exp_src_clean}) expected",
                        "reason": f"Expected step {pos+1} to be '{exp_src_clean}', observed '{src_clean}'",
                        "selector": obs_clean,
                        "transfer_id": xfer.transfer_id,
                        "group": "Sequence Mismatch"
                    })

            # 2. Check for Missing Steps in shorter cycle relative to baseline ONLY for COMPLETED cycles (not the active in-progress cycle) and if no deviation was already flagged
            cyc_keys = list(cycles_map.keys())
            is_active_in_progress_cycle = (cyc_id == cyc_keys[-1])

            if not is_active_in_progress_cycle and len(cyc_transfers) < baseline_len and not has_cycle_deviation:
                cyc_src_set = {x.source_entity.lower() for x in cyc_transfers}
                for exp_src, exp_dest in self.baseline_sequence:
                    if exp_src.lower() not in cyc_src_set:
                        src_clean = format_clean_entity_label("", exp_src)
                        dest_clean = format_clean_entity_label("", exp_dest)
                        logger.info(
                            f"🚨 [DEVIATION DETECTED] Missing Step in {cyc_id} | Expected='{exp_src} -> {exp_dest}'"
                        )
                        deviations.append({
                            "id": f"dev-missing-{cyc_id}-{len(deviations)+1}",
                            "cycle_id": cyc_id,
                            "source_entity": exp_src,
                            "expected_destination": exp_dest,
                            "observed_destination": "missing",
                            "label": f"Missing Step in {cyc_id}: Skipped Field ({src_clean}) → Field ({dest_clean})",
                            "reason": f"Workflow baseline expected step '{src_clean} → {dest_clean}'",
                            "selector": dest_clean,
                            "transfer_id": f"xfer-missing-{cyc_id}",
                            "group": "Omitted Action"
                        })

        active_deviations = []
        for d in deviations:
            sel = str(d.get("selector", "")).lower().strip()
            obs = str(d.get("observed_destination", "")).lower().strip()
            dev_id = str(d.get("id", "")).lower().strip()
            tid = str(d.get("transfer_id", "")).lower().strip()

            is_res = any(
                r == dev_id or r == tid or (r and r == sel and len(r) > 5)
                for r in self.resolved_selectors if r
            )
            if not is_res:
                active_deviations.append(d)

        logger.info(f"[STAGE 4: DEVIATION_DETECTOR] Evaluated {len(valid_transfers)} transfers -> Flagged {len(active_deviations)} active mistakes ({len(deviations) - len(active_deviations)} resolved).")
        return active_deviations


global_deviation_detector = DeviationDetector()
