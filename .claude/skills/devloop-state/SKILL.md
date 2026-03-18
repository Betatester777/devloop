---
name: devloop-state
description: "Read and write DevLoop workflow state from document files."
---

# devloop-state

## Purpose

Provide a consistent way to read, update, and validate the workflow state stored in `docs/STATE.md` and related workflow documents.

## Trigger

Invoked by the orchestrator at the start of every phase transition and at session boundaries.

## Inputs

- `docs/STATE.md`
- All workflow documents (to infer state when `STATE.md` is absent or stale)

## Outputs

- Updated `docs/STATE.md`

## Procedure

### Reading state

1. Check if `docs/STATE.md` exists.
2. If it exists, read the `Current Phase`, `Increment Sub-phase`, `YOLO Mode`, `Active Bundle`, `Repeat Count`, and `Blockers` fields.
3. If it does not exist or any field is empty, **infer state** from which workflow documents are present:
   - Only `BASE_CONFIG.md` exists → phase is `Init`
   - `docs/PRD.md` exists but not `docs/ARC.md` → phase is `Requirements`
   - `docs/ARC.md` exists but not `docs/PLN.md` → phase is `Architecture`
   - `docs/PLN.md` exists with no tasks started → phase is `Increment cycle`, sub-phase `Planning`
   - `docs/PLN.md` exists with incomplete tasks → phase is `Increment cycle`, sub-phase `Implementation`
   - `docs/PLN.md` has all tasks done but no `docs/TST.md` or TST shows failures → phase is `Increment cycle`, sub-phase `Testing`
   - `docs/PLN.md` has all tasks done + `docs/TST.md` shows all pass → phase is `Review`
   - `docs/REV.md` exists with approval → phase is `Release`
4. Validate that the inferred phase is consistent with the transition rules in `BASE_CONFIG.md`.
5. If inconsistent, flag as a blocker and escalate.

### Writing state

1. Copy `templates/STATE.md` to `docs/STATE.md` if it does not exist.
2. Fill in all fields:
   - **Current Phase**: one of `Init`, `Requirements`, `Architecture`, `Increment cycle`, `Review`, `Release`
   - **Increment Sub-phase**: when Current Phase is `Increment cycle`, one of `Planning`, `Implementation`, `Testing`. Otherwise `N/A`.
   - **YOLO Mode**: `Enabled` or `Disabled` (default `Disabled`). When Enabled, reviews auto-approve and releases run after every cycle.
   - **Active Bundle**: name from `docs/PLN.md` or `None`
   - **Repeat Count**: number of implement-test iterations for the current bundle (starts at 0). Reset to 0 when the Pass gate succeeds or a new bundle starts.
   - **Last Transition**: `<from> → <to>, <YYYY-MM-DD>`
   - **Blockers**: list of active blockers, or `None`
   - **Transient Artifacts**: list of temp files/dirs created during this session
3. Write the file atomically — never leave a half-written `STATE.md`.

### Validation rules

- Current Phase must be one of the known phases.
- Increment Sub-phase must be one of `Planning`, `Implementation`, `Testing` when in Increment cycle, or `N/A` otherwise.
- Active Bundle must match the bundle name in `docs/PLN.md` (if that file exists).
- Repeat Count must be a non-negative integer, not exceeding the max repeats guardrail in `BASE_CONFIG.md`.
- If Blockers are listed, the orchestrator must not transition to the next phase.
- Last Transition date must not be in the future.

## Example

```markdown
# Workflow State

## Current Phase
Increment cycle

## Increment Sub-phase
Implementation

## YOLO Mode
Enabled

## Active Bundle
Markdown-to-HTML conversion

## Repeat Count
1

## Last Transition
Architecture → Increment cycle, 2026-03-16

## Blockers
None

## Transient Artifacts
- /tmp/devloop_build_cache/
```
