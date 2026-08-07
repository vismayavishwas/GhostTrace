# GhostTrace Core System Rules

## Immutable Upstream Engine & Contract Freeze (Commit f111128)

### System Boundary Architecture
```
Telemetry
Semantic Normalizer
Transfer Builder
Mapping Memory
Learning Planner
Deviation Detector
State API
Dashboard
Analyze Button
──────────────────────────
        ↑
   LOCK HERE (f111128)

Workflow DNA
Automation Blueprint
Playwright Compiler
Ghost Replay
Self Healing
```

Everything above the line is the **Learning Engine** (Upstream).
Everything below the line is **Presentation & Automation** (Downstream).

---

### Strict Immutability & Reopening Protocol

> [!CRITICAL]
> **UPSTREAM ENGINE LOCK**: No modifications to upstream modules (above the line) are permitted unless the user **explicitly approves** reopening the upstream engine.
>
> If a downstream bug or feature appears to require upstream changes:
> 1. **STOP** immediately.
> 2. Explain to the user exactly why the upstream contract or module is insufficient (e.g. `"Workflow DNA requires additional metadata that the locked engine does not expose. Please approve reopening the upstream engine."`).
> 3. **WAIT** for explicit user approval before editing any upstream module. Do NOT silently edit upstream files.

---

### Contract Freeze by Interface

The following data models and contracts are **FROZEN & CONTRACTUAL**:
- `SemanticTransfer`
- `WorkflowCandidate`
- `WorkflowState`
- `Deviation`
- `FieldMapping`

**Rules**:
- Do NOT change field names, types, meaning, or lifecycle of contractual models.
- Downstream code (below the line) must adapt to these contracts rather than modifying them.

---

### Pre-Modification Evaluation Protocol

Before modifying ANY existing code:

1. **Determine whether the requested feature or fix can be implemented downstream.**
2. **If YES**:
   - Implement strictly downstream. **NEVER edit upstream modules.**
3. **If NO**:
   - Explain exactly why an upstream contract is insufficient and request explicit approval before editing it.
4. **Never proactively refactor working code.**
5. **Never rename working APIs.**
6. **Never change existing behavior unless explicitly requested.**
