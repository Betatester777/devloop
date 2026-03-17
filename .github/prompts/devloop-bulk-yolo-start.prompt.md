---
description: "Start a Devloop workflow with a pre-structured request and YOLO mode enabled (no user approval, auto-release)."
mode: "agent"
agent: "devloop-orchestrator"
---

# Start workflow from structured input (YOLO)

The user is providing a pre-structured request with some or all of the following fields:

- **name**: project or feature name
- **summary**: one-line description
- **requirements**: structured list with sub-items (these map to feature bundles and acceptance criteria)
- **architecture**: tech stack, platforms, libraries

## Instructions

1. Check whether `docs/STATE.md` already exists. If it does, warn the user and ask whether to continue or start fresh.
2. Read `BASE_CONFIG.md` for constraints.
3. Capture the structured input verbatim into `docs/input/user_request.md`.
4. Set `docs/STATE.md` to phase `Init` with **YOLO Mode: Enabled**.
5. Transition to Requirements and invoke the product manager.
6. After PRD is complete, continue the full workflow automatically — Architecture, Increment cycle (Planning → Implementation → Testing), Review (auto-approve), and Release (mandatory) — without stopping for user approval.

The product manager should recognize this as structured input and use it to accelerate PRD creation:
- Each top-level requirement maps to a **feature bundle**.
- Sub-items under each requirement map to **acceptance criteria**.
- The architecture section informs technical constraints and should be cross-checked against `BASE_CONFIG.md`.

The product manager still validates, fills gaps, and asks the user to confirm scope — but should not discard the structure the user provided.

YOLO mode rules apply: reviews auto-approve, versions auto-increment, releases are mandatory every cycle. Quality gates (Ready, Pass) are still enforced.

The user's structured input follows:
