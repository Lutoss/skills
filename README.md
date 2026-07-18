# Lutoss Skills

Own agent skills in the open [SKILL.md](https://agentskills.io) format, as two ready-to-install packs:

- **`claude/`** — 6 skills for Claude Code / Cowork
- **`codex/`** — 8 skills for OpenAI Codex (CLI, IDE extension, app)

## Skills

| Skill | claude | codex | Purpose |
|---|:-:|:-:|---|
| `verify-before-done` | ✓ | ✓ | No "done" report without fresh evidence from a check that could have failed — the single biggest quality lever for agent work. |
| `review-loop` | ✓ | ✓ | Iterative review loop with an external second opinion: the Claude pack asks the Codex CLI, the Codex pack asks Claude Code (inverted roles by design). |
| `implement-issues` | ✓ | ✓ | Works through ready issues in dependency waves, one worker per issue, with review handoff. |
| `loop-creator` | ✓ | ✓ | Designs new agent loops (steps, gates, output contract) from a goal description. |
| `project-review` | ✓ | ✓ | Two-axis review (project standards / original brief) for finished non-code deliverables — documents, presentations, spreadsheets, plans. |
| `improve-project-structure` | ✓ | ✓ | Scans a project folder for structural friction, presents reorganization proposals as a visual HTML report, and applies the chosen one. |
| `agent-evals` | — | ✓ | Records verified native and external agent runs in a private SQLite store and recommends models by task after enough comparable evidence. |
| `ask-claude` | — | ✓ | Invokes a locally authenticated Claude Code CLI as a bounded read-only second-opinion agent and feeds the verified result into `agent-evals`. |

The Claude pack contains 7 skills. The Codex pack contains 8 skills.

## Repository structure

```text
skill-packs/
├── claude/
│   ├── README.md
│   └── <skill>/SKILL.md
├── codex/
│   ├── README.md
│   └── <skill>/SKILL.md
├── install.sh
├── install.ps1
├── CHANGES.md
└── LICENSE
```

Skill directories live directly below their platform folder. There are no
author or origin grouping directories.

## Installation

Both installers take a platform (`claude` or `codex`) and an optional scope
(`global`, the default, or `project` with an optional target directory).

```sh
./install.sh claude
./install.sh codex
./install.sh claude project
./install.sh codex project /path/to/repo
```

```powershell
.\install.ps1 claude
.\install.ps1 codex
.\install.ps1 claude project
.\install.ps1 codex project C:\path\to\repo
```

### Manual install

Copy the skill folders from `<pack>/` into the destination so that it contains `skills/<skill-name>/SKILL.md` directly. Skip the loose `README.md`.

| Pack | Global | Project |
|---|---|---|
| claude | `~/.claude/skills/` | `<repo>/.claude/skills/` |
| codex | `$HOME/.agents/skills/` | `<repo>/.agents/skills/` |

## Optional companion: mattpocock/skills

Several skills reference skills from [mattpocock/skills](https://github.com/mattpocock/skills) (`code-review`, `tdd`, `handoff`, `to-issues`, `grill-*`, `implement`, `diagnosing-bugs`) as recommended handoff targets. These references are **optional**: each skill works standalone and treats a missing target as "recommend to the user" rather than "invoke". For the full flow, install mattpocock/skills separately alongside this pack.

## Why two packs?

The packs are deliberately maintained as two full copies rather than a single source with build tooling:

- **Different invocation mechanics.** Claude uses `/name` references and frontmatter keys like `disable-model-invocation`; Codex uses `$name` references and `agents/openai.yaml` with `allow_implicit_invocation: false`.
- **Inverted second opinions.** `review-loop` in the Claude pack consults the Codex CLI; in the Codex pack it consults Claude Code — including different protocols and scripts.
- **Pack-only skills.** `agent-evals` and `ask-claude` exist only on the Codex side.
- **No build step.** Each pack is directly copyable; the duplication cost (four skills with small diffs) is accepted in exchange for zero tooling.

## Repository structure

```
skills/
├── claude/               # 6 skills for Claude Code / Cowork
│   └── <skill-name>/SKILL.md (+ references/, scripts/)
├── codex/                # 8 skills for OpenAI Codex
│   └── <skill-name>/SKILL.md (+ references/, scripts/, agents/openai.yaml)
├── install.sh            # installer (bash)
├── install.ps1           # installer (PowerShell)
├── CHANGES.md            # changelog (German)
└── LICENSE
```

## License

MIT — see [LICENSE](LICENSE).
