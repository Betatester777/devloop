---
description: "Clean up transient workflow artifacts or perform a full reset."
agent: "devloop-orchestrator"
---

# Cleanup

The user wants to clean up workflow artifacts.

1. Ask the user to choose a cleanup scope:
   - **Transient only** (recommended) — remove temp files, scratch outputs, cached logs, and local session artifacts. Keep all workflow documents, decisions, and release history.
   - **Full reset** — archive and remove all workflow documents under `docs/` (except `docs/input/` and `docs/OVERVIEW.*`). This cannot be undone. Require explicit confirmation before proceeding.
2. Perform the selected cleanup.
3. If full reset was chosen, remove `docs/STATE.md` so the next invocation starts fresh.
4. **Never delete `src/assets/`, `releases/`, or `docs/OVERVIEW.*`** — these are always preserved regardless of cleanup scope.
5. Report what was removed and what was kept.
