---
name: feature-bundle-planning
description: "Create and update docs/PLN.md with tasks, dependencies, DoR/DoD, and validation commands."
---

# feature-bundle-planning

## Purpose

Break an architecture into one active feature bundle with implementable tasks, explicit dependencies, definitions of ready and done, and validation commands.

## Trigger

Invoked by the task planner during the Increment cycle setup, or when replanning is needed.

## Inputs

- `docs/ARC.md`
- `docs/PRD.md` (for acceptance criteria)

## Outputs

- `docs/PLN.md`

## Procedure

### Creating a new plan

1. Copy `templates/PLN.md` to `docs/PLN.md` (or overwrite the Active Bundle section if the file exists from a previous bundle).
2. Read `docs/ARC.md` for modules, interfaces, and technical decisions.
3. Read `docs/PRD.md` for the feature bundle list and acceptance criteria.
4. Select the next pending bundle (or the one confirmed by the user).

#### Active Bundle
Name the bundle and write a one-sentence description.

#### Tasks
Break the bundle into 3–8 small tasks. Each task should be completable by the developer in one focused session. Use the table format:

```markdown
| # | Task | Traces | Dependencies | Status |
|---|---|---|---|---|
| 1 | Create AST node types for headings, lists, paragraphs | AC-1.1 | None | Pending |
| 2 | Implement markdown tokenizer | AC-1.1, AC-1.2 | None | Pending |
| 3 | Implement parser (tokens → AST) | AC-1.1, AC-1.2 | 1, 2 | Pending |
| 4 | Add unit tests for parser | AC-1.1, AC-1.2 | 3 | Pending |
```

Rules for tasks:
- Each task has a clear, observable output (a file, a test, a passing command).
- **Traces** column lists the AC-N.M IDs the task satisfies. Every AC ID for the active bundle must appear in at least one task.
- Dependencies reference task numbers, not vague descriptions.
- Status is one of: `Pending`, `In Progress`, `Done`, `Blocked`.

#### Dependencies
List external dependencies (libraries, services, data) that must be available before work starts. If none, write "None".

#### Definition of Ready
Conditions that must hold before the developer starts:
- Architecture section covering this bundle exists in `docs/ARC.md`.
- Acceptance criteria for this bundle exist in `docs/PRD.md`.
- All external dependencies are available.

#### Definition of Done
Conditions that must hold before the bundle is considered complete:
- All tasks are marked `Done`.
- All acceptance criteria have passing tests.
- `pytest` passes with no failures.
- `ruff` and `shellcheck` report no errors.
- `docs/PLN.md` task statuses are up to date.

#### Validation Commands
List the exact commands to verify the bundle:

```markdown
- `pytest tests/ -v` — runs all tests
- `ruff check .` — lint Python
- `shellcheck scripts/*.sh` — lint Bash (if applicable)
```

### Updating a plan (rework or re-plan)

1. Read the existing `docs/PLN.md`.
2. If tasks need splitting, add new rows and update dependency references.
3. If a task is blocked, set its status to `Blocked` and add the blocker to the Dependencies section.
4. If scope changed (user feedback from review), update the Active Bundle description and adjust tasks.
5. Never delete completed tasks — keep them as `Done` for traceability.

## Validation checklist

Before handoff, verify:
- [ ] Active Bundle has a name, REQ-N ID, and description.
- [ ] At least 3 tasks are defined.
- [ ] Every task has a Traces column with at least one AC-N.M ID.
- [ ] Every AC ID for the active bundle appears in at least one task's Traces column.
- [ ] Every task has dependencies listed (or "None").
- [ ] Every task has a clear status.
- [ ] Definition of Ready conditions are met.
- [ ] Validation Commands are executable (not placeholder text).
