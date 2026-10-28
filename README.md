# p3-stack

p3-stack is [pstack](https://github.com/cursor/plugins/tree/main/pstack) rebuilt for T3 Code. Same engineering discipline, native T3 orchestration.

pstack is poteto's answer to AI slop code. It turns an agent into an engineering team: one mode skill that routes to playbooks, principles that ground every decision, and verification strict enough that you can parallelize with confidence. p3-stack keeps that system and rewires the mechanics to T3 Code's primitives:

- **Delegation.** `delegate_task` child agents replace Cursor's Task tool, with per-role providers and models resolved from `orchestrator_capabilities`. Cross-model panels are native.
- **Workspaces.** Managed boxes keep one prepared checkout and run writers sequentially. Workstations may use isolated worktrees when their setup supports them. Top-level T3 threads are created only when the user explicitly requests separate conversations.
- **Watching.** `watch_pull_request` wakes the thread when checks finish, someone comments, or the branch conflicts. No polling loops.
- **Scheduling.** `schedule_task` runs audits and overnight cadences even when no turn is active. No `/loop`.
- **Memory.** `t3_thread_read` and `t3_thread_search` replace mining Cursor transcript files.
- **Proof.** `preview_*` browser tools and `device_*` simulators replace external control skills. Screenshots and recordings land in the thread.

## This fork

This fork updates [uzairansaruzi/p3-stack](https://github.com/uzairansaruzi/p3-stack) to pstack **0.15.36**. [UPSTREAM.json](UPSTREAM.json) records the exact source commit and every included or excluded skill and agent file. T3 retains its own delegation, model discovery, PR watching, scheduling, and browser tools. Upstream installation adapters, PR pollers, and orchestration scripts are not installed.

New skills include `/ketchup-video`, `/ketchup`, `/sharpen`, `/in-your-own-words`, `/create-formal-verification-skill`, `/maintain-formal-verification-skill`, and `/statechart`.

## Install

```bash
git clone https://github.com/timkrase/p3-stack.git
cd p3-stack
./install.sh
```

`install.sh` links every `skills/*` directory into `~/.agents/skills/`, where T3 Code reads skills. Use `./install.sh --project /path/to/repo` to install into a project's `.agents/skills/` instead.

## Get started

1. Run `/setup-p3`. It reads `orchestrator_capabilities` and writes `p3-models.md`, mapping each role (code, judgment, the review panels) to a provider and model you actually have.
2. Use `/p3-mode` whenever you want rigorous work. It reads the request, picks a playbook, and runs the other skills as the steps need them.
3. Stuck or unsure which skill fits? Ask `/p3-help`.

## The mode

`p3-mode` routes every task. Its playbooks: investigation, bug fix, perf issue, hillclimb, runtime forensics, trace forensics, feature, refactoring, prototype, visual parity, authoring a skill, eval, babysit, shipping, autonomous run, orchestrate, autopilot-full, autopilot-stack, session pickup, pause safely, multi-phase plan, worktree cleanup, opening a PR.

## Skills

architect, arena, automate-me, benchmark-checklist, blast-radius, bro, correct, create-formal-verification-skill, create-verification-skill, figure-it-out, how, in-your-own-words, interrogate, ketchup, ketchup-video, maintain-formal-verification-skill, maintain-verification-skill, make-bot-ui, no-comments, p3-help, recall, reflect, setup-p3, sharpen, show-me-your-work, statechart, swarm, tdd, teach, technical-writing, typescript-best-practices, unslop, why.

## Principles

The twenty-four principle skills are indexed inside `p3-mode` and referenced by the other skills by name.

## Check the port

Run the structural checks with Python 3.10 or later:

```sh
python3 scripts/check-port.py
python3 -m unittest discover -s scripts -p 'test_*.py'
```

To check source hashes and complete file coverage, clone `cursor/plugins` and run `python3 scripts/check-port.py --upstream /path/to/cursor-plugins`. The checkout must contain the commit recorded in `UPSTREAM.json`.

Statechart's launcher supports Node.js 22.18 through 22.x, Node.js 23.6 or later, Bun 1.1.5 or later, or Deno 2.0 or later. Run its tests with one of those supported Node.js versions. The first model check uses `mise` to install the upstream-pinned TLC 1.7.4 and Java. Alternatively, set `TLA2TOOLS` to `tla2tools.jar` and `JAVA` to a Java 11 or later binary. SVG rendering uses Pele 1.9.0, as described in the statechart skill.

```sh
cd skills/statechart/scripts
npm install --ignore-scripts --package-lock=false
TLA2TOOLS=/path/to/tla2tools.jar JAVA=/path/to/java npm test
```

The tests need a JDK because the config fuzz test runs a Java source file. On macOS, use `TMPDIR=/private/tmp` so relative-symlink tests start from a physical path. The tests install their pinned renderers in the user cache. Tests that require TLC are skipped when `TLA2TOOLS` is unset. Run with TLC before publishing an update.

The external code-cleanup pass used by upstream's PR playbooks is bundled in `skills/p3-mode/references/code-cleanup.md`. Its source and hash are recorded in `UPSTREAM.json`, alongside the pstack files. This keeps the pass available without a separate plugin installation.

## Credit

p3-stack adapts [pstack](https://github.com/cursor/plugins/tree/main/pstack) by [poteto](https://x.com/poteto). The skills, principles, and language are hers; the T3 Code rewiring is this repo's. MIT, see [LICENSE](LICENSE).
