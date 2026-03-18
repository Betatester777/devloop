---
name: release-notes
description: "Generate release notes and user-facing guidance for approved increments."
---

# release-notes

## Purpose

Produce clear, user-oriented release notes that cover what's new, migration steps, known issues, and usage guidance.

## Trigger

Invoked by the release manager during the Release phase.

## Inputs

- Approved increment
- `docs/REV.md`

## Outputs

- `docs/REL.md`
- `releases/v<major.minor.sub>/release-v<major.minor.sub>.zip` — zip archive containing `src/`, `docs/REL.md`, and `docs/REV.md`
- `releases/v<major.minor.sub>/REL.md` — copy of release notes for quick reference

## Procedure

### Creating release notes

1. Copy `templates/REL.md` to `docs/REL.md` (or append a new version section if the file already has prior releases).
2. Read `docs/REV.md` for the increment summary, changes, and test results.
3. Determine the version number (`major.minor.sub`). If the user confirmed a version during the ask-tool interaction, use that. Otherwise:
   - First release → `0.1.0`
   - New features added → bump minor (`0.1.0` → `0.2.0`)
   - Bug fixes only → bump sub (`0.1.0` → `0.1.1`)
   - Breaking changes → bump major (`0.x.y` → `1.0.0`)

#### Version
Write the version number.

#### Release Date
Use today's date in `YYYY-MM-DD` format.

#### What's New
Write user-facing descriptions — focus on what the user can now **do**, not what code changed. Avoid internal jargon. Reference the REQ-N ID for traceability.

Good:
```markdown
- **Markdown conversion** (REQ-1): convert any `.md` file to clean HTML5 with a single command.
- **Syntax highlighting** (REQ-3): fenced code blocks are automatically highlighted using Pygments.
```

Bad:
```markdown
- Added converter.py with AST node types.
- Implemented TokenStream class.
```

#### Traceability
Add a traceability table listing every REQ and AC delivered:

```markdown
| REQ ID | AC IDs delivered | Commit(s) |
|---|---|---|
| REQ-1 | AC-1.1, AC-1.2 | abc1234 |
```

#### Migration Notes
If this version changes behavior or removes features, write step-by-step migration instructions:

```markdown
### Migrating from 0.1.0 to 0.2.0
1. The `--format` flag was renamed to `--output-format`. Update any scripts.
2. The default output encoding changed from ASCII to UTF-8. No action needed unless you relied on ASCII.
```

If no migration is needed, write: "No migration steps required."

#### Known Issues
List issues that exist in this release but are not yet fixed:

```markdown
- Tables with merged cells are not supported (planned for Bundle 3).
- Watch mode does not detect new files, only changes to existing files.
```

If none, write: "No known issues."

#### User Guide
Provide concise usage instructions with examples:

```markdown
### Basic usage
python src/converter.py input.md -o output.html

### Batch conversion
python src/converter.py docs/*.md --output-dir build/html/

### Options
- `-o, --output FILE` — output file path (default: stdout)
- `--output-dir DIR` — output directory for batch mode
- `--highlight` — enable syntax highlighting (default: on)
```

### Updating release notes (multi-bundle release)

If the user skipped release for earlier bundles and now wants combined notes:
1. Read all `docs/REV.md` entries (current and prior approved bundles).
2. Combine the What's New sections chronologically.
3. Merge Migration Notes and Known Issues, removing duplicates.
4. Use the latest version number.

### Packaging the release archive

After `docs/REL.md` is finalized, create a versioned release directory and zip:

1. Create `releases/v<major.minor.sub>/`.
2. Build the zip containing only the release deliverables:
   ```bash
   mkdir -p releases/v<major.minor.sub>
   zip -r releases/v<major.minor.sub>/release-v<major.minor.sub>.zip \
     src/ docs/REL.md docs/REV.md \
     --exclude '*.pyc' '__pycache__/*' '.venv/*' 2>/dev/null; true
   cp docs/REL.md releases/v<major.minor.sub>/REL.md
   ```
3. Verify the zip exists and is non-empty (`ls -lh releases/v<major.minor.sub>/`).

## Validation checklist

Before handoff, verify:
- [ ] Version number follows `major.minor.sub` format.
- [ ] Release Date is set.
- [ ] What's New describes user-facing capabilities, not code changes.
- [ ] Each What's New item references its REQ-N ID.
- [ ] Traceability table lists all delivered REQ and AC IDs with commit hashes.
- [ ] Migration Notes are present or explicitly marked "No migration steps required."
- [ ] Known Issues are listed or explicitly marked "No known issues."
- [ ] User Guide has at least one usage example with a runnable command.
- [ ] `releases/v<major.minor.sub>/release-v<major.minor.sub>.zip` exists and is non-empty.
- [ ] `releases/v<major.minor.sub>/REL.md` exists alongside the zip.
