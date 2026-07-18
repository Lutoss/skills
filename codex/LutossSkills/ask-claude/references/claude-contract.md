# Claude adapter contract

The adapter starts one external Agent Evals run with:

- provider claude-code;
- lane second_opinion;
- mode read;
- a unique claude:<uuid> agent ID.

Claude receives no Bash or editing tools. --allow-web adds only WebSearch and WebFetch.

The structured result contains:

- status: complete, blocked, or uncertain;
- summary and answer;
- zero or more findings with severity, title, detail, evidence, and recommendation;
- checks performed;
- uncertainties.

The normalized wrapper output also returns the run and agent IDs, requested model alias, model IDs reported by Claude Code, effort, duration, tokens, and cost when present.

Successful invocation ends as pending_review. The parent Codex agent verifies the result and records the evaluation. Timeout or CLI failure ends as failed and remains visible.
