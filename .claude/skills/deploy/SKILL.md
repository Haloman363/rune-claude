---
name: deploy
description: Stage all changes, commit with a generated message, push to origin, open a PR, and merge it. Runs the full commit → push → merge workflow in one shot.
disable-model-invocation: false
---

You are executing the `/deploy` skill for the rune-claude project.

## Steps

1. Run `git status` and `git diff --stat` to see what's changed.
2. Run `git log --oneline -5` to match the commit message style.
3. Stage only tracked/relevant files — skip `.claude/`, `*.png`, `User-Uploads/`, `.playwright-mcp/` (these are in `.gitignore`).
4. Write a concise commit message following the repo's `type(scope): description` convention.
5. Commit, push to origin, create a PR with `gh pr create`, then merge it with `gh pr merge --merge --delete-branch`.
6. Switch back to `main` and pull.

## Rules

- Never commit `.env`, secrets, or credential files.
- If there are no changes to commit, say so and stop.
- Use a HEREDOC for the commit message to preserve formatting.
- Add `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>` to every commit.
