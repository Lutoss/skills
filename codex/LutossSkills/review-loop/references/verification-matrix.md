# Verification Matrix

Pick checks by artifact type. Prefer the smallest check set that can catch the
class of defect found in review.

## Code

- unit/integration tests through public interfaces
- typecheck
- lint/format check
- targeted CLI or repro command
- fixture replay
- smoke test of changed entry points
- fresh `code-review` for meaningful diffs

Use TDD for behavior changes. If no red-capable signal exists, document the gap.

## Bugs and regressions

- reproduce the symptom first
- minimize the repro
- add a regression signal at the highest useful seam
- rerun original repro after the fix
- remove temporary instrumentation

Route unclear cases through `diagnosing-bugs`.

## UI, web apps, courses, and HTML artifacts

- DOM/structure checks: duplicate IDs, broken anchors, missing copy targets,
  missing local files
- desktop and mobile browser screenshots
- console error check
- horizontal overflow check
- link check for internal and external links
- visual spot check of key viewports
- interaction check for core controls where practical
- print/export check when the artifact is used offline or in a classroom

Use a design-review tool for design work when available and requested. Use local HTML/CSS
plus browser verification when a design-review tool is unavailable.

## Documents, PDFs, slides, and spreadsheets

- use the matching artifact skill
- render to images when layout matters
- inspect page or slide images, not just source files
- check links, page breaks, overflow, fonts, and export/readability

## Project hygiene and docs

- `rg` for old names, stale status markers, version strings, and expected terms
- file existence and non-empty checks
- report/handoff/index consistency
- Markdown link checks when practical
- validator scripts from the repo
- no accidental sensitive data or full transcripts

## Final acceptance

Report checks that actually ran. Separate local verification from external
gates such as real device tests, account/login checks, production deploys, or
human product judgment.
