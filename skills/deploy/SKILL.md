---
name: deploy
description: >
  Automates the full git deploy flow end-to-end without user intervention: analyzes code changes to determine branch name, creates branch, splits and commits changes (via commit skill), detects GitHub or GitLab remote, pushes, creates PR/MR, auto-merges, and deletes both local and remote branch.
  Trigger when the user types /deploy, "deploy", "幫我 deploy", "推上去", "送 PR", "auto deploy", or any variation of wanting to push and merge changes.
---

# Auto Deploy Skill

Analyze the current git changes and execute the full deploy pipeline — branch creation, commit splitting, PR/MR creation, auto-merge, and branch cleanup — entirely without user prompts.

## Workflow

### Step 1: Check git status

```bash
git status --short
```

- If the working tree is clean, tell the user there's nothing to deploy and stop.
- If there are changes, proceed.

### Step 2: Detect remote type

Run the detection script:

```bash
python3 ~/.claude/skills/deploy/scripts/detect_remote.py
```

The script outputs one of:
- `GITHUB <remote-url>`
- `GITLAB <remote-url>`
- `ERROR <message>`

If ERROR, tell the user and stop.

### Step 3: Determine current base branch

```bash
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'
```

If this fails, fall back to checking for `main` then `master`:

```bash
git branch -r | grep -E 'origin/(main|master)' | head -1
```

Use this as the base branch for the PR/MR.

### Step 4: Generate branch name from changes

Run:

```bash
git diff HEAD --name-only
git diff --cached --name-only
git status --short
```

Analyze the changed files and their paths to infer a meaningful branch name:
- Use format: `<type>/<short-description>` (kebab-case, lowercase, max 40 chars)
- Types: `feature`, `fix`, `refactor`, `chore`, `docs`
- Examples: `feature/user-auth`, `fix/login-redirect`, `chore/update-deps`
- Base the description on the dominant change in the diff, not just filenames

### Step 5: Create and switch to branch

```bash
git checkout -b <branch-name>
```

### Step 6: Commit all changes via commit skill

Invoke the `commit` skill now. It will:
- Analyze the full diff
- Split changes into logical groups
- Stage and commit each group with Conventional Commits messages

Do not re-analyze the diff yourself — delegate entirely to the commit skill.

### Step 7: Push branch to remote

```bash
git push -u origin <branch-name>
```

### Step 8: Create PR or MR

**If GitHub:**
```bash
gh pr create --fill --base <base-branch>
```

**If GitLab:**
```bash
glab mr create --fill --target-branch <base-branch>
```

`--fill` uses the commit message(s) to populate the PR/MR title and description automatically.

### Step 9: Auto-merge

**If GitHub:**
```bash
gh pr merge --squash --delete-branch --yes
```

**If GitLab:**
```bash
glab mr merge --squash --remove-source-branch --yes
```

If merge fails (e.g., CI required, approvals needed), report the error to the user with the PR/MR URL and stop — do not retry.

### Step 10: Cleanup local branch

```bash
git checkout <base-branch>
git pull
git branch -d <branch-name>
```

If `git branch -d` fails (unmerged warning), use `-D` only if the remote branch was already deleted by the merge step.

### Step 11: Report result

Show the user:
- Branch name used
- Commit(s) created (messages + hashes)
- PR/MR URL
- Merge status
- Confirmation that branch was deleted locally and remotely

## Rules

- Never ask the user for the branch name, commit message, or PR title — infer everything from the diff.
- Never skip the commit skill in Step 6 — it handles the splitting logic.
- Never force-push. If push fails, report the error.
- Never merge if the merge step returns a non-zero exit code — surface the error instead.
- If the working directory has unstaged and untracked files mixed together, include both in the analysis.
