# Model Scoreboard

Generated 2026-07-22T21:59:42.156Z from 10 evaluations. Do not edit by hand — regenerate via log_eval.mjs.

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

### image_generation

| model | n | correctness | taste | efficiency | overall | expl | accepted% |
|---|---|---|---|---|---|---|---|
| gpt-5.6-sol | 2 | 7.5 | 8.5 | 5.5 | 7.2 | 0 | 50% |

### planning_architecture

| model | n | correctness | taste | efficiency | overall | expl | accepted% |
|---|---|---|---|---|---|---|---|
| gpt-5.6-terra | 1 | 8.0 | 8.0 | 10.0 | 8.7 | 0 | 100% |

### research_primary_sources

| model | n | correctness | taste | efficiency | overall | expl | accepted% |
|---|---|---|---|---|---|---|---|
| gpt-5.6-terra | 1 | 9.0 | 8.0 | 8.0 | 8.3 | 0 | 100% |
| claude-fable-5 | 4 | 9.0 | 8.3 | 7.5 | 8.3 | 0 | 100% |

## By reasoning effort

| effort | n | overall | accepted% |
|---|---|---|---|
| high | 5 | 7.7 | 80% |
| low | 1 | 8.7 | 100% |
| medium | 4 | 4.8 | 50% |

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

- **gpt-5.6-terra** (planning_architecture, accepted): MCP-Transport mit effort=low blieb unter Harness-Timeout; kompakte Zweitmeinung mit Mehrwert (GitHub Skills statt veraltetem Actions-Video, Branch-Protection/Squash-Hinweise).
- **claude-fable-5** (research_primary_sources, accepted): Subagent (Advanced/Actions): schnell, erkannte veraltete Nana-Actions-Syntax (setup-java, docker-push) korrekt.
- **claude-fable-5** (research_primary_sources, accepted): Subagent (DE-Tutorials): entlarvte '2026'-Titel als 2021-Upload; fixes-#N-Claim per Grep bestätigt. Frames lohnen sich zur UI-Altersprüfung.
- **claude-fable-5** (research_primary_sources, accepted): Subagent (Mosh/fCC2026): erkannte Paid-Course-Funnel und Auto-Caption-Schwäche; Rebase/PR-Claims per Grep bestätigt.
- **claude-fable-5** (research_primary_sources, accepted): Subagent bewertete 2 YT-Tutorials via Transkript+Frames (Stratvert/SuperSimpleDev); Timestamp-Belege stimmten im Stichproben-Grep.
- **gpt-5.6-sol** (image_generation, accepted): codex exec CLI (detached, --skip-git-repo-check, Prompt via stdin wegen PS-5.1-Quoting) + explizite Anweisung 'nur eingebautes Bildgen-Tool, kein Computer Use' lieferte 8 Portraits inkl. NOTES.md fehlerfrei im ersten Anlauf; Referenzfotos je Generierung ergeben starke Aehnlichkeit.
- **gpt-5.6-sol** (image_generation, escalated): MCP-Transport fuer Bildgen-Laeufe ungeeignet: nach Bridge-Timeout verliert codex den Rueckkanal und haengt; ausserdem verlor der Lauf ~1h beim Versuch, ChatGPT/Photoshop per Computer Use zu steuern statt das eingebaute Bildgen-Tool zu nutzen. 2 gute Bilder entstanden trotzdem.
- **gpt-5.6-terra** (code_review, blocked): Codex MCP timed out twice (harness -32001) on a read-only commit review from Cowork sandbox; use detached CLI or longer harness timeout for such runs.
- **gpt-5.6-terra** (research_primary_sources, accepted): Terra fetched+cleaned a YouTube auto-transcript (yt-dlp) and filed it with good header/slug unprompted details. MCP transport hit the 60s bridge cap but the run completed server-side; verify via filesystem instead of rerunning.
- **gpt-5.5** (desktop_config, blocked): Codex-MCP: gpt-5.6-Modelle von installierter Codex-Version abgelehnt (Upgrade noetig); Lauf mit gpt-5.5 starb am MCP-Timeout ohne Output. Thunderbird-Signatur-Konfig danach direkt vom Orchestrator erledigt (prefs.js, 2 Keys). Fuer laengere Codex-Laeufe CLI-detached statt blocking MCP nutzen.
