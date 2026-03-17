---
description: "Resume the Devloop workflow from the current state."
mode: "agent"
agent: "devloop-orchestrator"
---

# Continue workflow

The user wants to resume the Devloop workflow.

1. Read `docs/STATE.md` to determine the current phase and active bundle.
2. If `docs/STATE.md` does not exist, infer the phase from which workflow documents are present.
3. If no workflow documents exist at all, tell the user there is nothing to continue and suggest using `#devloop-start` instead.
4. Pick up from the current phase and execute the next valid action according to the workflow transitions in `BASE_CONFIG.md`.
5. Brief the user on where the workflow is before proceeding: current phase, active bundle, and what happens next.
