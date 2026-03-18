# Base Configuration — DevLoop Orchestrator

## Stack

| Category | Value |
|---|---|
| Languages | Python 3.12+, Bash |
| UI framework | pygame |
| Test framework | pytest |
| Linters | ruff (Python), shellcheck (Bash) |
| Target platforms | Linux, Windows |
| Build | Project-specific (to be defined when code exists) |

## Project layout

| Directory | Content |
|---|---|
| `src/` | All application source code |
| `tests/` | All test code (mirrors `src/` structure) |
| `src/assets/` | Game assets: images, sounds, fonts, and manifests |
| `docs/` | Workflow documents (created by agents from templates) |
| `releases/` | Versioned release archives (`releases/v<major.minor.sub>/`) |
| `.github/` | Agent definitions, skills, prompts, and templates |

## Quality gates

| Gate | Condition |
|---|---|
| **Ready** | Bundle has scope, acceptance criteria, dependencies, and validation commands |
| **Pass** | Build succeeds, tests pass, required lint checks pass |
| **Accept** | User approves the runnable increment |
| **Release** | Release notes, traceability table, and packaged zip in `releases/v<major.minor.sub>/` are complete. *(Optional in normal mode, mandatory in YOLO mode.)* |

## Approval rules

- In normal mode, user approval is required after the Review phase before Release.
- In **YOLO mode**, review auto-approves and release runs automatically after every cycle.
- Rework input is requested when review is rejected (normal mode), requirements are ambiguous, or a blocker cannot be resolved automatically.

## Guardrails

| Guardrail | Value |
|---|---|
| **Increment cycle max repeats** | 3 (configurable) — after this many plan → implement → test iterations without passing the Pass gate, the orchestrator must stop and escalate to the user. Adjust this value per project as needed. |

## YOLO Mode

When **YOLO mode** is enabled (`## YOLO Mode` set to `Enabled` in `docs/STATE.md`):

- The **Review phase auto-approves**: the review presenter still assembles `docs/REV.md` but skips user confirmation and automatically approves.
- The **Release phase runs after every cycle**: every approved bundle gets a release — no bundles are skipped.
- **Version auto-increments**: the release manager bumps the minor version automatically (e.g. `0.1.0` → `0.2.0` → `0.3.0`). No user prompt for version number.
- The **Accept gate** is satisfied without user interaction.
- All other quality gates (Ready, Pass) still apply — YOLO mode skips human approval, not automated checks.

To enable: set `## YOLO Mode` to `Enabled` in `docs/STATE.md`.  
To disable: set it to `Disabled` (default).

## Forbidden actions

- `git push --force` on any shared branch.
- Direct commits to the main branch without review.
- Deleting accepted documents or release history without explicit user confirmation.
- Bypassing quality gates or skipping phases.
- Running destructive commands (`rm -rf`, `DROP TABLE`, etc.) without user confirmation.

## Transitions

| From | To | When |
|---|---|---|
| Init | Requirements | Constraints are clear |
| Requirements | Architecture | PRD is complete |
| Architecture | Increment cycle | Design is stable enough |
| Increment cycle | Review | Acceptance criteria pass |
| Review | Release | User approves and requests release (normal), or auto-approved (YOLO) |
| Review | Increment cycle | User approves and skips release (normal mode only) |
| Any phase | Rework | Blockers, failed tests, or missing information |

## Cleanup

Cleanup is not a workflow phase — it runs as a VS Code task (manually or automatically at session boundaries).

- **Persistent state**: documents, decisions, accepted increments, release history — kept across resets.
- **Assets**: `src/assets/` is always preserved — never deleted during cleanup or full reset.
- **Transient state**: temp files, scratch outputs, cached logs, local session artifacts — removed on cleanup.
- Cleanup removes transient state but keeps persistent state unless the user explicitly requests a full reset.
- Full reset removes workflow documents under `docs/` (except `docs/input/` and `docs/OVERVIEW.*`) and resets `docs/STATE.md`, but never touches `src/assets/` or `releases/`.
