---
name: verify-before-done
description: Evidence-based completion discipline. Use before claiming any work is done, fixed, working, or complete — run the check that would fail if it weren't, and report actual output. Also use when the user asks "is it done?", "did you test it?", or doubts a result, and at the end of any implementation, fix, or document-producing task.
---

# Verify Before Done

A completion claim is a **prediction** until a check has run. The rule: never
say "done", "fixed", "works", or "should work now" unless you hold **fresh
evidence from a check that could have failed**.

## The core move

Before reporting completion, ask: *what command or observation would go red if
this were actually broken?* Then run it — after your final edit, not before.
Evidence gathered before the last change is stale and proves nothing.

## Ladder of evidence

Strongest first — climb as high as the artifact allows:

1. **The original failing case, re-run.** For bugfixes: the repro/test that was
   red is now green.
2. **A targeted test at the right seam** — new or existing, exercising the
   changed behavior through its public interface.
3. **Suite-level checks** — relevant tests, typecheck, lint, build.
4. **A real invocation** — run the CLI/server/script and paste actual output.
5. **Rendering the artifact** — for docs/HTML/reports: open or render the
   produced file, check links and structure; re-read the file you wrote rather
   than trusting that the write succeeded.
6. **A careful read-through** — the weakest rung. If this is all you have, say
   so explicitly: "reviewed, not executed."

A check that passes **by construction** (asserting a value computed the same
way the code computes it, grepping for text you just wrote) is not evidence.

## Reporting

State claims at the strength of their evidence:

- **Verified:** what you ran, and the observed result (paste the relevant
  output, not a paraphrase).
- **Implemented but unverified:** what exists, why it is unverified, and the
  exact command the user can run to check.
- **Partial:** what works, what does not, what remains.

Unrelated failures you noticed still get reported — "done, but the suite has 2
pre-existing failures in X" — never silently absorbed.

## When no check exists

That is a finding, not an excuse. Either build the narrowest useful check (a
tight loop, as in /diagnosing-bugs Phase 1), or hand verification to the user
as an explicit gate: name what they should run or look at, and what they should
see if it works.
