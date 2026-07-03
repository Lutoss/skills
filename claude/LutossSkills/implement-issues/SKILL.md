---
name: implement-issues
description: Implement ready local Markdown issues produced by to-issues using dependency-aware parallel subagent batches and TDD. Use when the user says /implement-issues, run the issues, implement ready issues, work through .scratch issues, loop over issues, parallelize issue implementation, or wants to start implementation after approving /to-issues output.
---

# Implement Issues

Turn approved `.scratch/<feature>/issues/*.md` files into working code, one dependency wave at a time.

This skill is designed to run immediately after /to-issues (local tracker): once the user approves the issue breakdown, invoke this skill with the feature directory or issue paths.

The intended shape: humans review idea, PRD, and issue split; AFK agents handle implementation; QA/code review comes back to humans or a fresh review agent afterwards.

## Quick Start

From the repo root, run the helper scripts that ship in this skill's `scripts/` directory (use the absolute path of this skill folder — typically `~/.claude/skills/implement-issues/` or the project's `.claude/skills/implement-issues/`):

```bash
node <skill-dir>/scripts/list-ready-issues.mjs .scratch/<feature-slug>
node <skill-dir>/scripts/build-agent-prompt.mjs .scratch/<feature-slug>
node <skill-dir>/scripts/build-agent-prompt.mjs .scratch/<feature-slug> --issue .scratch/<feature-slug>/issues/01-example.md
```

Use `build-agent-prompt.mjs` to inspect one wave, tune the prompt/issue format, then repeat. Do not start with a blind long-running loop.

## Inputs

- A feature directory: `.scratch/<feature-slug>/`
- One or more issue files: `.scratch/<feature-slug>/issues/01-example.md`
- No input: inspect `.scratch/` and ask the user which feature to run if more than one candidate exists.

Only implement issues that are `Status: ready-for-agent` or have `ready-for-agent` in `Labels:`. Skip issues marked `Implementation: done`.

Treat `ready-for-agent` as AFK. Treat `ready-for-human`, `needs-info`, `needs-triage`, blocked issues, and completed issues as HITL/skipped.

## Workflow

1. Read the local project instructions:
   - `docs/agents/issue-tracker.md`
   - `docs/agents/triage-labels.md`
   - `docs/agents/domain.md`
   - `CONTEXT.md` and relevant `docs/adr/` files if they exist.
2. Inventory candidate issues with `scripts/list-ready-issues.mjs`.
3. Present the dependency batches and get approval unless the user already explicitly approved implementation.
4. Loop until there are no AFK issues left:
   - Rebuild the queue before each wave.
   - Take the current parallel batch: all ready issues whose blockers are already done.
   - Spawn one worker subagent per issue in the batch — send all Agent tool calls for the wave in a single message so they run in parallel.
   - Give each worker exactly one issue via `build-agent-prompt.mjs --issue <issue-file>`.
   - If subagents are unavailable, process the batch sequentially.
   - Wait for the wave to finish, inspect each worker result, integrate non-conflicting changes, and rerun the relevant feedback loops.
   - Rebuild the queue; newly unblocked issues become the next wave.
5. Each worker must:
   - Read the full issue, comments, acceptance criteria, and linked parent PRD.
   - Set or update `Implementation: in-progress` near the top of the issue.
   - Apply the TDD discipline from the /tdd skill: one behavior test, watch it fail, minimal implementation, watch it pass, then repeat.
   - Treat approved acceptance criteria as the behavior plan. If criteria are unclear, stop that issue and mark `Implementation: needs-info` with a short comment.
   - Run targeted verification first, then the smallest sensible broader regression command.
   - Set `Implementation: done` only after all acceptance criteria are satisfied and verification passes.
   - Append a concise `## Comments` entry with changed behavior and verification commands.
6. After each wave or coherent change set, tell the user whether a commit would make sense.

For an external runner, generate the full prompt context with `scripts/build-agent-prompt.mjs`. The reusable prompt contract lives in [PROMPT.md](PROMPT.md).

If no AFK issues remain, report `<promise>NO MORE TASKS</promise>` in the runner context or tell the user directly in conversation.

## TDD Rules

- Tests must exercise public behavior, not private implementation.
- Do not write all tests first. Use vertical RED-GREEN cycles.
- Expected values must come from the issue/spec or a concrete worked example, not from recomputing implementation logic.
- Never refactor while tests are red.
- If no automated test harness exists for the touched behavior, create the narrowest useful verification harness or document the manual verification clearly in the issue comment.

## Dependency Rules

- Never implement an issue whose `## Blocked by` section names unfinished blockers.
- If blockers are also in the queue, they form earlier dependency batches.
- When priorities are otherwise equal, follow this order: critical bugfixes, development infrastructure, tracer bullets, polish/quick wins, refactors.
- Parallelize all issues in the current batch when the work scopes are independent or each worker runs in an isolated subagent workspace (use worktree isolation when available).
- Do not let two workers edit the same files in the same worktree. If likely write scopes overlap, split that batch into smaller waves or assign one coordinator-owned sequential task.
- Tell workers they are not alone in the codebase, must not revert others' changes, and must report files changed plus verification commands.

## Subagent Coordination

- Use worker subagents for concrete implementation tasks, not vague exploration.
- Give each worker ownership of exactly one issue and, when known, a likely file/module scope.
- Include the skill path and the assigned issue path in each worker prompt.
- Ask workers to stop after their assigned issue and return: status, files changed, tests run, blockers, and whether `Implementation: done` was set.
- After workers finish, review and integrate results before starting the next dependency batch.

## Review Boundary

Implementation can be AFK; QA and code review are separate. After an AFK pass, run /code-review (or /review-loop for review-to-closure) with a cleared context when the change is large enough to matter.

## Completion Marker

The local triage labels do not include a completion state, so this skill uses a separate machine-readable line near the top of each issue:

```md
Implementation: in-progress
Implementation: needs-info
Implementation: done
```

Leave the existing `Status:` and `Labels:` triage lines intact unless the issue itself needs triage changes.
