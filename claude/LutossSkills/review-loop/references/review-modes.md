# Review Modes

Use exactly one top-level mode: `standard`, `deep`, or `architecture review`.
Second-opinion and TDD are mandatory phases inside those modes, not
separate modes.

## standard

Use by default for code, docs, project hygiene, diffs, WIP branches,
agent-generated work, and normal review-fix-re-review.

Loop:

1. Establish the feedback signal.
2. Review locally.
3. Run the second-opinion reviewer (Codex CLI or fresh-context subagent) when allowed.
4. Triage findings.
5. Use TDD for behavior-changing confirmed findings where practical.
6. Fix every confirmed in-scope finding.
7. For standalone artifacts, implement the fixes in a new versioned file.
8. Verify and re-review with both the primary and the second-opinion reviewer.
9. Repeat until no confirmed actionable findings remain or a gate blocks.

Stop when no confirmed actionable findings remain or when next work is gated.

## deep

Use for courses, docs, UI, apps, presentations, large artifacts, or anything
where "does this work for the user?" matters.

Review axes:

- user journey and target audience
- content correctness and source quality
- privacy, safety, and data handling
- structure, navigation, links, anchors, and local file references
- visual design, mobile/desktop layout, screenshots, print/export when relevant
- fallback paths, timing, live-demo risk, and operational readiness
- final acceptance gates that require real hardware, accounts, or human judgment

For UI/web artifacts, prefer real browser checks and screenshots.

Deep mode still runs second-opinion and the TDD phase. For non-code
artifacts, mark TDD `not applicable` with the reason and use the artifact's
strongest feedback signal instead. For standalone artifacts, deliver a new
versioned file and keep the reviewed source unchanged.

## architecture review route

Use when the review uncovers deep design friction rather than a local defect:
module depth, interface shape, seam placement, testability, agent navigability,
or large refactor candidates.

Do not turn this into an unplanned refactor. Route to
`improve-codebase-architecture` when available. Otherwise draft ranked
candidates locally and choose the first vertical refactor slice only after the
gate is clear.

Architecture mode still runs second-opinion and the TDD phase. TDD
usually applies only after a first vertical refactor slice is approved.
If implementation is approved, solve all confirmed in-scope architecture-review
findings through the smallest safe slices; do not start a broad rewrite without
the Human Gate.

## Mandatory second-opinion phase

Run in every mode when privacy and tool availability allow it. Prefer the
installed Codex CLI (`codex`) over any local subagent second-opinion. Use a
local fresh-context subagent only after Codex is missing, unusable, blocked by
privacy, or explicitly not allowed, and record the blocker.

Default posture:

- build a scoped review packet
- stop at Privacy/Human Gate before external send unless user already gave Go
- check `codex --version` and a `CODEX_OK` smoke test
- use the CLI's strongest available reviewing model and report the exact CLI args used
- require findings with evidence and severity
- do not let the external reviewer edit files
- import findings as data
- verify locally before fixing

Read `second-opinion-protocol.md` before invoking the second-opinion reviewer.

## Mandatory TDD phase

Use when confirmed findings affect observable behavior.

Route through `tdd`, unless the finding is
trivial or the project has no useful test seam. One behavior test should drive
one fix. If a test cannot be written at a public interface, surface that as
architecture friction.

If TDD does not apply, record the reason explicitly.

## Acceptance loop

After fixes, run both the primary re-review and second-opinion acceptance when
allowed. Continue triage -> fix -> verify -> re-review until both have no
confirmed actionable findings. If a finding cannot be fixed, classify it as
gated, out of scope, false positive, duplicate, or blocked with evidence.
