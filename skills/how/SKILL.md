---
name: how
description: "Use for \"how does X work\", code walkthroughs before changing something, and placement / ownership / layering questions (\"where should this live\", \"which package owns this\", \"is this the right layer\"). Explains subsystem architecture, runtime flow, onboarding mental models. Use why for motivation."
disable-model-invocation: true
---

# How

Explore the codebase to answer "how does X work?" questions.

If the scope is ambiguous, state your interpretation and explore. The user can redirect.

## 1. Explain

Spawn one `delegate_task` worker (`mode: "async"`, drained with `task_status`) that explores and explains in one pass. The worker gets only the brief, never your context, so the brief stands alone: the user's question, the scope in play, that it is read-only (inspect only, no writes), and this text:

> You are writing an architectural explanation for a senior engineer. Explore the codebase and write an explanation that a senior engineer unfamiliar with this area could read and walk away with a solid mental model. They should understand the architecture well enough to start working in it confidently. You have read-only access to the codebase.

## 2. Present

Present the worker's output. Light edits for clarity or context from the conversation are fine. Do not substantially rewrite it.
