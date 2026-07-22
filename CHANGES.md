*Detailed changelog (German). See [README.md](README.md) for the English summary.*

# CHANGES — Was geändert wurde und warum

## 2026-07-22 — Portables agent-orchestration + Codex-Port

- **Privaten Pfad entfernt:** `claude/agent-orchestration` enthielt den hartkodierten lokalen Repo-Pfad. `scripts/data-dir.txt` ist jetzt untracked und in `.gitignore`; `SKILL.md` dokumentiert stattdessen die Auflösungskette (`--data-dir` > `AGENT_ORCH_DATA` > `data-dir.txt` > `~/.agent-orchestration`) plus Ersteinrichtungs-Hinweis — der Agent fragt beim ersten Einsatz, statt einen fremden Pfad zu erben.
- **Codex-Transport auf CLI umgestellt:** Der MCP-Connector bricht gesunde Runs nach ~1 min Harness-Timeout ab (zweimal reproduziert, im Scoreboard geloggt). `codex exec` über die Shell (Claude Code: Bash; Cowork: Desktop-Shell-Bridge) ist jetzt Default — Output in Datei, lange Runs detached + Polling; MCP nur noch für Sub-Minuten-Interaktionen.
- **Codex-Port ergänzt:** `codex/agent-orchestration/` mit gleichem Scoreboard-Tooling (`log_eval.mjs`), Delegations-Rezepten für `codex exec`-Sub-Runs und `ask-claude`, plus `agents/openai.yaml`. Beide Packs können über `data-dir.txt`/`AGENT_ORCH_DATA` dasselbe Scoreboard teilen.

## 2026-07-18 — Aufräumen: nur noch eigene Skills

- **MattSkills komplett entfernt** (beide Pakete, inkl. `LICENSE-mattpocock-skills`). Wer den vollen Flow will, installiert [mattpocock/skills](https://github.com/mattpocock/skills) separat — die Referenzen in den eigenen Skills (`/code-review`, `$tdd`, `handoff`, ...) bleiben als optionale Handoff-Empfehlungen bestehen und degradieren sauber, wenn das Ziel fehlt.
- **Struktur geflattet:** `claude/LutossSkills/<skill>` → `claude/<skill>`, analog für `codex/`. Die Gruppenordner-Ebene ist weg.
- **Install-Scripts** (`install.sh`, `install.ps1`) an die flache Struktur angepasst; Hinweis auf `setup-matt-pocock-skills`/`ask-matt` durch Hinweis auf das optionale Companion-Repo ersetzt.
- **Claude/Codex-Trennung geprüft und beibehalten:** reale Unterschiede (Invocation-Syntax `/name` vs. `$name`, Frontmatter vs. `openai.yaml`, invertierter `review-loop`, zwei Codex-only-Skills). Entscheidung und Begründung jetzt im README dokumentiert („Why two packs?").
- READMEs (Root + Packs) neu geschrieben; Attribution-Abschnitte entfernt.


Stand: 2026-07-10, nach Ergänzung des lernenden Subagent-Routings und der read-only Claude-Code-Brücke.

## 0. Entfernt nach Flow-Diskussion

**brainstorming** und **writing-plans** wurden zunächst portiert/erstellt, repariert, reviewt und getestet (beide Tests bestanden) — dann aber auf deine Entscheidung hin **aus beiden Paketen entfernt**: brainstorming überlappt als Design-Interview mit `grill-with-docs` (Weg A ist dein Standard-Flow), und writing-plans existierte primär als brainstorming-Kettenglied. Der Design-Einstieg ist jetzt einheitlich `grill-with-docs` (bzw. `grill-me` ohne Codebase). Deine Original-Ordner im Projektroot sind unangetastet.

## 1. Gegenüber deinen Original-Skills (implement-issues, loop-creator, review-loop)

### implement-issues
**Befunde:** Hartkodiertes `$env:CODEX_HOME` (von Codex inzwischen abgelöst), nur PowerShell, Codex-Wording.
**Fixes:** Claude-Variante: Skill-Ordner-Pfad (`~/.claude/skills/...`), Worker-Wellen explizit über parallele Agent-Tool-Aufrufe „in einer Nachricht", Review-Handoff an `/code-review`//`/review-loop`. Codex-Variante: offizieller Pfad `$HOME/.agents/skills/` + Bash- und PowerShell-Beispiele. Scripts und PROMPT.md unverändert (nur `tdd`-Verweis auf `/tdd` bzw. `$tdd` — Review-Fund).

### loop-creator
**Befunde:** 9 hängende Referenzen (`privacy-gate-loop`, `context-brief-loop`, `tdd-slice`, `review-slice`, `project-hub-loop`, `github-ready-loop`, `second-opinion-review-loop`, `slice-pr-loop`, `docs/loop-contract.md`) sowie `lutoss-skills`-Bezug; Output-Template verlangte „Budget/iteration limit", das kein Schritt erhebt.
**Fixes:** Alle Subloops auf real installierte Skills gemappt (`handoff`, `diagnosing-bugs`, `tdd`, `code-review`, `review-loop`, `implement`, `to-issues`); Privacy-Gate inline formuliert; Template-Verweis auf den eingebauten Output-Block; „budget/iteration limit" in die Entscheidungsliste aufgenommen (Review-Fund).

### review-loop
**Befunde:** Gleiche hängende Referenzen wie loop-creator; harte Pinnung auf „Opus 4.8 Max"; Rollenverteilung nur für Codex-als-Orchestrator gedacht.
**Fixes (beide):** Referenzen gemappt; Modellwahl generalisiert („stärkstes verfügbares Modell, `--effort max`"); Beschreibung mit Triggern vorn (Codex kürzt lange Descriptions — Review-Fund); Routen zu nutzer-invozierten Skills (`implement`, `improve-codebase-architecture`) als Empfehlung statt Auto-Aufruf formuliert (Review-Fund: `disable-model-invocation` verhindert Auto-Invoke).
**Claude-Variante (invertiert):** Claude orchestriert, Zweitmeinung von der **Codex CLI** (`codex exec --sandbox read-only`, gegen offizielle CLI-Referenz verifiziert) über neues `references/second-opinion-protocol.md`; Fallback: Subagent mit frischem Kontext, klar als lokaler Fallback gelabelt. `claude-protocol.md`, `openai.yaml` und PowerShell-Script entfallen hier.
**Codex-Variante:** Original-Rollenverteilung (Claude Code als Zweitmeinung) beibehalten; `invoke-claude-review.ps1` jetzt im Protokoll verlinkt (Review-Fund: war verwaist).

## 2. Gegenüber dem Original-Repo (mattpocock/skills, Stand 2026-07-02)

**Unverändert (Claude-Paket):** 19 der 22 portierten Skills byte-identisch (per `diff -r` verifiziert). Matts Skills sind bewusst modellagnostisch — für Fable 5 gab es nichts zu „optimieren", und unnötige Umformulierungen wären reine Drift-Quelle.

**Geändert (beide Pakete):**
- `ask-matt`: Abschnitt „Local additions (this pack)" — routet die 6 lokalen Skills ins Gesamtsystem.
- `setup-matt-pocock-skills`-Templates (github/gitlab/local): „Wayfinding operations"-Abschnitte entfernt — sie verwiesen auf den nicht portierten `in-progress`-Skill `wayfinder` (Review-Fund).

**Zusätzlich geändert (nur Codex-Paket):**
- Global: Skill-Verweise `/name` → `$name`; Frontmatter-Schlüssel `disable-model-invocation`/`argument-hint` entfernt (Codex ignoriert sie); für die 12 vormals nutzer-invozierten Skills `agents/openai.yaml` mit `allow_implicit_invocation: false` und handgeschriebenen Kurzbeschreibungen (Review-Fund: automatische Truncations waren unsauber).
- `code-review`, `improve-codebase-architecture`, `codebase-design/DESIGN-IT-TWICE.md`: Claude-spezifische Subagent-Aufrufe (`Agent`-Tool, `subagent_type=Explore`, `general-purpose`) generalisiert (parallel wenn verfügbar, sonst sequenziell mit frischem Kontext).
- `writing-great-skills`: Invocation-Mechanik von Claude-Frontmatter auf den openai.yaml-Mechanismus umgeschrieben (Review-Fund: lehrte sonst eine im Paket wirkungslose Technik).

**Nicht übernommen:** `in-progress/` (7, explizit unfertig), `deprecated/` (4), `personal/` (Matts private: edit-article, obsidian-vault), `misc/migrate-to-shoehorn` + `misc/scaffold-exercises` (Matts Kurs-Tooling). `git-guardrails-claude-code` nur im Claude-Paket (PreToolUse-Hooks existieren nur dort; Codex hat eigene Sandbox/Approvals).

## 3. Neue Skills — was sie tun und warum

### verify-before-done
Abschluss-Disziplin: Eine „Fertig"-Meldung braucht frischen Beleg aus einem Check, der auch hätte fehlschlagen können — mit Beweis-Leiter (Original-Failing-Case > gezielter Test > Suite > realer Aufruf > Rendern > Read-Through), Meldeformat (Verified / Implemented-but-unverified / Partial) und Tautologie-Verbot.
**Warum:** Unbelegte Fertig-Meldungen sind der häufigste Agenten-Fehlermodus — modellunabhängig der größte einzelne Qualitätshebel; passt zur TDD/Feedback-Loop-Philosophie des restlichen Pakets.
**Test:** Agent fixte einen Umlaut-Bug, lief die vorher rote Suite **nach** der letzten Änderung (grün, Output eingefügt), deckte eine Testlücke (ä fehlte in der Suite) per realem Aufruf ab und benannte die Beweis-Stufe. Ground-Truth-Nachlauf: Suite grün, Fix minimal. Bestanden.

### improve-project-structure (Doku-Nachtrag 03.07.2026)
Ordner-Pendant zu `improve-codebase-architecture`: scannt einen Projektordner auf strukturelle Reibung, präsentiert Reorganisations-Vorschläge als visuellen HTML-Report und setzt die gewählte Variante um — Ziel ist eine Struktur, in der Menschen und Agenten gleichermaßen schnell finden.

### project-review (Doku-Nachtrag 03.07.2026)
Nicht-Code-Pendant zu `code-review`: Zwei-Achsen-Review (Standards des Projekts / ursprünglicher Auftrag) für fertige Dokumente, Präsentationen, Tabellen, Pläne oder Deliverable-Ordner, mit parallelen Sub-Reviews.

*Beide Skills waren im Paket enthalten, aber in READMEs und CHANGES nicht erfasst; Zahlen und Listen am 03.07.2026 nachgezogen.*

## 4. Review-Runde (2 unabhängige Agents) — Ergebnis

0 kritisch, 2 major (beide Codex-Paket, behoben: writing-great-skills-Mechanik; verwaistes PowerShell-Script), 6 minor + 5 nits (behoben, oben als „Review-Fund" markiert). Akzeptiert statt gefixt: Multi-Plattform-Abschnitte in `visual-companion.md` (inzwischen mit brainstorming entfernt). Abschluss-Verifikation nach der Entfernung: Frontmatter, Querverweise, Links, Paket-Leckagen, YAML — alles grün.

## 5. Zweite Review-Runde (04.07.2026, GPT-5.5 xhigh)

Vollständiger Zweit-Review des Codex-Pakets durch Codex CLI (GPT-5.5, reasoning `xhigh`, read-only Sandbox), inklusive Abgleich gegen die offiziellen Docs (developers.openai.com/codex/skills, Claude-Code-CLI-Referenz). Ergebnis: 0 kritisch, 6 major, 4 minor — alle Befunde am Code verifiziert und umgesetzt:

1. **setup-matt-pocock-skills** (Codex): bevorzugte `CLAUDE.md` beim Schreiben — Codex liest aber `AGENTS.md`. Jetzt: `AGENTS.md` bevorzugt, `CLAUDE.md` nur als Migrationskontext.
2. **to-issues ↔ implement-issues** (beide Pakete): Lokaler Markdown-Flow war intern gebrochen — das Issue-Template erzeugte keine `Status:`-/`Implementation:`-Zeilen, die implement-issues zum Aufgreifen braucht. Template ergänzt; Konventionen in `issue-tracker-local.md` dokumentiert.
3. **implement-issues Label-Matching** (beide Pakete): Skripte matchen kanonische Rollen-Strings hart; jetzt dokumentiert und erzwungen, dass lokale `Status:`-Werte immer kanonisch sind (Label-Remapping gilt nur für GitHub/GitLab).
4. **invoke-claude-review.ps1** (Codex): klassischer .NET-Pipe-Deadlock (ReadToEnd nach WaitForExit); auf asynchrones Stream-Draining umgestellt.
5. **setup-matt-pocock-skills**: hängende Referenz auf nicht portierten Skill `qa` entfernt (beide Pakete).
6. **tdd**: hängende Referenz „see the `review` skill" → `code-review`/`review-loop` (beide Pakete).
7. **writing-great-skills** (Codex): `openai.yaml`-Beispiel als korrektes verschachteltes YAML; Behauptung korrigiert — explizites `$name`-Routing bleibt trotz `allow_implicit_invocation: false` möglich.
8. **improve-project-structure** (Codex): Cowork-spezifische Formulierung neutralisiert.
9. **to-prd** (Codex): Widerspruch „no interview" vs. Pflicht-Rückfrage zu Seams → optionale Einzelrückfrage nur bei materieller Unsicherheit.
10. **implement, setup-pre-commit** (Codex): Commit erst nach Zustimmung, sofern nicht ausdrücklich beauftragt. Bei `resolving-merge-conflicts` bewusst nicht geändert — der Commit ist dort inhärenter Teil des Merge-Abschlusses (vom Reviewer selbst als Ausnahme benannt).

Durch die gespiegelten Fixes (2, 3, 5, 6) sind im Claude-Paket nun zusätzlich `tdd`, `to-issues` und `setup-matt-pocock-skills` (SKILL.md + `issue-tracker-local.md`) gegenüber Upstream verändert — jede Abweichung ist hier dokumentiert.

Außerdem in dieser Runde: Root-README auf Englisch neu geschrieben (Installation, Attribution, Änderungsübersicht), Pack-READMEs übersetzt, `install.sh`/`install.ps1` (flache Installation für beide Pakete, global/projektweit), Root-`LICENSE` (MIT) und `.gitignore` ergänzt.

## Paketstand

Claude: 29 Skills · Codex: 30 Skills, je gruppiert in `MattSkills/` (Upstream-Anteil inkl. Lizenz) und `LutossSkills/`; bei Installation flach ins Ziel kopieren. Flow: `grill-with-docs → to-prd → to-issues → implement`/`implement-issues` → `review-loop` → Human-Abnahme, mit `verify-before-done` als Disziplin darunter.

## 6. Lernendes Subagent-Routing und Claude-Brücke (10.07.2026)

### agent-evals

Lokaler, schema-versionierter SQLite-Store für native Codex-Subagents und externe Agenten. Erfasst nur minimierte Metadaten, Hashes, verifizierte 1–5-Rubriken und append-only Folgeurteile; keine Rohprompts, Transkripte, Secrets, Quelltexte oder absoluten Projektpfade. Empfehlungen werden nach Task-Typ und Lane getrennt und erst ab fünf vergleichbaren bewerteten Läufen als empirisches Routing ausgegeben. Enthält Tests für Lifecycle, Mindeststichprobe, ungültige Checkdaten und parallele SQLite-Writes.

### ask-claude

Read-only Adapter für eine lokal authentifizierte Claude-Code-CLI als unabhängige Zweitmeinung. Startet Claude in Safe Mode mit Read/Glob/Grep, optional WebSearch/WebFetch, und sperrt Bash/Edit/Write. Die strukturierte Antwort wird als `pending_review` in `agent-evals` registriert; der Codex-Hauptagent muss Befunde verifizieren und den Lauf anschließend bewerten. Reale Smoke-Tests mit Claude Sonnet 4.6 und Claude Opus 4.8 bestanden.

`ask-matt` routet beide neuen Skills. Der Codex-Pack-Stand steigt von 28 auf 30 Skills und der Lutoss-Anteil von 6 auf 8.
