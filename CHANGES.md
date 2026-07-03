# CHANGES — Was geändert wurde und warum

Stand: 2026-07-03, nach Review-Runde (2 unabhängige Review-Agents), Testläufen und Flow-Entscheidung.

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

## Paketstand

Claude: 29 Skills · Codex: 28 Skills, je gruppiert in `MattSkills/` (Upstream-Anteil inkl. Lizenz) und `LutossSkills/` (deine sanierten Skills + `verify-before-done`, `improve-project-structure`, `project-review`); bei Installation flach ins Ziel kopieren. Flow: `grill-with-docs → to-prd → to-issues → implement`/`implement-issues` → `review-loop` → Human-Abnahme, mit `verify-before-done` als Disziplin darunter.
