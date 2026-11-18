---
name: principle-separate-before-serializing-shared-state
description: "Apply when concurrent actors might write to the same file, branch, key, or state object. Eliminate the sharing first; serialize structurally only when one shared writer is a real invariant."
disable-model-invocation: true
---

# Separate Before Serializing Shared State

When concurrent actors might write the same file, branch, key, or object, first ask whether they need one shared object or are publishing independent facts. Default to giving each actor its own file, key, branch, or state directory, and merge only where the state is read. Two workers writing their own field into one `state.json` is still shared mutation.

Only when one shared write target is a real invariant, serialize access structurally (a lockfile, a single writer, sequential phases, compare-and-swap). Instructions are not concurrency control, and "we need a lock" is a smell to check first.

## Managed boxes

Choose the workspace before scheduling writers. Read the repository's environment instructions and inspect existing setup markers. A managed box or sandbox with services bound to one prepared checkout has one shared write target. For example, `.horaizon-worktree/state.json` with `t3Sandbox: true` identifies such a box. A plain git checkout is not proof that another checkout has the same dependencies, mounts, ports, or database.

In these boxes, use the existing checkout. Do not create additional worktrees or clones, even under `/tmp`, and do not copy or symlink the managed setup into another directory. These rules override worktree and parallel-writer defaults in other skills and playbooks.

Run repository writers sequentially. Delegate one writer, wait for its task to finish, inspect and verify its changes, then start the next. The parent must not edit while a delegated writer runs. Tests, migrations, dependency installs, and commands that mutate shared services also need exclusive access. Include the canonical checkout path and this restriction in every brief. Parallel read-only research is fine; reviews need a stable revision and must finish before it changes. Independent design documents may use separate scratch files, but those files are not runnable checkouts.

Multiple PRs do not require multiple worktrees. Finish, verify, and commit one slice before the next. Preserve branch refs for each PR; for a stack, branch the next slice from the previous tip. Switch branches only with a clean checkout, after all workers and verification commands using it finish. Respect T3's workspace binding; if a branch switch would leave it stale or disrupt the running setup, keep working in ordered commits on the bound branch and create PR refs without switching. Never reset or stash somebody else's work to make room. PR creation and splitting still follow the user's authorization and repository rules.

Parallel runnable implementations require separately provisioned boxes with their own setup and user authorization. If the workspace contract is unclear, keep the existing checkout and serialize until it is established. On a workstation whose setup supports independent checkouts, separate worktrees remain an option, with one writer per worktree.
