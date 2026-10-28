---
name: arena
description: "Spawn N parallel candidates at the same task, pick a base, graft the strongest parts of the losers into it. Use for /arena, 'arena this', 'throw it in the arena', or when one attempt at a non-trivial artifact would lock in the wrong shape."
disable-model-invocation: true
---

# Arena

For each delegate, match effort to the job per the Subagents section of `../p3-mode/SKILL.md`, preserving the configured role and provider.

Open a todolist with one entry per phase (Frame, Fan out, Cross-judge, Pick, Graft, Verify) before launching anything.

## Phase A: Frame

Every candidate gets the same prompt, so the prompt is the contract.

1. State the artifact each candidate is producing.
2. Derive the rubric. State what success looks like for *this* task, then turn it into 3-6 concrete gradeable criteria. The rubric is the picker's tool in Phase D. Candidates only see the task.
3. Pick the runners. Use the `arena runners` line in `p3-models.md`, resolved against `orchestrator_capabilities`. If the file or that line is missing, run `setup-p3` or pick one model per available provider from `orchestrator_capabilities`. An `auto` or `inherit-parent` entry in this line means the parent model, so omit `model` for it. If `delegate_task` rejects a configured entry, use the closest available model of the same family from `orchestrator_capabilities`, or drop the seat when none is available, and say so. If dropped seats leave fewer than two runners, add runners until there are two, or one when the line has one entry. Use a remaining runner's model, or inherit the parent when none remain, and report the fallback. Spawn more when the arena covers multiple design directions. Same model N times when the work is generation-bound rather than judgment-sensitive.
4. Assign output paths using the [workspace rules](../principle-separate-before-serializing-shared-state/SKILL.md#managed-boxes). Design documents may use `/tmp/arena-<slug>/candidate-<n>/`. In a managed box, runnable candidates use the one prepared checkout sequentially; record each candidate in commits before the next, preserve its result, and never create another checkout. Separate worktrees are an option only when the environment supports them. Include the path and restriction in each brief.

## Phase B: Fan out

Spawn candidates with `delegate_task`, one per runner entry, each with `mode: "async"`. Start them together only when step 4 permits parallel execution; otherwise drain and verify each candidate before starting the next. T3 child agents get only the brief, never the parent's context, so every brief stands alone: the task, the path to the shared grounding, its own output path, and instructions to produce both the artifact and a short rationale.

Each rationale names the alternatives the candidate considered and what it rejected.

Drain the candidates with `task_status`. If a candidate fails to produce output, proceed with N-1 and note the dropout in the synthesis record.

## Phase C: Cross-judge

After all Phase B candidates complete, choose one model from the `arena cross-judge pool` line in `p3-models.md`, resolved through `orchestrator_capabilities`. The judge is never from the parent's model family. Try only entries from another family, in pool order. A different provider does not by itself mean a different model family. An `auto` or `inherit-parent` entry never judges. If an entry is rejected, try an available variant of that model, then the next pool entry. If none runs, try another available model family from the catalog. If none runs, skip the judge, pick the base alone in Phase D, and say so. If the parent's model is unknown, try the pool's explicit models in order and report that the family check did not run.

Spawn one judge with `delegate_task`, `mode: "async"`. Its self-contained brief says read-only: inspect only, no writes. It sees the rubric and candidates by path label, scores each criterion, and recommends a base with rationale. It runs in parallel with your reading in Phase D, after all candidates finish writing.

## Phase D: Pick a base

Read every candidate end to end before picking. Score each against the rubric criterion by criterion, not on holistic feel, and compare with the cross-judge when Phase C ran one. Agreement on the base confirms the pick. Disagreement means one of you is biased or the rubric was ambiguous. Read both rationales before deciding.

Pick the base a future maintainer can extend most easily without breaking invariants. When two feel tied, prefer the cleaner boundary or smaller API, per the Laziness Protocol.

## Phase E: Graft

Walk each losing candidate once more for what is worth porting into the base, usually one or two things per candidate, not most of it. Fold each graft in by hand, per the **redesign-from-first-principles** principle skill, so the result stays coherent under one mental model. Don't paste mechanically.

If the candidates converge on one shape, that is strong agreement. Note it and ship the consensus shape. No graft is needed. If they wildly diverge, Phase A was under-specified. Reframe and re-run rather than averaging the divergence.

## Phase F: Verify

Verify the synthesized artifact like any other output, per the **prove-it-works** principle skill. If verification finds a problem the arena missed, either Phase A was wrong (re-frame and re-run) or a candidate caught it and you missed the graft (go back to Phase E). Don't paper over it.

## Outputs

One synthesized artifact, with a short synthesis note alongside naming the base and why, the cross-judge's verdict or that Phase C skipped the judge, each graft with its source candidate, what was rejected and why, any convergence or dropouts, and the verification result.
