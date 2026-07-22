---
name: agent-orchestration
description: Route delegated work to the right worker (gpt-5.6 sol/terra/luna sub-runs via codex exec, or Claude via ask-claude), verify the result, and record a mandatory evaluation in a self-maintained scoreboard. Use whenever delegating substantial work to a sub-run or to Claude, when choosing a model for a task, when the user asks which model is best for something, or asks for the scoreboard/leaderboard.
---

# Agent Orchestration

You (the orchestrator) maintain your own evaluation table of how well each
model performs each kind of task. Every substantial delegation ends with a
scored evaluation. Over time the scoreboard — not static priors — decides
routing.

All writes go through `scripts/log_eval.mjs` (requires Node.js); never edit
`evaluations.jsonl` or `SCOREBOARD.md` by hand. The script resolves the
data directory in this order: `--data-dir` flag > `AGENT_ORCH_DATA` env
var > `scripts/data-dir.txt` next to the script > `~/.agent-orchestration`
(created automatically).

**First use in a new environment:** if none of the first three are set,
the store lands in `~/.agent-orchestration` — fine for a single-machine
setup. To share one scoreboard with other agents (e.g. the Claude pack's
copy of this skill), point `scripts/data-dir.txt` (untracked,
machine-local) or `AGENT_ORCH_DATA` at the same directory. Ask the user
once rather than guessing.

## Glossary (score axes, 1-10)

- **Correctness** — did the result hold up under verification? 10 = verified
  correct as delivered; 5 = usable after material corrections; 1 = wrong,
  unsafe, or no useful progress.
- **Taste** — quality of the output beyond correctness: code style fitting
  the repo, API design, UI/UX, copy, minimal scope, no unrelated edits.
- **Efficiency** — time and tokens relative to the task. Overthinking,
  rework loops, and overreach lower this even if the result is fine.

A polished answer is not evidence. Deterministic checks (tests, diffs,
source references, screenshots) outrank the worker's self-report.

## Workflow per delegation

1. **Classify** the task with one task kind (`node scripts/log_eval.mjs kinds`
   lists them; extend deliberately with `--new-kind`).
2. **Route**: read `SCOREBOARD.md`. Rows with n >= 5 evaluated runs for that
   task kind outrank priors; below that, treat the priors section as
   cold-start defaults. Respect a user-pinned model.
3. **Explore** occasionally: for roughly every 5th low-risk, easily
   verifiable delegation, deliberately pick the runner-up or an
   under-represented model and flag the eval `--exploration`. Never on
   shipping-relevant work.
4. **Delegate** using [delegation-recipes.md](references/delegation-recipes.md)
   (`codex exec` sub-run mechanics, prompt style, effort, timeouts; Claude
   via the `ask-claude` skill).
5. **Verify** the result yourself against the real feedback signal before
   accepting it.
6. **Evaluate** — the delegation is not finished until this ran:

   ```
   node scripts/log_eval.mjs add \
     --model gpt-5.6-terra --effort medium --task-kind code_review \
     --project lakebed --correctness 8 --taste 7 --efficiency 9 \
     --verdict accepted --duration-min 12 \
     --learning "Terra reviews TS diffs reliably; missed one async edge case."
   ```

   Verdicts: `accepted`, `accepted_with_edits`, `rejected`, `escalated`,
   `blocked`. Record every attempt; when escalating to a smarter model, log
   the failed attempt too (verdict `escalated`) — never overwrite it.

## Routing rules

- Defaults, not limits: judge the output, not the price tag. If a cheaper
  model's output misses the bar, redo with a smarter model without asking.
- Reasoning effort default is `high` (`medium` for terra/luna routine work).
  `xhigh`/`max` are allowed only after a failed attempt on `high` or with a
  clear stated justification — always logged via `--effort`, so the data
  itself can settle whether they ever pay off.
- Timeouts must never kill a healthy run: plan ~30 min for normal
  delegations, 2h+ for xhigh or long-runners (details in the recipes file).
- Skip logging for trivial lookups (a sub-run finding a file, a one-line
  factual check). Log everything with a real work product.
- If a sub-run finds nothing or fails, that is a result: report it
  clearly, log it, do not silently rerun.
- Claude delegations stay behind the `ask-claude` privacy gate; that skill's
  own `agent-evals` registration continues to apply — log here as well so
  the cross-model scoreboard stays complete.

## Reports

- `node scripts/log_eval.mjs regen` — rebuild SCOREBOARD.md from the log.
- Scoreboard questions ("which model for X?") are answered from
  SCOREBOARD.md, citing n and averages, noting when data is prior-only.
