---
description: "Start a new DevLoop workflow — capture user request, set up constraints, and begin the first phase."
mode: "agent"
agent: "devloop-orchestrator"
---

# Start new workflow

The user wants to start the DevLoop workflow with a new request.

1. Check whether `docs/STATE.md` already exists. If it does, warn the user that a workflow is already in progress and ask whether to continue it instead or start fresh (which requires cleanup first).
2. If no workflow is active, read `BASE_CONFIG.md` for constraints and stack.
3. Capture the user's request into `docs/input/user_request.md` (copy from `.github/templates/input/user_request.md`).
4. Set `docs/STATE.md` to phase `Init`.
5. Proceed through the Init phase: validate that constraints are clear, then transition to Requirements.
6. Invoke the product manager to produce `docs/PRD.md` from the user's request.

The user's request follows. If no request is provided below, ask for one.
