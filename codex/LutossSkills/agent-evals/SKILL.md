---
name: agent-evals
description: Route, register, and evaluate native Codex subagents and external agent runs in a private local SQLite store. Use whenever Codex is about to use a subagent, has received a subagent result, compares model suitability, records a retry or escalation, or the user asks for the model leaderboard or learned routing history. This skill manages evaluation; it does not itself authorize delegation.
---

# Agent Evals

Use the store CLI at scripts/agent_evals.py. Keep database details behind this interface.

## Before a subagent run

1. Classify the task using one task_kind from [rubrics.md](references/rubrics.md).
2. Set risk to low, medium, or high and mode to read or write.
3. Respect an explicit user-pinned model. Otherwise request a recommendation:

    python "<skill-dir>\scripts\agent_evals.py" recommend --task-kind code_review --risk medium --mode read

Use --lane second_opinion for a cross-model reviewer such as Claude.

4. Spawn only when the user or another applicable instruction authorizes subagents.
5. Prefer a model-pinned custom agent. After spawn returns an agent ID, annotate the hook-created run:

    python "<skill-dir>\scripts\agent_evals.py" annotate --agent-id "<id>" --model-id "gpt-5.6-terra" --reasoning medium --task-kind codebase_exploration --risk low --mode read

If the actual model is not visible or pinned, record unknown; never infer it.

## After a subagent run

1. Inspect the returned result.
2. Verify important claims with the task's real feedback signal: tests, source checks, file references, render/visual QA, or human acceptance.
3. Read [rubrics.md](references/rubrics.md) and score the run. The producing agent must not be its only evaluator.
4. Finalize the evaluation:

    python "<skill-dir>\scripts\agent_evals.py" finish --agent-id "<id>" --outcome accepted_with_edits --correctness 4 --completeness 5 --judgment 4 --efficiency 4 --confidence 0.85 --check tests=pass --note "Needed one scoped correction."

Record every attempt. Link retries when starting them; never overwrite a weak first attempt with a successful escalation.

## Evaluation rules

- Scores are 1–5. Confidence is 0–1.
- Deterministic evidence outranks a model's self-report.
- accepted_with_edits means useful but required material correction or rework.
- blocked and cancelled remain data, not silent omissions.
- Do not bypass tests, review, privacy gates, or production gates because of a high score.
- Treat recommendations with fewer than five comparable evaluated runs as cold-start defaults.
- Compare only within the same task kind and lane.

## Privacy

Read [schema.md](references/schema.md) before changing stored fields.

Never store raw prompts, transcripts, source code, secrets, email addresses, or absolute project paths. Hooks hash the last message and project path. Keep notes short and sanitized.

## Failure behavior

Hooks fail open so the user's task is not blocked by telemetry. If a manual store command fails, report the failure and continue the main task without pretending the evaluation was recorded.

## Reports

    python "<skill-dir>\scripts\agent_evals.py" leaderboard --task-kind code_review
    python "<skill-dir>\scripts\agent_evals.py" pending
    python "<skill-dir>\scripts\agent_evals.py" db-path
