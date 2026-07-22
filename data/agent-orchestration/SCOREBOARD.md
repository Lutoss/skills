# Model Scoreboard

Generated 2026-07-22T11:40:53.719Z from 3 evaluations. Do not edit by hand — regenerate via log_eval.mjs.

Rows with n >= 5 are trustworthy for routing; below that, treat as cold-start and consult the priors.

## By task kind

### code_review

| model | n | correctness | taste | efficiency | overall | expl | accepted% |
|---|---|---|---|---|---|---|---|
| gpt-5.6-terra | 1 | 1.0 | 1.0 | 1.0 | 1.0 | 0 | 0% |

### desktop_config

| model | n | correctness | taste | efficiency | overall | expl | accepted% |
|---|---|---|---|---|---|---|---|
| gpt-5.5 | 1 | 1.0 | 1.0 | 1.0 | 1.0 | 0 | 0% |

### research_primary_sources

| model | n | correctness | taste | efficiency | overall | expl | accepted% |
|---|---|---|---|---|---|---|---|
| gpt-5.6-terra | 1 | 9.0 | 8.0 | 8.0 | 8.3 | 0 | 100% |

## By reasoning effort

| effort | n | overall | accepted% |
|---|---|---|---|
| medium | 3 | 3.4 | 33% |

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

- **gpt-5.6-terra** (code_review, blocked): Codex MCP timed out twice (harness -32001) on a read-only commit review from Cowork sandbox; use detached CLI or longer harness timeout for such runs.
- **gpt-5.6-terra** (research_primary_sources, accepted): Terra fetched+cleaned a YouTube auto-transcript (yt-dlp) and filed it with good header/slug unprompted details. MCP transport hit the 60s bridge cap but the run completed server-side; verify via filesystem instead of rerunning.
- **gpt-5.5** (desktop_config, blocked): Codex-MCP: gpt-5.6-Modelle von installierter Codex-Version abgelehnt (Upgrade noetig); Lauf mit gpt-5.5 starb am MCP-Timeout ohne Output. Thunderbird-Signatur-Konfig danach direkt vom Orchestrator erledigt (prefs.js, 2 Keys). Fuer laengere Codex-Laeufe CLI-detached statt blocking MCP nutzen.
