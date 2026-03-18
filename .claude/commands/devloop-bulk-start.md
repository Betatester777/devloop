Start a DevLoop workflow with a pre-structured request (name, summary, requirements, architecture).

The user is providing a pre-structured request with some or all of the following fields:
- **name**: project or feature name
- **summary**: one-line description
- **requirements**: structured list with sub-items (these map to feature bundles and acceptance criteria)
- **architecture**: tech stack, platforms, libraries

## Instructions

1. Check whether `docs/STATE.md` already exists. If it does, warn the user and ask whether to continue or start fresh.
2. Read `BASE_CONFIG.md` for constraints.
3. Capture the structured input verbatim into `docs/input/user_request.md` (copy from `.github/templates/input/user_request.md`).
4. Set `docs/STATE.md` to phase `Init`.
5. Transition to Requirements and invoke the product manager sub-agent (`.claude/agents/product-manager.md`).

The product manager should recognize this as structured input and use it to accelerate PRD creation:
- Each top-level requirement maps to a **feature bundle**.
- Sub-items under each requirement map to **acceptance criteria**.
- The architecture section informs technical constraints and should be cross-checked against `BASE_CONFIG.md`.

The product manager still validates, fills gaps, and asks the user to confirm scope — but should not discard the structure the user provided.

After the product manager returns, present accept/improve options as numbered text:
- 1. Accept — PRD is ready for architecture
- 2. Improve — I have feedback

Follow the orchestrator rules in `.claude/agents/devloop-orchestrator.md` for all phase transitions and quality gates.

The user's structured input follows (if provided after the command):
