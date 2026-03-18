# Agents — DevLoop Orchestrator

This file defines the agent roster, their roles, and document ownership.

## Agent roster

| Agent | Role | Primary output |
|---|---|---|
| `orchestrator` | Reads state, selects the next valid phase, invokes sub-agents, validates output docs, enforces quality gates | `docs/STATE.md` |
| `product-manager` | Converts raw user input into structured product requirements with REQ/AC IDs | `docs/PRD.md` |
| `software-architect` | Defines modules, interfaces, technical decisions, and risks | `docs/ARC.md` |
| `task-planner` | Plans one active feature bundle with tasks, dependencies, and validation commands | `docs/PLN.md` |
| `software-developer` | Implements the active bundle — code, unit tests, inline docs | Code and tests |
| `software-tester` | Creates and executes tests from requirements and acceptance criteria | `docs/TST.md` |
| `review-presenter` | Prepares a runnable review package and presents summary to orchestrator | `docs/REV.md` |
| `release-manager` | Creates release notes, traceability table, and packaged zip archive (`src/`, release notes, change log) | `docs/REL.md`, `releases/` |

## Agent definitions

Each agent has a detailed definition in `.claude/agents/<name>.md`.

## Phase banners

Every agent prints a phase banner as the first line of every response:

| Phase | Banner |
|---|---|
| Init | `# 🚀 Init` |
| Requirements | `# 📋 Requirements` |
| Architecture | `# 🏗️ Architecture` |
| Planning | `# 📐 Planning — Bundle N/T: <name>` |
| Implementation | `# 💻 Implementation — Bundle N/T: <name> · Cycle R/M` |
| Testing | `# 🧪 Testing — Bundle N/T: <name> · Cycle R/M` |
| Review | `# 🔍 Review — Bundle N/T: <name>` |
| Release | `# 📦 Release` |

**N/T** = bundle position / total bundles. **R/M** = iteration / max repeats.

## User interaction patterns

All user-facing prompts are handled by the **orchestrator**, not by sub-agents. Sub-agents return their deliverables and the orchestrator presents accept/improve/approval options.

| Agent | Normal mode | YOLO mode |
|---|---|---|
| Product Manager | Orchestrator asks accept/improve after PRD | Auto-accept |
| Software Architect | Orchestrator asks accept/improve after design | Auto-accept |
| Task Planner | Orchestrator asks bundle selection (if ambiguous) | Auto-select next |
| Software Developer | No prompts — auto-handoff | — |
| Software Tester | No prompts — Pass gate is automated | — |
| Review Presenter | Orchestrator asks: Approve & Next Cycle / Approve & Release / Needs Rework | Auto "Approve & Release" |
| Release Manager | Orchestrator asks version, audience, migration | Auto-increment minor |

## Skills

Skills are reusable procedures that agents reference from their definition files. Each skill lives in `.claude/skills/<name>/SKILL.md`.

| Skill | Used by | Purpose |
|---|---|---|
| `devloop-state` | `orchestrator` | Read and write workflow state from document files |
| `prd-authoring` | `product-manager` | Author and update `docs/PRD.md` with feature bundles and acceptance criteria using REQ-N / AC-N.M IDs |
| `feature-bundle-planning` | `task-planner` | Create and update `docs/PLN.md` with tasks, dependencies, and validation commands; trace tasks to AC IDs |
| `requirements-based-testing` | `software-tester` | Design tests from requirements and acceptance criteria; trace tests to AC IDs |
| `review-packaging` | `review-presenter` | Assemble a review package with change summary, AC traceability, risks, test results, and approval questions |
| `release-notes` | `release-manager` | Generate release notes with REQ-N references and traceability table |

The `software-architect` and `software-developer` agents do not use skills — their procedures are self-contained in their agent definitions.

## Orchestrator authority

- The orchestrator is the only agent that selects phases and invokes sub-agents.
- Sub-agents must not self-transition to another phase.
- The orchestrator validates output docs before allowing a phase transition.
- If a quality gate fails, the orchestrator returns work to the same phase.
- If constraints conflict or acceptance is unclear, the orchestrator escalates to the user.

## Document ownership

Each document has exactly one owning agent. Only the owner creates or makes structural changes to its document. Other agents may read any document but must not modify documents they do not own.

**Exception**: The `software-developer` may update task statuses (`Pending` → `Done` / `Blocked`) in `docs/PLN.md`. This is a status-field update, not a structural change.

| Document | Owner |
|---|---|
| `docs/input/user_request.md` | `orchestrator` (initial capture) |
| `BASE_CONFIG.md` | `orchestrator` |
| `docs/PRD.md` | `product-manager` |
| `docs/ARC.md` | `software-architect` |
| `docs/PLN.md` | `task-planner` |
| `docs/TST.md` | `software-tester` |
| `docs/REV.md` | `review-presenter` |
| `docs/REL.md` | `release-manager` |
| `docs/STATE.md` | `orchestrator` |
