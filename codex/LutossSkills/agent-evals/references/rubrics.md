# Evaluation rubric

## Task kinds

Use exactly one primary kind:

- codebase_exploration
- research_primary_sources
- planning_architecture
- implementation_clear_spec
- implementation_ambiguous
- bug_diagnosis
- code_review
- test_verification
- ui_computer_use
- migration_mechanical

## Universal 1–5 scores

| Score | Correctness | Completeness | Judgment | Efficiency |
|---|---|---|---|---|
| 5 | Verified correct | Fully satisfies scope | Excellent prioritization and restraint | Direct, low-rework execution |
| 4 | Minor non-material issue | Small omission | Good decisions with minor correction | Reasonable cost/time/rework |
| 3 | Mixed or partly verified | Material gap | Usable but needs guidance | Noticeable avoidable work |
| 2 | Major error | Large portion missing | Poor scope or prioritization | Heavy rework or overreach |
| 1 | Wrong or unsafe | Did not perform task | Fundamentally unsuitable decisions | No useful progress |

## Task-specific evidence

- Exploration: accurate file references, useful synthesis, no invented architecture.
- Research: primary-source coverage, supported claims, explicit uncertainty.
- Planning/architecture: constraints honored, seams clear, risks and alternatives addressed.
- Implementation: acceptance criteria and tests, minimal scope, no unrelated edits.
- Diagnosis: reproduced symptom, isolated cause, distinguished evidence from hypotheses.
- Review: confirmed findings, false-positive rate, missed issues, precise references.
- Verification/UI: reproducible steps, screenshots/logs where relevant, actual behavior checked.
- Migration: count of transformed cases, validation, no semantic drift.

Use lower confidence when evidence is incomplete. A polished answer is not evidence.
