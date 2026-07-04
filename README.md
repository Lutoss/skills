# Skill Packs: Claude & Codex

Two ready-to-install skill packs in the open [SKILL.md](https://agentskills.io) format:

- **`claude/`** — 29 skills for Claude Code / Cowork
- **`codex/`** — 28 skills for OpenAI Codex (CLI, IDE extension, app)

Most skills are ported from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT) and partially reworked; the rest are our own repaired or newly written skills.

## Installation

### Quick install (scripts)

Both scripts take a pack (`claude` or `codex`) and an optional scope (`global`, the default, or `project` with an optional target directory).

Bash:

```sh
./install.sh claude                       # global: $HOME/.claude/skills
./install.sh codex                        # global: $HOME/.agents/skills
./install.sh claude project               # project: ./.claude/skills
./install.sh codex project /path/to/repo  # project: /path/to/repo/.agents/skills
```

PowerShell:

```powershell
.\install.ps1 claude                        # global: $HOME\.claude\skills
.\install.ps1 codex                         # global: $HOME\.agents\skills
.\install.ps1 claude project                # project: .\.claude\skills
.\install.ps1 codex project C:\path\to\repo # project: C:\path\to\repo\.agents\skills
```

### Manual install

Copy the skill folders from `<pack>/MattSkills/` and `<pack>/LutossSkills/` **flat** into the destination — without the `MattSkills/`/`LutossSkills/` group folders. The destination must contain `skills/<skill-name>/SKILL.md` directly. Skip the loose files (`LICENSE-mattpocock-skills`, `README.md`); they do no harm at the destination but are not needed.

| Pack | Global | Project |
|---|---|---|
| claude | `~/.claude/skills/` | `<repo>/.claude/skills/` |
| codex | `$HOME/.agents/skills/` | `<repo>/.agents/skills/` |

### First step after installing

Run `setup-matt-pocock-skills` once in the target repo (configures issue tracker, triage labels, docs layout). Use `ask-matt` as the router — it explains which skill fits when, including the local additions.

## Attribution

Most skills in both packs were copied from [mattpocock/skills](https://github.com/mattpocock/skills) by Matt Pocock (MIT license, snapshot from 2026-07-02) and partially reworked. See `LICENSE-mattpocock-skills` in each pack's `MattSkills/` folder.

## What we changed and why

**Codex pack** — adapted to the Codex harness: Claude-specific frontmatter keys (`disable-model-invocation`, `argument-hint`) removed; skill cross-references switched to `$name` syntax; user-invoked skills carry an `agents/openai.yaml` with `allow_implicit_invocation: false`; Claude-specific subagent instructions generalized (parallel where available, otherwise sequential with fresh context); `review-loop` gets its second opinion from the Claude Code CLI.

**Claude pack** — stays close to upstream by design; deviations are limited to dangling-reference and issue-flow interop fixes, each documented in [CHANGES.md](CHANGES.md). `review-loop` is inverted to get its second opinion from the Codex CLI.

**Own skills repaired** (in both packs): `implement-issues` (hardcoded, outdated `$env:CODEX_HOME` path; PowerShell-only), `loop-creator` (8+ dangling references to non-existent skills and files), `review-loop` (dangling references; hard pin to one specific reviewer model, now generalized).

**Three new skills:**

- `verify-before-done` — no "done" report without fresh evidence from a check that could have failed; the single biggest quality lever for agent work.
- `improve-project-structure` — scans a project folder for structural friction, presents reorganization proposals as a visual HTML report, and applies the chosen one; the folder counterpart to `improve-codebase-architecture`.
- `project-review` — two-axis review (project standards / original brief) for finished non-code deliverables (documents, presentations, spreadsheets, plans); the counterpart to `code-review`.

Full changelog (German): [CHANGES.md](CHANGES.md).

## Repository structure

```
skill-packs/
├── claude/               # 29 skills for Claude Code / Cowork
│   ├── MattSkills/       # 23 ported skills + LICENSE-mattpocock-skills
│   └── LutossSkills/     # 6 own skills
├── codex/                # 28 skills for OpenAI Codex
│   ├── MattSkills/       # 22 ported skills + LICENSE-mattpocock-skills
│   └── LutossSkills/     # 6 own skills
├── install.sh            # installer (bash)
├── install.ps1           # installer (PowerShell)
├── CHANGES.md            # detailed changelog (German)
└── LICENSE
```

## License

MIT — see [LICENSE](LICENSE). Skills under `*/MattSkills/` are © Matt Pocock ([mattpocock/skills](https://github.com/mattpocock/skills), MIT; see `LICENSE-mattpocock-skills` in each pack).
