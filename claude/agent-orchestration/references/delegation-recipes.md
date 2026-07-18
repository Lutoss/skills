# Delegation recipes

## Codex (gpt-5.6 family) via the `codex` MCP

Call `mcp__codex__codex` (follow-ups: `mcp__codex__codex-reply` with the same
conversation ID). Key config:

- `model`: `gpt-5.6-sol` (hard/open-ended, high-value), `gpt-5.6-terra`
  (everyday + read-heavy), `gpt-5.6-luna` (high-volume mechanical). The alias
  `gpt-5.6` routes to sol.
- `model_reasoning_effort`: default `high`; `medium` for terra/luna routine
  work; `xhigh`/`max` only per the escalation rule in SKILL.md.
- `sandbox`: `read-only` for reviews/analysis, `workspace-write` for
  implementation. Prefer a git worktree for parallel write work.

### Timeouts

Reasoning effort multiplies per-step time, not step count — budget
accordingly and never let a healthy run die on a timeout:

| Run type | Minimum timeout |
|---|---|
| Read-only review/analysis, medium/high | 30 min |
| Implementation, high | 60 min |
| xhigh/max, computer use, long-runners | 2 h+ |

For anything expected to exceed the harness limit, run it detached (worktree
+ background) and poll, rather than holding one blocking call open.

### Prompting Codex

Prompt Codex simply — it is not Claude. State the task, the scope, and the
expected output format in a few plain sentences. It does not need
motivation, personas, or guardrail prose; unlike Claude models it rarely
does things it wasn't asked to do.

Always include: "If you find nothing, say so clearly and name what you
inspected." (Prevents the orchestrator from misreading an empty result and
rerunning.)

Ask for a structured report back (findings, files touched, verification
performed, open questions) so verification and scoring are cheap.

### Strengths to exploit

- Token-heavy grunt work: log digging, giant PDFs/specs, bulk analysis —
  Codex sub usage is extremely generous, treat it as near-free.
- Computer use / runtime verification: Codex desktop-class computer use is
  currently far ahead; delegate "test this flow, capture screenshots,
  report actual behavior" tasks there.
- Independent second-opinion reviews of plans and diffs.

## Claude subagents (Agent tool)

- Fan-out reads, codebase exploration, parallel per-file analysis: `Explore`
  or `general-purpose` agents; run independent agents concurrently in one
  block.
- Model choice per scoreboard; video-era priors: opus for reviews/taste,
  sonnet for mid-tier bounded work, avoid haiku for real work.
- Invent the archetype per task (reviewer, adversarial reviewer, verifier)
  in the prompt instead of maintaining fixed agent definitions.
- Give each subagent: bounded scope, expected return format, and the
  instruction to report uncertainty rather than paper over it.

## Escalation ladder

1. Attempt on the scoreboard-best model at default effort.
2. Output misses the bar → redo on the next-smarter model (or same model,
   `xhigh`) without asking; log the failed attempt as `escalated`.
3. Two failures on a task usually mean the task is underspecified or the
   architecture fights it — stop delegating, tell the user what you saw
   (time-to-solve is a code-health signal: minutes = fine, an hour+ =
   something structural is wrong).
