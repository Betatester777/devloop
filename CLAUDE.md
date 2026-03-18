# DevLoop Orchestrator — Claude Code

This repository uses the **DevLoop** workflow: a document-driven, phase-gated agentic software process that produces small, testable, executable increments.

## Quick Start

Use these slash commands in Claude Code:

| Command | Description |
|---|---|
| `/devloop-start` | Start a new workflow — capture requirements and begin |
| `/devloop-bulk-start` | Start with a pre-structured request (name, summary, requirements, architecture) |
| `/devloop-bulk-yolo-start` | Start with a pre-structured request and YOLO mode (no approval, auto-release) |
| `/devloop-continue` | Resume the workflow from the current state |
| `/devloop-status` | Show current phase, bundle, progress, and next step |
| `/devloop-cleanup` | Clean up transient artifacts or perform a full reset |

## Core rule

The workflow is document-driven.
The PRD defines expected behavior.
The plan selects the active bundle.
The tester validates behavior against requirements.
The user accepts only tested, runnable increments.

## Stack

- **Languages**: Python 3.12+, Bash
- **UI framework**: pygame
- **Test**: pytest
- **Lint**: ruff (Python), shellcheck (Bash)
- **Target platforms**: Linux, Windows

## Key references

| Document | Purpose |
|---|---|
| `BASE_CONFIG.md` | Constraints, guardrails, quality bars, forbidden actions |
| `AGENTS.md` | Agent roster, roles, skills, document ownership |
| `docs/STATE.md` | Current workflow phase and active bundle (if present) |
| `.claude/agents/<name>.md` | Sub-agent definitions with prompts and quality gates |
| `.claude/skills/<name>/SKILL.md` | Reusable procedures referenced by agents |
| `.claude/commands/<name>.md` | Slash commands for common workflow operations |

## Document creation

Workflow documents (`docs/*.md`) do **not** exist at the start of a project. Templates live in `templates/`. When an agent needs to create its output document, it copies the matching template into `docs/` and fills it in. Never commit empty templates into `docs/`.

## Rules for all agents

1. **Check state first.** Read `docs/STATE.md` (if it exists) or infer the current phase from which workflow documents are present.
2. **Never skip quality gates.** Every phase transition requires its gate to pass (Ready → Pass → Accept). Release is optional in normal mode but mandatory in YOLO mode. In YOLO mode the Accept gate is auto-satisfied (no user prompt).
3. **One active bundle.** Keep exactly one active feature bundle at a time unless the user explicitly allows more.
4. **Tests come from requirements.** The software tester designs tests from `docs/PRD.md` and acceptance criteria in `docs/PLN.md`, not from source code.
5. **No forbidden actions.** See `BASE_CONFIG.md` for the list.
6. **Escalate on ambiguity.** When constraints conflict or acceptance is unclear, ask the user — do not guess.
7. **Document before transition.** Update the owning phase document before moving to the next phase.
8. **YOLO mode.** When enabled in `docs/STATE.md`, reviews auto-approve, versions auto-increment, and releases are created for every cycle. See `BASE_CONFIG.md` § YOLO Mode.
9. **Phase banners.** Print a phase banner as the first line of every response (e.g. `# 📋 Requirements`, `# 💻 Implementation — Bundle 1/8: Desktop UI & window · Cycle 1/3`). See `AGENTS.md` § Phase banners for the full format table.

## Coding standards

1. **Source code in `src/`**: all application code goes in `src/`. Tests go in `tests/`. Do not place application code in the project root.
2. **Meaningful names.** Use descriptive function, class, and variable names that reflect domain concepts. Never use requirement or acceptance-criteria IDs as names (no `req_1_parse`, `ac_2_validate`, `test_AC3`). Names should read naturally to someone unfamiliar with the workflow docs.
3. **Traceability comments.** Add a brief comment at the top of each module, class, or test file linking it to the relevant requirement and acceptance criterion IDs. Use the format `# Implements: REQ-N AC-N.M — <short description>` or `# See: ARC §<section>`. Keep these comments short — one line per reference.
4. **No ID-driven design.** Do not organize code structure (file names, directories, class hierarchies) around requirement IDs or bundle numbers. Organize by domain concept.

## Traceability ID scheme

| Artifact | ID format | Example |
|---|---|---|
| Requirement (feature bundle) | `REQ-<N>` | `REQ-1`, `REQ-2` |
| Acceptance criterion | `AC-<N>.<M>` | `AC-1.1`, `AC-2.3` |

**ID rules**: IDs are assigned once and never reused. Retired items are marked `(Retired)` — rows are never deleted. Every AC ID must trace forward to at least one task (PLN), one test (TST), and one commit.

## Tools

| Tool | Usage |
|---|---|
| `AskUserQuestion` | Structured user decisions (scope, approval, version) |
| `Edit` / `Write` | Create and modify files |
| `Read` | Read files |
| `Bash` | Run commands (pytest, ruff, zip, etc.) |
| `Grep` / `Glob` | Search codebase |
| `Agent` | Invoke sub-agents for each workflow phase |
