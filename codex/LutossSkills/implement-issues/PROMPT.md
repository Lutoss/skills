# Issues

Local issue files from `.scratch/<feature>/issues/` are provided at the start of context. Parse them to understand the open issues.

Work on AFK issues only: `Status: ready-for-agent` or `Labels: ready-for-agent`.

Do not work on HITL issues: `ready-for-human`, `needs-info`, `needs-triage`, blocked issues, or issues with `Implementation: done`.

Recent commits may be provided. Review them to understand what work has already been done.

If all AFK tasks are complete, output `<promise>NO MORE TASKS</promise>`.

If an `# Assigned Issue` section is present, work only that issue. If a `# Current Parallel Batch` section is present and no single issue is assigned, act as the coordinator: split that batch across worker subagents when available, usually one worker per issue.

## Task Selection

Process dependency waves. In each wave, all unblocked issues in the current parallel batch can start immediately. Prioritize issues inside a batch in this order when subagents are limited:

1. Critical bugfixes
2. Development infrastructure
3. Tracer bullets for new features
4. Polish and quick wins
5. Refactors

Development infrastructure like tests, types, and dev scripts is an important precursor to building features.

Tracer bullets are small end-to-end slices of functionality that go through all layers of the system, allowing the approach to be tested and validated early.

TL;DR: build a tiny end-to-end slice of the feature first, then expand it out.

## Coordination

As coordinator:

- Rebuild the queue before each wave.
- Spawn worker subagents for every independent issue in the current batch when tools allow it.
- Give each worker exactly one assigned issue and a disjoint likely write scope when known.
- Tell workers they are not alone in the codebase and must not revert others' changes.
- Wait for the wave, inspect results, integrate changes, rerun relevant feedback loops, then rebuild the queue.
- Continue until no AFK issues remain.

As worker:

- Work only the assigned issue.
- Stop after the assigned issue.
- Report status, files changed, verification commands, blockers, and whether `Implementation: done` was set.

## Exploration

Explore the repo before editing. Read local agent docs, domain docs, and relevant ADRs when they exist.

## Implementation

Use the $tdd skill to complete the task:

- Write one behavior test.
- Confirm it fails for the right reason.
- Implement the smallest code change that makes it pass.
- Repeat for the next behavior.
- Refactor only while tests are green.

## Feedback Loops

Before marking an issue done, run the smallest useful feedback loops for the touched area. Prefer targeted tests first, then broader checks such as:

- `npm run test`
- `npm run typecheck`
- framework-specific lint/build/check commands
- manual or Playwright verification when UI behavior is involved

Use the commands that actually exist in the repo.

## Completion

If the task is complete:

- Set `Implementation: done` in the issue file.
- Leave `Status:` and `Labels:` intact unless triage really changed.
- Append a `## Comments` note summarizing behavior changed, verification run, and any follow-up.
- Stop after this issue if you are a worker. Coordinators may continue with the next dependency wave after rebuilding the queue.

If the task is not complete:

- Set `Implementation: needs-info` or leave `Implementation: in-progress`, whichever is more accurate.
- Append a comment explaining what was done, what blocked completion, and the next concrete action.

## Commit

If the repo is a git repository and the completed wave is coherent, ask before committing unless the user already requested commits.

The commit message should include:

1. Key decisions made
2. Files changed
3. Blockers or notes for the next iteration
