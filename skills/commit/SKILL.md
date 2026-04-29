---
name: commit
description: >
  Automatically reads git diff, groups changes, writes Conventional Commits formatted message(s), stages files, and commits — all without user intervention.
  Invoked manually via /commit in Claude Code.
  Also triggers when the user asks to "commit my changes", "幫我 commit", "自動 commit", "看我改了什麼然後 commit", or any variation of wanting to commit their current git changes.
---

# Git Auto-Commit Skill

Analyze git changes and automatically stage and commit them with well-formed Conventional Commits message(s). Run the full workflow end-to-end without asking for confirmation.

## Workflow

### Step 1: Check git status
```bash
git status
git status --short
```
- If the working tree is clean (nothing to commit), tell the user and stop.
- If there are changes, proceed.

### Step 2: Capture the full diff
```bash
git diff
git diff --cached
```
Read both staged and unstaged diffs to understand the full scope of changes.

### Step 3: Analyze and group the changes

Carefully read the diff and group changed files by their **logical concern**:
- What changed (files, functions, logic)
- Why it likely changed (new feature, bug fix, refactor, config, docs, etc.)
- Which module/component is affected

**Decide: single commit or multiple commits?**

Split into multiple commits when the changes clearly contain **unrelated concerns**, for example:
- A bug fix in `api/` + a new feature in `ui/` → 2 commits
- Dependency update + business logic change → 2 commits
- 5+ files spanning completely different domains → consider splitting

Keep as a single commit when:
- All changes serve one coherent purpose
- Files are in the same feature/module
- The diff is large but all related (e.g., a big refactor)

### Step 4: Write the commit message(s)

Use **Conventional Commits** format for each commit:
```
<type>(<scope>): <short description>

[optional body]
```

**Types:**
| Type | When to use |
|------|-------------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `refactor` | Code restructuring without behavior change |
| `chore` | Tooling, dependencies, config, scripts |
| `docs` | Documentation only |
| `style` | Formatting, whitespace (no logic change) |
| `test` | Adding or fixing tests |
| `perf` | Performance improvement |
| `ci` | CI/CD changes |
| `build` | Build system changes |

**Rules:**
- Subject line: imperative mood, lowercase after the colon, no period, max 72 chars
- Scope: optional, use the module/folder/feature name if clear
- Body: only add if changes are complex and need explanation
- Write in **English**

### Step 5: Stage and commit

#### If single commit:
```bash
git add .
git commit -m "<subject>"
```
If the message has a body:
```bash
git add .
git commit -m "<subject>" -m "<body>"
```

#### If multiple commits:
Stage and commit each group separately in order:
```bash
git add <files for commit 1>
git commit -m "<message 1>"

git add <files for commit 2>
git commit -m "<message 2>"
```

### Step 6: Confirm to the user
After committing, show:
- The commit message(s) used
- The files included in each commit
- The commit hash(es) from `git log --oneline -<n>`

## Edge Cases

- **No git repo**: If `git status` fails, tell the user there's no git repository in the current directory.
- **Merge conflicts**: If there are conflict markers, do NOT suggest committing. Warn the user to resolve conflicts first.
- **Very large diffs**: Focus on the high-level pattern rather than every line. Group by domain/module.
- **Binary files only**: Use the filename/type to infer the message (e.g., `chore: update logo assets`).
- **Already staged files**: Respect what the user has already staged — don't suggest `git add .` if they've been selective with staging.
