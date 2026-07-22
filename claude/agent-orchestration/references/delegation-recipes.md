# Delegation recipes

## Codex (gpt-5.6 family) via the CLI

Two transports exist; the **CLI is the default** (the video's original
mechanism):

- **CLI (`codex exec ...` via a shell on the user's machine)** — the
  default for every delegation. The MCP harness enforces a short
  client-side timeout (observed ~1 min) that kills healthy runs at
  normal reasoning effort, so real work goes through the CLI:
  run `codex exec` with output redirected to a file; for anything beyond
  a few minutes start it detached (background/`Start-Process`) in a
  worktree and poll the output file. In Claude Code, shell out via Bash;
  in Cowork the sandbox shell has neither the Codex CLI nor its auth —
  use a desktop shell bridge (e.g. the Windows MCP PowerShell tool)
  instead.
- **MCP (`mcp__codex__codex`)** — only for sub-minute interactions:
  trivial commands, quick follow-ups on an existing thread via
  `mcp__codex__codex-reply`. Never for reviews or implementation at
  medium+ effort; two harness timeouts in a row proved the point
  (see scoreboard entry 2026-07-22).

CLI skeleton (foreground, short run):

    codex exec --model gpt-5.6-terra -c model_reasoning_effort=medium \
      --sandbox read-only "<self-contained prompt>" > out.md 2>&1

Detached (anything that might exceed a shell-call timeout): same command
started in the background with output to a file, then poll the file for
the final report instead of holding one blocking call open.

**CLI gotchas (both verified 2026-07-22):**

- `codex exec` refuses to start outside a trusted git repo ("Not inside
  a trusted directory"). Run it from inside the target repo, or add
  `--skip-git-repo-check` when no repo applies.
- In non-interactive shells it also reads from stdin ("Reading
  additional input from stdin...") and can hang waiting for EOF. Always
  close stdin: `$null | codex exec ...` (PowerShell) or
  `codex exec ... < /dev/null` (bash).

Key config (both transports):

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

These budgets apply to the CLI path; the MCP harness cannot honor them —
another reason MCP is reserved for sub-minute interactions. For anything
expected to exceed a shell-call limit, run it detached (worktree +
background) and poll, rather than holding one blocking call open.

### Prompting Codex

Prompt Codex simply — it is not Claude. State the task, the scope, and the
expected output format in a few plain sentences. It does not need
motivation, personas, or guardrail prose; unlike Claude models it rarely
does things it wasn't asked to do.

The prompt must be **self-contained**: Codex sees nothing of this
conversation. Include the concrete paths, branch names, PR numbers, and
acceptance criteria it needs — never "as discussed above".

For pure investigation/analysis, run it read-only (`sandbox: read-only`,
CLI equivalent `codex exec --read-only`) with a self-contained prompt
instead of setting up a full implementation delegation.

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

### Codex inside Claude subagents/workflows

When a workflow or subagent must use Codex (workflows can only spawn Claude
models directly), wrap it: a cheap Claude subagent (sonnet, low effort)
invokes Codex, waits, and reports the results upward. Prefix such
subagent names with `gpt56-` so it stays visible which workers actually
ran on Codex.

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
