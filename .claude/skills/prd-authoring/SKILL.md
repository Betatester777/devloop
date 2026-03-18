---
name: prd-authoring
description: "Author and update docs/PRD.md with feature bundles and acceptance criteria."
---

# prd-authoring

## Purpose

Structure raw user input and constraints into a well-formed Product Requirements Document with clear feature bundles, acceptance criteria, and scope boundaries.

## Trigger

Invoked by the product manager during the Requirements phase.

## Inputs

- `docs/input/user_request.md`
- `BASE_CONFIG.md`

## Outputs

- `docs/PRD.md`

## Procedure

### Creating a new PRD

1. Copy `templates/PRD.md` to `docs/PRD.md`.
2. Read `docs/input/user_request.md` for the raw request.
3. Read `BASE_CONFIG.md` for stack constraints, forbidden actions, and quality gates.
4. **Detect structured input**: if the request contains structured fields (name, summary, requirements with sub-items, architecture), use them as a head start:
   - Set the Overview from the name and summary.
   - Map each top-level requirement to a feature bundle.
   - Map sub-items to acceptance criteria (convert to Given/When/Then).
   - Cross-check the architecture field against `BASE_CONFIG.md` stack constraints.
   - Do not discard the user's structure — refine it, don't replace it.
5. Fill in each section:

#### Overview
Write 2–3 sentences describing the product or feature set in plain language.

#### Scope
List what this work includes. Be specific — name the capabilities, not the implementation.

#### Feature Bundles
Break the scope into small, independently deliverable bundles. Each bundle should be completable in one Increment cycle. Assign each bundle a stable **REQ-N** ID (sequential, never reused). Use the table format:

```markdown
| ID | Bundle | Description | Status |
|---|---|---|---|
| REQ-1 | Markdown parsing | Parse standard markdown to an AST | Pending |
| REQ-2 | HTML rendering | Convert AST to valid HTML5 output | Pending |
| REQ-3 | Syntax highlighting | Detect fenced code blocks and apply Pygments | Pending |
```

ID rules:
- IDs are sequential: REQ-1, REQ-2, REQ-3, …
- Once assigned, an ID is **never reused or renumbered**.
- If a bundle is dropped, mark it `(Retired)` — do not delete the row.

#### Acceptance Criteria
For each bundle, write measurable criteria using the pattern:
- **Given** [context], **when** [action], **then** [expected result].

Every criterion must be testable — no vague words like "fast", "good", or "user-friendly" without a measurable threshold.

Assign each criterion a stable **AC-N.M** ID where N is the bundle number and M is sequential within the bundle.

Example:
```markdown
### REQ-1: Markdown parsing
| ID | Criterion | Testable? |
|---|---|---|
| AC-1.1 | Given a markdown file with headings (H1–H6), when parsed, then each heading produces the correct `<h1>`–`<h6>` tag. | Yes |
| AC-1.2 | Given a file with nested bullet lists, when parsed, then the output preserves nesting depth up to 4 levels. | Yes |
```

AC ID rules:
- IDs are sequential within each REQ: AC-1.1, AC-1.2, AC-2.1, …
- Once assigned, an AC ID is **never reused or renumbered**.
- If a criterion is dropped, mark it `(Retired)` — do not delete the row.

#### Out of Scope
Explicitly list what this work does **not** include. This prevents scope creep.

#### Open Questions
List anything ambiguous that needs user input before proceeding. Use the format:
- **Q1**: [question] — Options: [A / B / needs discussion]

### Updating an existing PRD

1. Read the existing `docs/PRD.md`.
2. Identify which sections need changes (new bundles, revised criteria, resolved questions).
3. Update only the affected sections. Do not rewrite unchanged content.
4. If a bundle status changes, update the Feature Bundles table.
5. Move resolved questions from Open Questions to the relevant section.

## Validation checklist

Before handoff, verify:
- [ ] At least one feature bundle is defined with a unique REQ-N ID.
- [ ] Every bundle has at least two acceptance criteria, each with a unique AC-N.M ID.
- [ ] Every acceptance criterion is testable (Given/When/Then or equivalent).
- [ ] No ID has been reused or renumbered.
- [ ] Out of Scope section is not empty.
- [ ] Open Questions are either resolved or explicitly flagged for the user.
