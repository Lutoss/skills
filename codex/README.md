# Codex Skill Pack

9 skills for OpenAI Codex (CLI, IDE extension, app).

**Installation:** Copy the skill folders **flat** into `$HOME/.agents/skills/` (global) or `<repo>/.agents/skills/` (project-level). Or use `../install.sh codex` / `..\install.ps1 codex`. Invoke via `$skill-name`, `/skills`, or implicitly via the skill description. Codex picks up changes automatically; otherwise restart Codex.

**Skills:** `agent-evals`, `agent-orchestration`, `ask-claude`, `implement-issues`, `improve-project-structure`, `loop-creator`, `project-review`, `review-loop`, `verify-before-done`.

**Pack-specific notes:**

- Skill cross-references use `$name` syntax; skills that are user-invoked only carry an `agents/openai.yaml` with `allow_implicit_invocation: false`.
- `review-loop` gets its second opinion from **Claude Code** (`claude -p --model opus --effort max`, see `review-loop/references/claude-protocol.md` and `scripts/invoke-claude-review.ps1`).
- `agent-evals` and `ask-claude` exist only in this pack (they wrap the Claude CLI from the Codex side).
- References to skills from [mattpocock/skills](https://github.com/mattpocock/skills) (`$code-review`, `$tdd`, `$handoff`, ...) are optional handoff recommendations — install that pack separately for the full flow.
