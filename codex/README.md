# Codex Skill Pack

28 Skills für OpenAI Codex (CLI, IDE-Extension, App — z. B. Codex 5.5).

**Struktur:** `MattSkills/` (22, portiert aus mattpocock/skills, inkl. Lizenz) und `LutossSkills/` (6: deine drei sanierten Skills + die neuen `verify-before-done`, `improve-project-structure`, `project-review`).

**Installation:** Die Skill-Ordner aus `MattSkills/` und `LutossSkills/` **flach** (ohne die Gruppenordner) nach `$HOME/.agents/skills/` (global) oder `<repo>/.agents/skills/` (projektweit) kopieren. Aufruf per `$skill-name`, `/skills`, oder implizit über die Description. Codex erkennt Änderungen automatisch; sonst Codex neu starten.

**Einstieg:** Einmalig `$setup-matt-pocock-skills` im Zielrepo ausführen. Danach `$ask-matt` als Router: Der Haupt-Flow ist `grill-with-docs → to-prd → to-issues → implement → code-review`. `$verify-before-done` läuft als Disziplin unter allem.

**Besonderheiten dieses Pakets:**

- Claude-spezifische Frontmatter-Schlüssel entfernt; rein nutzergesteuerte Skills tragen stattdessen `agents/openai.yaml` mit `allow_implicit_invocation: false`.
- Skill-Querverweise in `$name`-Syntax; Subagent-Anweisungen generalisiert (parallel wenn verfügbar, sonst sequenziell mit frischem Kontext).
- `review-loop` holt die Zweitmeinung von **Claude Code** (`claude -p --model opus --effort max`, siehe `review-loop/references/claude-protocol.md` und `scripts/invoke-claude-review.ps1`).
- Kein `git-guardrails-claude-code` (Claude-Code-Hooks; Codex nutzt eigene Sandbox/Approvals).

MattSkills: ask-matt, code-review, codebase-design, diagnosing-bugs, domain-modeling, grill-me, grill-with-docs, grilling, handoff, implement, improve-codebase-architecture, prototype, research, resolving-merge-conflicts, setup-matt-pocock-skills, setup-pre-commit, tdd, teach, to-issues, to-prd, triage, writing-great-skills.

LutossSkills: implement-issues, improve-project-structure, loop-creator, project-review, review-loop, verify-before-done.
