Start a DevLoop workflow with a pre-structured request and YOLO mode enabled (no user approval, auto-release).

The user is providing a pre-structured request with some or all of the following fields:
- **name**: project or feature name
- **summary**: one-line description
- **requirements**: structured list with sub-items (these map to feature bundles and acceptance criteria)
- **architecture**: tech stack, platforms, libraries

## Instructions

1. Check whether `docs/STATE.md` already exists. If it does, warn the user and ask whether to continue or start fresh.
2. Read `BASE_CONFIG.md` for constraints.
3. Capture the structured input verbatim into `docs/input/user_request.md` (copy from `.github/templates/input/user_request.md`).
4. Set `docs/STATE.md` to phase `Init` with **YOLO Mode: Enabled**.
5. Transition to Requirements and invoke the product manager sub-agent (`.claude/agents/product-manager.md`).
6. After PRD is complete, continue the full workflow automatically — Architecture, Increment cycle (Planning → Implementation → Testing), Review (auto-approve), and Release (mandatory) — without stopping for user approval.

The product manager should recognize this as structured input:
- Each top-level requirement maps to a **feature bundle**.
- Sub-items map to **acceptance criteria**.
- The architecture section informs technical constraints.

YOLO mode rules apply: reviews auto-approve, versions auto-increment, releases are mandatory every cycle. Quality gates (Ready, Pass) are still enforced.

Follow the orchestrator rules in `.claude/agents/devloop-orchestrator.md` for all phase transitions.

The user's structured input follows (if provided after the command):
