Start a new DevLoop workflow — capture user request, set up constraints, and begin the first phase.

1. Check whether `docs/STATE.md` already exists. If it does, warn the user that a workflow is already in progress and ask whether to continue it instead or start fresh (which requires cleanup first).
2. If no workflow is active, read `BASE_CONFIG.md` for constraints and stack.
3. Use the AskUserQuestion tool to capture the user's request into `docs/input/user_request.md` (copy from `.github/templates/input/user_request.md`) — ask four questions:
   - **Project name** (freeform)
   - **Project summary** (freeform — one-sentence description)
   - **Requirements** (freeform — structured list or prose; top-level items become bundles, sub-items become acceptance criteria)
   - **Architecture / stack** (freeform — languages, frameworks, platforms)
4. Set `docs/STATE.md` to phase `Init`.
5. Proceed through the Init phase: validate that constraints are clear, then transition to Requirements.
6. Invoke the product manager sub-agent (`.claude/agents/product-manager.md`) to produce `docs/PRD.md` from the user's request.
7. After the product manager returns, present accept/improve options as numbered text:
   - 1. Accept — PRD is ready for architecture
   - 2. Improve — I have feedback

Follow the orchestrator rules in `.claude/agents/devloop-orchestrator.md` for all phase transitions and quality gates.
