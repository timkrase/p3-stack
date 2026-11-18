### Opening a PR

Invoked at the end of every other playbook.

**Workspace.** Follow the [workspace rules](../../principle-separate-before-serializing-shared-state/SKILL.md#managed-boxes). Managed boxes keep their prepared checkout and finish one writer and its verification before starting another. An occupied checkout means wait, not create another worktree. Include its path, branch, and restriction in every brief; preserve unrelated changes. Rebase into small, landable commits. Run the code-cleanup pass in [code-cleanup.md](../references/code-cleanup.md) and the **unslop** skill over the diff before commit.

Title: `type(scope): subject`, naming a real symbol when one carries the change. Body: a one-minute briefing under 40 lines with these `##` headings in order, dropping empty ones: `## Why`, `## What changed`, `## Scope`, `## Tradeoffs` (only rejected alternatives a reviewer would otherwise ask about), `## Blast Radius`, `## Verification`.

Stack follow-ups by base branch. Open PRs ready, with `gh pr create` without `--draft`. `link_pull_request` registers a PR rather than creating one, so call it with the full URL the moment a PR opens, and link every layer of a stack. Follow the user's requested PR count and repository policy. Opening a PR does not start a babysit.
