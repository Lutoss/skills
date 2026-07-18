---
name: loop-creator
description: Create a concrete Loop Contract or Loop Spec from project context, decisions, and existing skills. Use when a new repeatable agent workflow is needed, a vague process should become agent-ready, or the user asks to design a loop.
---

# Loop Creator

Use this as the meta-loop before adding another workflow skill. Prefer reusing
or composing existing skills when they already cover the job.

## Contract

Goal: Turn a fuzzy repeatable workflow into a concrete Loop Contract, Loop Spec,
or smallest safe edit to an existing skill.
Scope: Local project context, the skills installed in this pack, relevant
reports, handoffs, and the requested workflow.
Allowed: Read local context and skill files; draft local Loop Specs, reports,
handoffs, or skill edits; run local validation.
Forbidden: No push, publish, remote setup, send, label, close, delete, move,
merge, external write, full transcript artifact, or visible new chat/thread
without explicit Go.
Signals: Existing skill fit, missing contract decisions, validation result,
reference test clarity, and unresolved Human/Privacy Gates.
Stop: Stop when an existing skill composition is enough, when missing decisions
block a safe contract, before any gated action, or after validation of the
smallest approved local edit.
Human gates: The user must approve external writes, risky local rewrites,
sensitive project handling beyond read-only analysis, and new visible
chats/threads.
Output: Loop Spec or smallest skill-change proposal with subloops, gates,
signals, stop rules, reference test, and next action.
Learning capture: Record evidence-backed workflow rules in the final brief,
`docs/agents/loop-learnings.md`, or a proposed skill update.

## Inputs

- User goal or recurring pain point.
- Project context: `README.md`, `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`,
  `PLAN.md`, ADRs, handoffs, and relevant reports.
- Existing skills and loop contracts.
- Optional /grill-with-docs results when decisions are still fuzzy.

## Loop

1. State the requested loop in one sentence.
2. Check whether an existing skill already fits.
3. If a skill mostly fits, propose the smallest edit or composition instead of
   creating a new skill.
4. If the project is sensitive or unknown, add an explicit privacy gate to the
   contract before anything else: what data may leave the machine, what needs
   user approval, and what stays read-only.
5. Identify missing decisions:
   - goal
   - scope
   - allowed actions
   - forbidden actions
   - delegation/subagents
   - feedback signals
   - stop conditions
   - budget/iteration limit
   - human gates
   - output artifact
   - learning capture
   - artifact lifecycle
   - AFK eligibility
   - backlog shape
6. If missing decisions block a safe contract, run or recommend
   /grill-with-docs.
7. Draft the Loop Contract using the template in the Output section below.
8. Select subloops from the installed skills, such as /handoff (context
   briefs), /diagnosing-bugs, /tdd, /code-review, /review-loop, /implement,
   or /to-issues.
9. Define the smallest reference test slice.
10. Prefer a Kanban/backlog loop over a linear phase plan when work can split.
11. Mark which steps can run AFK and which require Privacy or Human Gate.
12. Mark whether subagents may be used and whether new visible chats/threads
    require explicit Go.
13. If the user asked for a reusable skill, create or update a `SKILL.md`
    (see /writing-great-skills for the craft) and run validation.

## Output

End with:

```text
Loop name:
Use when:
Goal:
Scope:
Allowed actions:
Forbidden actions:
Delegation/Subagents:
Subloops:
Signals:
Stop rules:
Budget/iteration limit:
Human gates:
Output artifact:
Learning capture:
Reference test:
Next action:
```
