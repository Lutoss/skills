# Issue tracker: Local Markdown

Issues and PRDs for this repo live as markdown files in `.scratch/`.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The PRD is `.scratch/<feature-slug>/PRD.md`
- Implementation issues are `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`
- Triage state is recorded as a `Status:` line near the top of each issue file, always using the canonical role strings (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`) verbatim — the label remapping in `triage-labels.md` applies to remote trackers (GitHub/GitLab), not to these lines; automation matches the canonical strings
- Implementation progress is recorded as an `Implementation:` line (`pending`, `in-progress`, `needs-info`, `done`)
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<feature-slug>/` (creating the directory if needed).

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.
