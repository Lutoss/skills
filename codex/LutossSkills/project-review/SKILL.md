---
name: project-review
description: Review a finished piece of work — a document, presentation, spreadsheet, plan, or folder of deliverables — along two axes — Standards (does it follow the project's documented conventions and quality bar?) and Brief (does it deliver what was originally asked?). Runs both reviews in parallel sub-agents and reports them side by side. Use when the user wants feedback on a draft, a check against requirements or the original task, or a second pair of eyes before something is sent, submitted, or presented — even if they just say "look this over". The non-code counterpart of code-review.
---

Two-axis review of a finished piece of work — a document, presentation, spreadsheet, plan, or folder of deliverables:

- **Standards** — does it follow the project's documented conventions and quality bar?
- **Brief** — does it deliver what was originally asked?

Both axes run as **parallel sub-agents** so they don't pollute each other's context, then this skill aggregates their findings.

## Process

### 1. Pin the deliverable

Whatever the user pointed at is the deliverable — a file, a folder, several files, or text pasted into the chat. If it's ambiguous which files are under review, ask.

Before going further, confirm every file opens and is non-empty. A missing attachment or an empty draft should fail here — not inside two parallel sub-agents.

### 2. Identify the brief

The brief is wherever the task was originally stated. Look for it in this order:

1. A path or text the user supplied.
2. A file in the project that states the task — names like `BRIEF.md`, `requirements`, `task`, `Auftrag`, a kickoff email, meeting notes.
3. If nothing is found, ask the user what was originally asked. If there is no written brief, have them state the goal in one or two sentences and use that. Only when they can't: the **Brief** sub-agent skips and reports "no brief available".

### 3. Identify the standards sources

Anything in the project that documents how work should look: style guides, templates, checklists, corporate-design rules, "how we write" notes.

On top of whatever the project documents, the Standards axis always carries the **quality baseline** below — a fixed set of deliverable smells that applies even when a project documents nothing. Two rules bind it:

- **The project overrides.** A documented project standard always wins; where it endorses something the baseline would flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic ("possible Buried Lede"), never a hard violation.

Each smell reads *what it is* → *how to fix*; match it against the deliverable:

- **Buried Lede** — the key message or ask sits behind pages of background. → put the conclusion first; background follows for those who need it.
- **Mysterious Title** — a title, heading, or filename that doesn't reveal what's underneath. → rename it; if no honest name comes, the content's murky.
- **Inconsistent Terminology** — the same thing called by different names across the piece. → pick one term, use it everywhere.
- **Duplicated Message** — the same point made in several places, each version drifting. → make it once, in the strongest spot.
- **Unexplained Jargon** — terms the stated audience won't know, used without a gate. → define on first use, or replace with plain language.
- **Format Fights Content** — the container hides the message: comparisons trapped in prose, narrative chopped into bullet confetti, a slide carrying a document's worth of text. → switch to the form the content wants.
- **Padding** — sentences that add words but no information ("as already mentioned", throat-clearing intros). → delete them; nothing replaces them.
- **Number Soup** — figures with no anchor: no comparison, no target, no time frame. → anchor every number the audience is meant to react to.
- **Missing Ask** — the piece informs but never says what should happen next. → end with the decision, action, or next step it exists to produce.
- **Leftover Scaffolding** — TODOs, placeholder text, dummy data, tracked changes still visible in the final. → resolve them, or flag the piece as a draft.
- **Audience Drift** — sections written for a different reader than the one the brief names (too expert, too basic, wrong concerns). → rewrite for the named reader.
- **Broken Promise** — a table of contents, agenda, or intro that announces content the piece never delivers. → deliver it, or stop announcing it.

### 4. Spawn both sub-agents in parallel

Spawn both as parallel subagents in the same turn if subagent tooling is available; otherwise run them one after another in fresh, separate contexts so their findings stay independent.

**Standards sub-agent prompt** — include:

- The deliverable's location (or full contents, if pasted).
- The list of standards-source files you found in step 3, **plus the quality baseline from step 3** pasted in full — the sub-agent has no other access to it.
- The brief: "Report — per file/section where relevant — (a) every place the deliverable violates a documented standard: cite the standard (file + the rule); and (b) any baseline smell you spot: name it and quote the passage. Distinguish hard violations from judgement calls — documented-standard breaches can be hard, but baseline smells are always judgement calls, and a documented project standard overrides the baseline. Under 400 words."

**Brief sub-agent prompt** — include:

- The deliverable's location (or full contents).
- The brief's contents, or the user's stated goal.
- The brief: "Report: (a) things the brief asked for that are missing or half-done; (b) content the brief never asked for (scope creep); (c) requirements that look addressed but miss the intent. Quote the brief line for each finding. Under 400 words."

If no brief is available, skip the Brief sub-agent and note this in the final report.

### 5. Aggregate

Present the two reports under `## Standards` and `## Brief` headings, verbatim or lightly cleaned. Do **not** merge or rerank findings — the two axes are deliberately separate (see _Why two axes_).

End with a one-line summary: total findings per axis, and the worst issue _within each axis_ (if any). Don't pick a single winner across axes — that's the reranking the separation exists to prevent.

## Why two axes

A deliverable can pass one axis and fail the other:

- A beautifully polished report that answers the wrong question → **Standards pass, Brief fail.**
- A piece that delivers exactly what was asked but ignores the house style → **Brief pass, Standards fail.**

Reporting them separately stops one axis from masking the other.
