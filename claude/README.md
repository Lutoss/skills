# Claude Skill Pack

8 skills for Claude Code / Cowork.

**Installation:** Copy the skill folders **flat** into `~/.claude/skills/` (global) or `<repo>/.claude/skills/` (project-level) — Claude Code expects `skills/<skill-name>/SKILL.md` directly. Or use `../install.sh claude` / `..\install.ps1 claude`. Invoke via `/skill-name` or automatically via the skill description; `disable-model-invocation: true` marks skills that are user-invoked only.

**Skills:** `agent-orchestration`, `implement-issues`, `improve-project-structure`, `loop-creator`, `project-review`, `review-loop`, `verify-before-done`, `youtube-transcript`.

**Pack-specific notes:**

- `agent-orchestration` keeps a cross-model scoreboard; its data directory is machine-local (see the skill's first-use note), not hardcoded in the repo.
- `review-loop` gets its second opinion from the **Codex CLI** (`codex exec --sandbox read-only`, see `review-loop/references/second-opinion-protocol.md`); the fallback is a subagent with fresh context.
- `implement-issues` spawns one worker subagent per issue per dependency wave (all Agent calls in a single message = parallel).
- `youtube-transcript` needs Python 3 plus `ffmpeg` on PATH for the optional frame cards; `yt-dlp` and Pillow are auto-installed by the bundled scripts.
- References to skills from [mattpocock/skills](https://github.com/mattpocock/skills) (`/code-review`, `/tdd`, `/handoff`, ...) are optional handoff recommendations — install that pack separately for the full flow.
