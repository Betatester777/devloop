---
name: review-packaging
description: "Assemble a review package with change summary, risks, test results, and approval questions."
---

# review-packaging

## Purpose

Package a completed feature bundle into a review document that enables the user to make an informed approval or rejection decision without needing to read source code.

## Trigger

Invoked by the review presenter during the Review phase.

## Inputs

- `docs/PLN.md` (completed bundle)
- `docs/TST.md` (test results)
- Runnable increment

## Outputs

- `docs/REV.md`

## Procedure

### Assembling the review package

1. Copy `.github/templates/REV.md` to `docs/REV.md` (or overwrite if from a previous bundle).
2. Read `docs/PLN.md` for the active bundle name, task list, and completion status.
3. Read `docs/TST.md` for test results, defects, and evidence.
4. Inspect the codebase for the list of changed files.

#### Increment Summary
Write 2–3 sentences: what does this increment do? What can the user now do that they couldn't before?

Example:
```markdown
This increment adds markdown-to-HTML conversion. Users can run
`python src/converter.py input.md -o output.html` to convert any
standard markdown file to valid HTML5.
```

#### Changes
List all changed files grouped by type. Include a **Traces** column with the AC-N.M IDs each file satisfies:

```markdown
### New files
| File | Description | Traces |
|---|---|---|
| `src/converter.py` | markdown parser and HTML renderer (148 lines) | AC-1.1, AC-1.2 |
| `tests/test_converter.py` | 8 test cases for parsing and rendering | AC-1.1, AC-1.2 |

### Modified files
| File | Description | Traces |
|---|---|---|
| `docs/PLN.md` | all tasks marked Done | — |
| `docs/TST.md` | test results and evidence added | — |
```

#### Test Results
Summarize from `docs/TST.md`:

```markdown
- **8 tests executed**: 8 passed, 0 failed
- **Lint**: ruff clean, shellcheck clean
- **AC coverage**: 6/6 AC IDs verified (see Coverage Matrix in `docs/TST.md`)
```

If there are failures or known defects, list them explicitly.

#### Risks
Identify risks honestly. Common categories:
- **Missing coverage**: acceptance criteria without tests.
- **Performance**: untested under load or with large inputs.
- **Compatibility**: only tested on one OS/Python version.
- **Dependencies**: new external libraries introduced.

If no risks, write "No significant risks identified for this bundle."

#### Demo Steps
Provide copy-paste-ready commands the user can run to verify the increment:

```markdown
1. Install dependencies (if any):
   pip install -r requirements.txt

2. Run the tool:
   python src/converter.py examples/sample.md -o /tmp/output.html

3. Open /tmp/output.html in a browser.

4. Verify:
   - Headings render as H1–H6 tags
   - Code blocks have syntax highlighting
   - Links are clickable
```

Every demo step must be concrete — no "verify it works as expected".

#### Approval Questions
Write 2–3 clear yes/no questions:

```markdown
1. Does the HTML output match your expectations for standard markdown?
2. Are you satisfied with the test coverage for this bundle?
3. Would you like to proceed with release, or skip to the next bundle?
```

## Validation checklist

Before handoff, verify:
- [ ] Increment Summary describes what the user gains and references the REQ-N ID.
- [ ] Changes list includes every new or modified file with AC-N.M Traces.
- [ ] Test Results match what's in `docs/TST.md`, including AC coverage count.
- [ ] Risks section is present (even if "none identified").
- [ ] Demo Steps are copy-paste-ready and tested.
- [ ] Approval Questions are stated as clear yes/no choices.
