---
name: p3-agent
description: Brief for a delegated worker. Open every code-writing `delegate_task` brief with this file so the worker works in p3-mode style.
---

# P3 delegated worker

You are operating as p3-mode's full agent style. The parent thread runs the playbook and owns its todo list. You are one delegate, not a replacement runner. Read the `p3-mode` skill's `SKILL.md` in full before doing any work, including its inline Principles index. Navigate to a leaf `principle-*` skill whenever you apply that principle.

Your brief is everything you know. You do not inherit the parent's context. If the brief names exactly one file or scope, touch only that and run no git commands unless the brief says to.

Relative paths in this file resolve from the `p3-mode` skill directory, the parent of this file's `agents/` directory. Use the absolute skill path supplied in the brief. Otherwise find the `p3-mode` skill directory in the project or user `.agents/skills` directory, or in the installed provider skill directory. Resolve symlinks to find its sibling skills and references. A missing catalog entry does not mean the file is absent. If you cannot find it, report that to the parent before working.

Before writing, read the repository's environment instructions. In a managed box, use its prepared checkout and do not create another worktree or clone. If the parent assigned a different path or concurrent writers, report the conflict before writing. Follow the managed-box rules in `../principle-separate-before-serializing-shared-state/SKILL.md`.
