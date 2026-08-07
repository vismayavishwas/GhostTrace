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

    def resolve_all_current(self, current_deviations: Optional[List[Dict[str, Any]]] = None):
        """Marks currently active deviations as resolved."""
        if current_deviations:
            for d in current_deviations:
                sel = d.get("selector", "")
                obs = d.get("observed_destination", "")
                dev_id = d.get("id", "")
                if sel: self.resolved_selectors.add(str(sel).lower().strip())
                if obs: self.resolved_selectors.add(str(obs).lower().strip())
                if dev_id: self.resolved_selectors.add(str(dev_id).lower().strip())


    def set_sequence_template(self, transfers: List[SemanticTransfer]):
        """Sets the established baseline sequence template (source_entity, destination_entity)."""
        self.baseline_sequence = [(x.source_entity, x.destination_entity) for x in transfers if not x.is_immediate_correction]

    def detect_deviations(self, transfers: List[SemanticTransfer]) -> List[Dict[str, Any]]:
        """Detects deviations by comparing expected stable mappings & baseline sequences against observed transfers."""
        deviations: List[Dict[str, Any]] = []
        valid_transfers = [x for x in transfers if not x.is_immediate_correction]

        if not valid_transfers:
            return deviations

        # Auto-establish baseline sequence if not explicitly set and transfers exist
        if not self.baseline_sequence and len(valid_transfers) >= 2:
            self.set_sequence_template(valid_transfers)

        # 1. Detect Wrong Destination Fields (Mapping Memory or Positional Baseline)
        for idx, xfer in enumerate(valid_transfers):
            src = xfer.source_entity
            expected_dest = global_mapping_memory.get_expected_destination(src)
            
            positional_dest = None
            if self.baseline_sequence and idx < len(self.baseline_sequence):
                positional_dest = self.baseline_sequence[idx][1]

            target_expected = expected_dest or positional_dest
            observed_dest = xfer.destination_entity.lower()

            src_clean = format_clean_entity_label("", src)
            exp_clean = format_clean_entity_label("", target_expected or "")
            obs_clean = format_clean_entity_label("", observed_dest)

            if target_expected and target_expected.lower() != observed_dest:
                logger.info(
                    f"🚨 [DEVIATION DETECTED] Wrong Destination Field | Step={idx+1} | Source='{src}' | "
                    f"Expected='{target_expected}' != Observed='{observed_dest}'"
                )
                deviations.append({
                    "id": f"dev-wrong-dest-{len(deviations)+1}",
                    "source_entity": src,
                    "expected_destination": target_expected,
                    "observed_destination": observed_dest,
                    "label": f"Field ({src_clean}) pasted into Field ({obs_clean})",
                    "reason": f"Expected destination '{exp_clean}' but observed '{obs_clean}'",
                    "selector": obs_clean,
                    "transfer_id": xfer.transfer_id,
                    "group": "Wrong Field Target"
                })

        # 2. Detect Reordered Steps against baseline sequence
        if self.baseline_sequence and len(valid_transfers) >= 2:
            observed_srcs = [x.source_entity for x in valid_transfers]
            expected_src_order = [s for s, _ in self.baseline_sequence if s in observed_srcs]
            if observed_srcs != expected_src_order and len(observed_srcs) == len(expected_src_order):
                for idx, (obs_s, exp_s) in enumerate(zip(observed_srcs, expected_src_order)):
                    if obs_s != exp_s:
                        obs_clean = format_clean_entity_label("", obs_s)
                        exp_clean = format_clean_entity_label("", exp_s)
                        deviations.append({
                            "id": f"dev-reordered-{len(deviations)+1}",
                            "source_entity": obs_s,
                            "expected_destination": "reordered",
                            "observed_destination": obs_s,
                            "label": f"Reordered Step: Field ({obs_clean}) pasted out of baseline sequence",
                            "reason": f"Expected Field ({exp_clean}) before Field ({obs_clean})",
                            "selector": obs_clean,
                            "transfer_id": valid_transfers[idx].transfer_id,
                            "group": "Sequence Reordering"
                        })
                        break

        # 3. Detect Missing Steps against baseline sequence
        if self.baseline_sequence and len(valid_transfers) < len(self.baseline_sequence):
            observed_src_set = {x.source_entity for x in valid_transfers}
            for exp_src, exp_dest in self.baseline_sequence:
                if exp_src not in observed_src_set:
                    src_clean = format_clean_entity_label("", exp_src)
                    dest_clean = format_clean_entity_label("", exp_dest)
                    deviations.append({
                        "id": f"dev-missing-{len(deviations)+1}",
                        "source_entity": exp_src,
                        "expected_destination": exp_dest,
                        "observed_destination": "missing",
                        "label": f"Missing Step: Skipped Field ({src_clean}) → Field ({dest_clean})",
                        "reason": f"Workflow baseline expected step '{src_clean} → {dest_clean}'",
                        "selector": dest_clean,
                        "transfer_id": "missing-step",
                        "group": "Omitted Action"
                    })

        active_deviations = []
        for d in deviations:
            sel = str(d.get("selector", "")).lower().strip()
            obs = str(d.get("observed_destination", "")).lower().strip()
            dev_id = str(d.get("id", "")).lower().strip()
            
            is_res = any(
                r in sel or r in obs or r in dev_id or sel in r or obs in r
                for r in self.resolved_selectors if r
            )
            if not is_res:
                active_deviations.append(d)

        logger.info(f"[STAGE 4: DEVIATION_DETECTOR] Evaluated {len(valid_transfers)} transfers -> Flagged {len(active_deviations)} active mistakes ({len(deviations) - len(active_deviations)} resolved).")
        return active_deviations


global_deviation_detector = DeviationDetector()
