# Codex Skill Pack

30 skills for OpenAI Codex (CLI, IDE extension, app — e.g. Codex 5.6).

**Structure:** `MattSkills/` (22 skills ported from [mattpocock/skills](https://github.com/mattpocock/skills), license included) and `LutossSkills/` (8 skills: three repaired own skills plus `verify-before-done`, `improve-project-structure`, `project-review`, `agent-evals`, and `ask-claude`).

**Installation:** Copy the skill folders from `MattSkills/` and `LutossSkills/` **flat** (without the group folders) into `$HOME/.agents/skills/` (global) or `<repo>/.agents/skills/` (project-level). Invoke via `$skill-name`, `/skills`, or implicitly via the skill description. Codex picks up changes automatically; otherwise restart Codex.

**Getting started:** Run `$setup-matt-pocock-skills` once in the target repo. Then use `$ask-matt` as the router: the main flow is `grill-with-docs → to-prd → to-issues → implement → code-review`. `$verify-before-done` runs as a discipline underneath everything.

**Pack-specific notes:**

- Claude-specific frontmatter keys removed; skills that are user-invoked only carry an `agents/openai.yaml` with `allow_implicit_invocation: false` instead.
- Skill cross-references use `$name` syntax; subagent instructions are generalized (parallel where available, otherwise sequential with fresh context).
- `review-loop` gets its second opinion from **Claude Code** (`claude -p --model opus --effort max`, see `review-loop/references/claude-protocol.md` and `scripts/invoke-claude-review.ps1`).
- No `git-guardrails-claude-code` (Claude Code hooks; Codex uses its own sandbox/approvals).

MattSkills: ask-matt, code-review, codebase-design, diagnosing-bugs, domain-modeling, grill-me, grill-with-docs, grilling, handoff, implement, improve-codebase-architecture, prototype, research, resolving-merge-conflicts, setup-matt-pocock-skills, setup-pre-commit, tdd, teach, to-issues, to-prd, triage, writing-great-skills.

LutossSkills: agent-evals, ask-claude, implement-issues, improve-project-structure, loop-creator, project-review, review-loop, verify-before-done.
