# Claude Skill Pack

29 skills for Claude Code / Cowork (Fable 5 and Opus 4.8 — same harness, same skills).

**Structure:** `MattSkills/` (23 skills ported from [mattpocock/skills](https://github.com/mattpocock/skills), license included) and `LutossSkills/` (6 skills: three repaired own skills plus the new `verify-before-done`, `improve-project-structure`, `project-review`).

**Installation:** Copy the skill folders from `MattSkills/` and `LutossSkills/` **flat** (without the group folders) into `~/.claude/skills/` (global) or `<repo>/.claude/skills/` (project-level) — Claude Code expects `skills/<skill-name>/SKILL.md` directly. Invoke via `/skill-name` or automatically via the skill description. `disable-model-invocation: true` marks skills that are user-invoked only.

**Getting started:** Run `/setup-matt-pocock-skills` once in the target repo. Then use `/ask-matt` as the router: the main flow is `grill-with-docs → to-prd → to-issues → implement → code-review`. `/verify-before-done` runs as a discipline underneath everything.

**Pack-specific notes:**

- `code-review` and `improve-codebase-architecture` use native parallel subagents (Agent tool) — Fable 5 and Opus 4.8 benefit from parallel execution.
- `review-loop` gets its second opinion from the **Codex CLI** (`codex exec --sandbox read-only`, see `review-loop/references/second-opinion-protocol.md`); the fallback is a subagent with fresh context.
- `implement-issues` spawns one worker subagent per issue per dependency wave (all Agent calls in a single message = parallel).
- `git-guardrails-claude-code` is included only in this pack (PreToolUse hooks).

MattSkills: ask-matt, code-review, codebase-design, diagnosing-bugs, domain-modeling, git-guardrails-claude-code, grill-me, grill-with-docs, grilling, handoff, implement, improve-codebase-architecture, prototype, research, resolving-merge-conflicts, setup-matt-pocock-skills, setup-pre-commit, tdd, teach, to-issues, to-prd, triage, writing-great-skills.

LutossSkills: implement-issues, improve-project-structure, loop-creator, project-review, review-loop, verify-before-done.
