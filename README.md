# Lutoss Skills

Personal skills for Claude Code and OpenAI Codex in the open
[SKILL.md](https://agentskills.io) format. This repository contains only skills
maintained as part of this collection; third-party skill ports are not bundled.

## Skills

| Skill | Claude | Codex | Purpose |
|---|:---:|:---:|---|
| `implement-issues` | yes | yes | Implement approved local Markdown issues in dependency-aware waves. |
| `improve-project-structure` | yes | yes | Review and safely reorganize project folders. |
| `loop-creator` | yes | yes | Turn a recurring workflow into a concrete loop contract. |
| `project-review` | yes | yes | Review non-code deliverables against standards and the original brief. |
| `review-loop` | yes | yes | Review, fix, verify, and repeat until acceptance or a human gate. |
| `verify-before-done` | yes | yes | Require fresh evidence before reporting completion. |
| `agent-evals` | - | yes | Evaluate agent runs and learn routing preferences locally. |
| `agent-orchestration` | yes | - | Route delegations to the best model and maintain a self-learned scoreboard (replaces delegate-to-codex). |
| `ask-claude` | - | yes | Request a bounded, read-only Claude second opinion. |

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

The scripts install only direct child directories that contain a `SKILL.md`.
Existing skills with the same name are replaced. Other installed skills are
left untouched.

For manual installation, copy the desired skill directories from `claude/` or
`codex/` into the matching user- or project-level skills directory.

## License

MIT - see [LICENSE](LICENSE).
