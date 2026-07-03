# Claude Skill Pack

27 Skills für Claude Code / Cowork (Fable 5, Opus 4.8 — gleicher Harness, gleiche Skills).

**Struktur:** `MattSkills/` (23, portiert aus mattpocock/skills, inkl. Lizenz) und `LutossSkills/` (4: deine drei sanierten Skills + der neue `verify-before-done`).

**Installation:** Die Skill-Ordner aus `MattSkills/` und `LutossSkills/` **flach** (ohne die Gruppenordner) nach `~/.claude/skills/` (global) oder `<repo>/.claude/skills/` (projektweit) kopieren — Claude Code erwartet `skills/<skill-name>/SKILL.md` direkt. Aufruf per `/skill-name` oder automatisch über die Description. `disable-model-invocation: true` markiert rein nutzergesteuerte Skills.

**Einstieg:** Einmalig `/setup-matt-pocock-skills` im Zielrepo ausführen. Danach `/ask-matt` als Router: Der Haupt-Flow ist `grill-with-docs → to-prd → to-issues → implement → code-review`. `/verify-before-done` läuft als Disziplin unter allem.

**Besonderheiten dieses Pakets:**

- `code-review` und `improve-codebase-architecture` nutzen native parallele Subagents (Agent-Tool) — Fable 5 und Opus 4.8 profitieren von paralleler Ausführung.
- `review-loop` holt die Zweitmeinung von der **Codex CLI** (`codex exec --sandbox read-only`, siehe `review-loop/references/second-opinion-protocol.md`); Fallback ist ein Subagent mit frischem Kontext.
- `implement-issues` spawnt pro Dependency-Welle einen Worker-Subagent je Issue (alle Agent-Calls in einer Nachricht = parallel).
- `git-guardrails-claude-code` ist nur hier enthalten (PreToolUse-Hooks).

MattSkills: ask-matt, code-review, codebase-design, diagnosing-bugs, domain-modeling, git-guardrails-claude-code, grill-me, grill-with-docs, grilling, handoff, implement, improve-codebase-architecture, prototype, research, resolving-merge-conflicts, setup-matt-pocock-skills, setup-pre-commit, tdd, teach, to-issues, to-prd, triage, writing-great-skills.

LutossSkills: implement-issues, loop-creator, review-loop, verify-before-done.
