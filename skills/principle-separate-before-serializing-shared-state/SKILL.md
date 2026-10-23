---
name: principle-separate-before-serializing-shared-state
description: "Apply when concurrent actors might write to the same file, branch, key, or state object. Eliminate the sharing first; serialize structurally only when one shared writer is a real invariant."
disable-model-invocation: true
---

# Separate Before Serializing Shared State

When concurrent actors might share mutable state, first ask whether they need the same mutable object. If not, eliminate the sharing. When sharing is real, enforce serialization structurally: lockfiles, sequential phases, exclusive ownership. Instructions and conventions are not concurrency control.

**Why:** Concurrent writes to shared state create race conditions that are intermittent, hard to reproduce, and expensive to debug.

**Pattern:**
1. **Identify shared mutable state** (files both read and write, branches both push to, APIs both define and consume).
2. **Default: eliminate the shared write target.** Ask: do these actors need one canonical object, or are they publishing independent facts? Give each actor its own owned file, key, branch, or state directory, and merge only at the read/reporting boundary. Two workers writing their own `lastX` field into one `state.json` is still shared mutation. `indexer-state.json` + `metrics-state.json` is not.
3. **Only when one shared write target is a real invariant, serialize access structurally** (lockfiles, sequential phases, single-writer actor, or atomic compare-and-swap). Treat "we need a lock" as a design smell to check, not as the default answer.

## Managed boxes

Choose the workspace before scheduling writers. Read the repository's environment instructions and inspect existing setup markers. A managed box or sandbox with services bound to one prepared checkout has one shared write target. For example, `.horaizon-worktree/state.json` with `t3Sandbox: true` identifies such a box. A plain git checkout is not proof that another checkout has the same dependencies, mounts, ports, or database.

In these boxes, use the existing checkout. Do not create additional worktrees or clones, even under `/tmp`, and do not copy or symlink the managed setup into another directory. These rules override worktree and parallel-writer defaults in other skills and playbooks.

Run repository writers sequentially. Delegate one writer, wait for its task to finish, inspect and verify its changes, then start the next. The parent must not edit while a delegated writer runs. Tests, migrations, dependency installs, and commands that mutate shared services also need exclusive access. Include the canonical checkout path and this restriction in every brief. Parallel read-only research is fine; reviews need a stable revision and must finish before it changes. Independent design documents may use separate scratch files, but those files are not runnable checkouts.

Multiple PRs do not require multiple worktrees. Finish, verify, and commit one slice before the next. Preserve branch refs for each PR; for a stack, branch the next slice from the previous tip. Switch branches only with a clean checkout, after all workers and verification commands using it finish. Respect T3's workspace binding; if a branch switch would leave it stale or disrupt the running setup, keep working in ordered commits on the bound branch and create PR refs without switching. Never reset or stash somebody else's work to make room. PR creation and splitting still follow the user's authorization and repository rules.

Parallel runnable implementations require separately provisioned boxes with their own setup and user authorization. If the workspace contract is unclear, keep the existing checkout and serialize until it is established. On a workstation whose setup supports independent checkouts, separate worktrees remain an option, with one writer per worktree.
