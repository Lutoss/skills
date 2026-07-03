---
name: improve-project-structure
description: Scan a project folder for structural friction, present reorganizations as a visual HTML report, then grill through whichever one you pick and carry out the moves — toward a structure where humans and AI agents alike find things fast.
---

# Improve Project Structure

Surface structural friction and propose **reorganizations** — moves that turn a grown-wild folder into a navigable project. The aim is **findability for both kinds of newcomer: humans and AI agents.**

The two audiences want the same thing. An agent finds material by listing names and searching text; a human finds it by scanning names and remembering places. Both are served by the same three properties:

- **Honest names** — every folder and file name says what's inside; nothing needs opening to be identified.
- **One home per topic** — each topic lives in exactly one place, so finding one thing means finding all of it.
- **An entry point** — a README (or index) at the root that maps what lives where, so nobody starts from zero.

What helps the intern helps the agent.

## Process

### 1. Pin the project

This skill operates on one concrete folder. Establish it before anything else:

- If the user named a folder, or one is already connected, confirm that's the project to restructure.
- If not, ask for one — in Cowork, request folder access; in a terminal, ask for the path.

Never scan without an agreed root: proposals about the wrong folder waste everyone's time, and the final step moves real files.

### 2. Explore

Walk the project read-only — with a read-only exploration subagent when available, otherwise directly. Don't follow rigid heuristics — explore organically and note where you experience friction:

- Where do names lie or say nothing — `New folder (2)`, `final_final_v3`, `misc`, `stuff`?
- Where does one topic live in several places — or several unrelated topics in one folder?
- Where do versions pile up as copies instead of one current file plus an archive?
- Where does depth hide things (six levels down) or flatness drown them (two hundred files in one folder)?
- Where do conventions flip mid-project — date formats, languages, `CamelCase` vs `kebab-case`?
- Is there an entry point at all — anything that tells a newcomer what lives where?

Apply the **stranger test** to anything you suspect: could a stranger — human or agent — find this from names alone, without opening files or asking around? A "no" is the signal you want.

### 3. Present candidates as an HTML report

Write a self-contained HTML file to the OS temp directory so nothing lands in the project. Resolve the temp dir from `$TMPDIR`, falling back to `/tmp` (or `%TEMP%` on Windows), and write to `<tmpdir>/structure-review-<timestamp>.html` so each run gets a fresh file. Open it for the user — `xdg-open <path>` on Linux, `open <path>` on macOS, `start <path>` on Windows — and tell them the absolute path.

The report uses **Tailwind via CDN** for layout and styling. Each candidate gets a **before/after folder tree**, side by side — the before tree annotated with its friction, the after tree showing the proposed shape. Be visual.

For each candidate, render a card with:

- **Folders** — which parts of the project are involved
- **Problem** — why the current structure causes friction
- **Solution** — plain-language description of what would move, merge, or be renamed
- **Benefits** — stated separately for humans ("you find X without remembering where it is") and for agents ("a search for X hits one folder, not four")
- **Before / After tree** — side by side
- **Recommendation strength** — one of `Strong`, `Worth exploring`, `Speculative`, rendered as a badge

End the report with a **Top recommendation** section: which candidate to tackle first and why.

Do NOT move anything yet. After the file is written, ask the user: "Which of these would you like to explore?"

### 4. Grilling loop

Once the user picks a candidate, run the `$grilling` skill to walk the decision tree with them: what belongs where, what counts as current vs. archive, which naming convention wins, and — critically — what must not break: shared links, shortcuts, tools or colleagues that expect today's paths.

### 5. Execute the restructure

Folders, unlike architectures, don't stop at the drawing board. Once the grilling converges:

1. Present the complete move plan — every move, rename, and archive step — as a dry-run list, and get explicit approval.
2. Execute it. **Delete nothing**: anything obsolete or unidentifiable goes into an `archive/` folder inside the project, where the user can inspect and empty it later. A restructure that loses a file has failed, no matter how clean the result looks.
3. Write or update the **README at the project root** — the entry point: what this project is, what lives where, and the naming convention that keeps it that way. Without this step the structure starts decaying the day after.
4. Close with the stranger test, re-run: name three things someone might look for, and show where each now lives — one guess, one hit each.
