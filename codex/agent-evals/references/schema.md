# Store and privacy contract

The SQLite database contains two logical records:

- subagent_runs: provenance, model configuration, task classification, timing, status, hashes, and optional numeric usage.
- run_evaluations: append-only evaluator judgments. Later human or downstream outcomes do not overwrite earlier judgments.

The store may contain:

- opaque session, turn, run, and agent identifiers;
- provider, pinned/reported model ID, alias, reasoning effort;
- controlled task kind, risk class, read/write mode, lane;
- timestamps, duration, tokens, and cost only when reported reliably;
- hashes of project path and last message;
- short sanitized evaluation notes and structured check outcomes.

The store must not contain:

- raw prompts or transcripts;
- source code or file contents;
- credentials, secrets, personal messages, or email addresses;
- absolute project paths;
- guessed model IDs, token counts, or costs.

The default database is %LOCALAPPDATA%\CodexAgentEvals\agent-evals.sqlite3 on Windows. Override with AGENT_EVALS_DB or the CLI --db option.
