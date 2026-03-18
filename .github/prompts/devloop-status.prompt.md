---
description: "Show the current DevLoop workflow state — phase, bundle, progress, and next step."
agent: "devloop-orchestrator"
---

# Workflow status

The user wants a status overview.

1. Read `docs/STATE.md` for the current phase and active bundle.
2. If `docs/STATE.md` does not exist, infer state from which workflow documents are present.
3. Report the following in a concise summary:
   - **Phase**: current workflow phase.
   - **Active bundle**: name and number (if in Increment cycle or later).
   - **Increment cycle iteration**: current repeat count out of the max allowed.
   - **Last completed gate**: which quality gate was last passed.
   - **Next step**: what will happen when the workflow continues.
   - **Documents**: which `docs/` files exist and their last-modified status.
4. Do not take any workflow action — this is read-only.
