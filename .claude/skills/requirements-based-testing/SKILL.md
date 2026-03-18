---
name: requirements-based-testing
description: "Design tests from requirements and acceptance criteria, not from source code."
---

# requirements-based-testing

## Purpose

Ensure that all tests are derived from product requirements and acceptance criteria. Source code may be inspected for integration details, but expected behavior must come from the PRD and plan.

## Trigger

Invoked by the software tester during the Increment cycle test phase.

## Inputs

- `docs/PRD.md`
- Active bundle acceptance criteria in `docs/PLN.md`
- Interface constraints from `docs/ARC.md`

## Outputs

- `docs/TST.md`
- Test scripts

## Procedure

### Designing test cases

1. Read the active bundle's acceptance criteria from `docs/PLN.md`.
2. Read the corresponding requirements from `docs/PRD.md`.
3. Read relevant interface definitions from `docs/ARC.md` for boundary conditions.
4. For each acceptance criterion, create at least one test case. Use the AC-N.M ID in the **Traces** column for traceability:

```markdown
| # | Test Case | Traces | Expected Result | Status |
|---|---|---|---|---|
| 1 | Heading tags H1–H6 rendered correctly | AC-1.1 | Input `# Title` produces `<h1>Title</h1>` | Pending |
| 2 | Nested lists preserve depth | AC-1.2 | 4-level nesting produces matching `<ul>` depth | Pending |
| 3 | Empty input produces empty output | ARC §Parser | No crash, returns empty string | Pending |
```

Rules for test cases:
- **Name the behavior**, not the ID: `test_heading_h1_renders_correctly`, not `test_AC1`.
- **Traces** column: the AC-N.M ID(s) this test verifies. Every AC ID for the active bundle must be covered by at least one test.
- **Expected result** must be specific and verifiable — include what the output looks like.
- **Derive from requirements first**: read the PRD criterion, then write the test. Do not look at source code to decide what to test.
- **Include edge cases** from `docs/ARC.md` interface constraints (empty input, malformed input, boundary values).

### Writing test code

1. Create test files named after the domain concept: `test_parser.py`, `test_renderer.py`.
2. Add traceability comments at the top using the AC-N.M IDs:
   ```python
   # Verifies: AC-1.1 — headings H1–H6 produce correct tags
   # Requirement: REQ-1 (Markdown parsing)
   ```
3. Write tests using `pytest`. Each test function should:
   - Have a descriptive name (`test_fenced_code_block_produces_pre_tag`).
   - Arrange inputs from the requirement, not from reading the implementation.
   - Assert against the expected behavior stated in the acceptance criterion.
4. Do **not** test implementation internals (private methods, internal data structures) unless they are part of a public interface defined in `docs/ARC.md`.

### When source code inspection is allowed

Source code may be read to determine:
- How to invoke the component under test (function signatures, module paths).
- What fixtures or setup are needed.
- Integration points between modules.

Source code must **never** be used to determine:
- What the correct output should be.
- Which behaviors to test.
- Pass/fail thresholds.

### Executing tests and recording results

1. Run tests: `pytest tests/ -v`
2. Record results in `docs/TST.md`:
   - Update the Test Cases table status column (`Pass`, `Fail`, `Skip`, `Error`).
   - Fill in the Results section with pass/fail counts.
   - For failures, add entries to the Defects section with reproduction steps.
   - Paste relevant command output into the Evidence section.

### Updating tests (rework)

1. If acceptance criteria changed, update or add test cases to match.
2. If a defect was fixed, re-run the affected tests and update status.
3. Never delete a test case — mark it `Superseded` if replaced, with a note pointing to the replacement.

## Validation checklist

Before handoff, verify:
- [ ] Every AC-N.M ID has at least one test case in the Traces column.
- [ ] Every test case references an AC-N.M ID (not a free-text section name).
- [ ] All tests have been executed (no `Pending` status remaining).
- [ ] The Coverage Matrix accounts for every AC ID in the active bundle.
- [ ] Defects (if any) have reproduction steps.
- [ ] Evidence section has command output or logs from the test run.
- [ ] No test derives its expected behavior from the source code.
