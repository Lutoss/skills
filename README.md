# Skill-Packs: Claude & Codex

Zwei einsatzfertige Skill-Pakete, erstellt am 2026-07-03 aus zwei Quellen:

1. **[mattpocock/skills](https://github.com/mattpocock/skills)** (Stand: Commit vom 2026-07-02, MIT-Lizenz) — die 21 aktiven Skills aus `engineering/` und `productivity/` plus `setup-pre-commit` und `git-guardrails-claude-code`
2. **Eigene Skills** aus diesem Projektordner — `implement-issues`, `loop-creator`, `review-loop` (repariert und pro Paket angepasst; `brainstorming` wurde nach Flow-Review bewusst nicht übernommen, da `grill-with-docs` als Design-Einstieg genügt)

Dazu **drei neue Skills** (`verify-before-done`, `improve-project-structure`, `project-review`).

## Warum 2 Pakete statt 3 (Fable 5 / Opus 4.8 / Codex 5.5)?

Skills sind Prozess-Anweisungen im offenen SKILL.md-Standard ([agentskills.io](https://agentskills.io)). Die relevanten Unterschiede liegen im **Harness** (Claude Code vs. Codex CLI: Subagent-Aufrufe, Frontmatter-Felder, `/skill`- vs. `$skill`-Syntax, Installationspfade), nicht im Modell. Fable 5 und Opus 4.8 nutzen denselben Harness und damit identische Skills — ein drittes Paket wäre reine Duplikation, die bei jeder Änderung doppelt gepflegt werden müsste.

Modellspezifisch ist nur die Reviewer-Wahl in `review-loop`: Das Codex-Paket ruft Claude Code (Opus 4.8 oder neuer, `--effort max`) als Zweitmeinung auf, das Claude-Paket umgekehrt die Codex CLI.

## Review-Befunde (Kurzfassung)

**mattpocock/skills:** Hohe Qualität, bewusst modellagnostisch, für Fable 5 fast 1:1 geeignet. Angepasst wurde nur: Claude-Code-spezifische Subagent-Aufrufe (`Agent`-Tool, `subagent_type=Explore` in `code-review`, `improve-codebase-architecture`, `codebase-design`) für Codex generalisiert; `disable-model-invocation`/`argument-hint`-Frontmatter (Codex ignoriert beides) für Codex entfernt und durch `agents/openai.yaml` mit `allow_implicit_invocation: false` ersetzt; Skill-Verweise für Codex auf `$name`-Syntax umgestellt.

**Eigene 4 Skills:** Gut konstruiert, aber mit Defekten, die in beiden Paketen behoben wurden:

| Skill | Befund | Fix |
|---|---|---|
| implement-issues | Hartkodiertes `$env:CODEX_HOME` (veraltet), nur PowerShell | Claude: Skill-Ordner-Pfad + parallele Task-Tool-Worker; Codex: offizieller Pfad `$HOME/.agents/skills/` + Bash/PowerShell |
| loop-creator | 8+ hängende Referenzen (`privacy-gate-loop`, `tdd-slice`, `review-slice`, `docs/loop-contract.md`, `lutoss-skills` …) | Auf real vorhandene Skills gemappt; Privacy-Gate inline; Template inline |
| review-loop | Hängende Referenzen (`review-slice`, `tdd-slice`, `slice-pr-loop`, `diagnose`, `second-opinion-review-loop`); harte Pinnung auf „Opus 4.8 Max" | Referenzen gemappt; Modellwahl auf „stärkstes verfügbares Modell" verallgemeinert; Claude-Variante invertiert (Codex CLI als Zweitmeinung, `references/second-opinion-protocol.md`) |

## Neue Skills

- **verify-before-done** — Abschluss-Disziplin: keine „Fertig"-Meldung ohne frischen Beleg aus einem Check, der auch hätte fehlschlagen können. Der größte einzelne Qualitätshebel für Agentenarbeit, modellunabhängig.
- **improve-project-structure** — scannt einen Projektordner auf strukturelle Reibung, präsentiert Reorganisations-Vorschläge als visuellen HTML-Report und setzt den gewählten um. Das Ordner-Pendant zu `improve-codebase-architecture`.
- **project-review** — Zwei-Achsen-Review (Standards / ursprünglicher Auftrag) für fertige Nicht-Code-Ergebnisse: Dokumente, Präsentationen, Tabellen, Pläne. Das Pendant zu `code-review`, mit parallelen Sub-Reviews.

## Nicht übernommen

`in-progress/` (7 Skills, explizit unfertig), `deprecated/` (4), `personal/` (Matts private Skills: `edit-article`, `obsidian-vault`), `misc/migrate-to-shoehorn` und `misc/scaffold-exercises` (Matts Kurs-Tooling). `git-guardrails-claude-code` nur im Claude-Paket (Claude-Code-Hooks; Codex bringt eigene Sandbox/Approvals mit).

## Installation

**Claude** (Claude Code / Cowork): Skill-Ordner aus `claude/MattSkills/` und `claude/LutossSkills/` **flach** nach `~/.claude/skills/` (global) oder `<repo>/.claude/skills/` (projektweit) kopieren. In Cowork: Settings → Capabilities.

**Codex** (CLI / IDE / App): Skill-Ordner aus `codex/MattSkills/` und `codex/LutossSkills/` **flach** nach `$HOME/.agents/skills/` (global) oder `<repo>/.agents/skills/` (projektweit) kopieren. Aufruf per `$skill-name` oder implizit.

**Flach** heißt: Im Ziel liegt `skills/<skill-name>/SKILL.md` direkt — die Gruppenordner `MattSkills/`/`LutossSkills/` selbst werden nicht mitkopiert. Die Datei `LICENSE-mattpocock-skills` muss nicht mit (stört im Ziel aber auch nicht).

**Erster Schritt in beiden Paketen:** `setup-matt-pocock-skills` ausführen (konfiguriert Issue-Tracker, Triage-Labels, Doku-Layout). Der Router `ask-matt` erklärt, welcher Skill wann passt — inklusive der lokalen Ergänzungen.

## Lizenz

Portierte Skills: MIT (siehe `LICENSE-mattpocock-skills` in jedem Paket, © Matt Pocock). Eigene und neue Skills: dein Projekt.
