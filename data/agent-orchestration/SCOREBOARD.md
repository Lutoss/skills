# Model Scoreboard

Generated 2026-07-18T19:21:59.426Z from 0 evaluations. Do not edit by hand — regenerate via log_eval.mjs.

Rows with n >= 5 are trustworthy for routing; below that, treat as cold-start and consult the priors.

## By task kind

_No evaluated runs yet._

## By reasoning effort

| effort | n | overall | accepted% |
|---|---|---|---|

## Priors (cold-start defaults, source: video + research doc)

| model | intelligence | taste | cost-friendliness | note |
|---|---|---|---|---|
| gpt-5.6-sol | 9 | 6 | 8 | Hard, open-ended, high-value tasks. Alias gpt-5.6 routes here. Codex sub usage is near-free. |
| gpt-5.6-terra | 7 | 5 | 9 | Everyday work, read-heavy subagents (exploration, triage, summarization). |
| gpt-5.6-luna | 5 | 4 | 10 | Clear, repeatable high-volume tasks: log digging, bulk analysis, mechanical migrations. |
| fable-5 | 9 | 9 | 2 | Orchestrator. Best-in-class intelligence and taste; use for steering, reviews, user-facing output. |
| opus-4.8 | 7 | 8 | 4 | Reviews and second passes; often cheaper than token-hungry sonnet-5 in practice. |
| sonnet-5 | 5 | 7 | 5 | Mid-tier bounded subagent work; token-hungry. |
| haiku-4.5 | 2 | 3 | 9 | Avoid for real work (video: never use haiku, especially with Codex near-free). |

## Recent learnings

_None yet._
