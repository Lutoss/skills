# Delegation recipes (Codex orchestrator)

## gpt-5.6 sub-runs via `codex exec`

Spawn workers as fresh CLI runs so each gets a clean context:

    codex exec --model gpt-5.6-terra -c model_reasoning_effort=medium \
      --sandbox read-only "<self-contained prompt>"

- `--model`: `gpt-5.6-sol` (hard/open-ended, high-value), `gpt-5.6-terra`
  (everyday + read-heavy), `gpt-5.6-luna` (high-volume mechanical). The alias
  `gpt-5.6` routes to sol.
- `model_reasoning_effort`: default `high`; `medium` for terra/luna routine
  work; `xhigh`/`max` only per the escalation rule in SKILL.md.
- `--sandbox`: `read-only` for reviews/analysis, `workspace-write` for
  implementation. Prefer a git worktree for parallel write work.
- For runs that would outlive a blocking call (xhigh, long-runners,
  computer use): start detached in a worktree, write output to a file,
  poll — rather than holding one foreground run open.
- `codex exec` refuses to start outside a trusted git repo; run it from
  inside the target repo or add `--skip-git-repo-check`. In
  non-interactive shells it also reads stdin and can hang waiting for
  EOF — close stdin (`$null | codex exec ...` in PowerShell,
  `codex exec ... < /dev/null` in bash).

### Timeouts

Reasoning effort multiplies per-step time, not step count — budget
accordingly and never let a healthy run die on a timeout:

| Run type | Minimum timeout |
|---|---|
| Read-only review/analysis, medium/high | 30 min |
| Implementation, high | 60 min |
| xhigh/max, computer use, long-runners | 2 h+ |

### Prompting sub-runs

State the task, the scope, and the expected output format in a few plain
sentences. The prompt must be **self-contained**: the sub-run sees nothing
of this conversation. Include the concrete paths, branch names, PR numbers,
and acceptance criteria it needs — never "as discussed above".

Always include: "If you find nothing, say so clearly and name what you
inspected." (Prevents the orchestrator from misreading an empty result and
rerunning.)

Ask for a structured report back (findings, files touched, verification
performed, open questions) so verification and scoring are cheap.

### Strengths to exploit per model

- luna/terra: token-heavy grunt work — log digging, giant PDFs/specs, bulk
  analysis, mechanical migrations.
- sol: architecture, ambiguous implementation, hard debugging.
- Any model, read-only: independent second-opinion reviews of plans and
  diffs.

## Gemini via the Antigravity CLI (`agy`)

Google's consumer subscriptions (AI Pro/Ultra) stopped covering the old
Gemini CLI on 2026-06-18; the **Antigravity CLI (`agy`)** is the official
successor and is covered by those subscriptions. Auth is a one-time
interactive OAuth login (run `agy`, browser flow) done by the user —
headless mode only uses cached credentials and exits non-zero otherwise.
Missing credentials are a "ask the user to log in" situation, not a dead
end.

Skeleton (print mode, JSON envelope):

    agy -p "<self-contained prompt>" --output-format json \
      --model gemini-3.1-pro-high --print-timeout 30m

- **Always pin `--model`** — without it Antigravity routes on its own.
  `agy models` lists current slugs; pattern `<model>-<effort>`:
  `gemini-3.1-pro-high` for reviews/second opinions,
  `gemini-3.5-flash-*` for cheap bulk work.
- `--print-timeout` needs a duration unit (`120s`, `30m`); default is 5m.
  Budget timeouts like the table above.
- JSON envelope: `status` (`SUCCESS`/`ERROR`), `response`, `usage`,
  `conversation_id` (resume via `--conversation`); enforce structured
  output with `--json-schema`.
- Headless soft-denies shell commands by default — ideal for text-only
  second opinions. Grant tools via permission rules if needed, not via
  `--dangerously-skip-permissions`.
- Subscription quota is workload-based (rolling refresh + weekly cap):
  fine for second opinions and reviews, unpredictable for bulk runs.
- Log evals with `--model gemini-3.1-pro` (effort separately via
  `--effort`) so Gemini runs land on the scoreboard like everyone else.

## Kimi K3 via OpenRouter (OpenAI-compatible API)

Moonshot's Kimi K3 (1M context, always-thinking) is reachable as a plain
OpenAI-compatible chat call — no CLI needed:

    POST https://openrouter.ai/api/v1/chat/completions
    Authorization: Bearer <key>      # from a local secrets file/env var
    { "model": "moonshotai/kimi-k3", "messages": [...] }

- **The key never appears in output, prompts, or commits.** Read it from
  the local secrets store (e.g. `OPENROUTER_API_KEY`) at call time.
- K3 always reasons; completions include thinking tokens — budget
  `max_tokens` generously (2000+ even for short answers).
- OpenRouter fans out across providers; for tool-heavy jobs prefer the
  Exacto routing variant (higher tool-calling fidelity). A first-party
  key on platform.moonshot.ai (`https://api.moonshot.ai/v1`, model
  `kimi-k3`) adds automatic prompt caching — cheaper for repeated long
  contexts.
- Best fit: independent second opinions from a non-Anthropic/non-OpenAI
  lineage, and huge-context reads (1M window).
- Log evals with `--model kimi-k3` so K3 runs land on the scoreboard
  like everyone else.

## Claude via the `ask-claude` skill

Use `$ask-claude` for cross-model second opinions and independent reviews —
it wraps the locally authenticated Claude Code CLI read-only, enforces the
privacy gate, and registers the run in Agent Evals. Model choice per the
scoreboard; cold-start default is opus with high effort for review/taste
work, sonnet for bounded mid-tier questions.

Claude runs are read-only in this setup: never delegate writes, commits,
messages, merges, or deployment to Claude.

## Escalation ladder

1. Attempt on the scoreboard-best model at default effort.
2. Output misses the bar → redo on the next-smarter model (or same model,
   `xhigh`) without asking; log the failed attempt as `escalated`.
3. Two failures on a task usually mean the task is underspecified or the
   architecture fights it — stop delegating, tell the user what you saw
   (time-to-solve is a code-health signal: minutes = fine, an hour+ =
   something structural is wrong).
