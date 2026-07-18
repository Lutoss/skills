#!/usr/bin/env python3
"""Local, privacy-preserving evaluation store for Codex and external agents."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1"
VALID_TASK_KINDS = {
    "codebase_exploration",
    "research_primary_sources",
    "planning_architecture",
    "implementation_clear_spec",
    "implementation_ambiguous",
    "bug_diagnosis",
    "code_review",
    "test_verification",
    "ui_computer_use",
    "migration_mechanical",
}
VALID_OUTCOMES = {"accepted", "accepted_with_edits", "rejected", "blocked", "cancelled"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def default_db_path() -> Path:
    override = os.environ.get("AGENT_EVALS_DB")
    if override:
        return Path(override).expanduser().resolve()
    base = os.environ.get("LOCALAPPDATA")
    if base:
        return Path(base) / "CodexAgentEvals" / "agent-evals.sqlite3"
    return Path.home() / ".local" / "share" / "codex-agent-evals" / "agent-evals.sqlite3"


def project_hash(path: str | Path | None = None) -> str:
    resolved = str(Path(path or os.getcwd()).resolve()).lower()
    return hashlib.sha256(resolved.encode("utf-8")).hexdigest()[:16]


def text_hash(value: str | None) -> str | None:
    if value is None:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def connect(db_path: str | Path | None = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path else default_db_path()
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 10000")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    initialize(conn)
    return conn


def initialize(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS subagent_runs (
            run_id TEXT PRIMARY KEY,
            session_id TEXT,
            turn_id TEXT,
            agent_id TEXT NOT NULL UNIQUE,
            provider TEXT NOT NULL DEFAULT 'openai',
            lane TEXT NOT NULL DEFAULT 'primary',
            agent_type TEXT NOT NULL,
            model_id TEXT NOT NULL DEFAULT 'unknown',
            model_alias TEXT,
            model_snapshot TEXT,
            reasoning_effort TEXT NOT NULL DEFAULT 'unknown',
            task_kind TEXT NOT NULL DEFAULT 'unknown',
            risk_class TEXT NOT NULL DEFAULT 'unknown',
            read_write_mode TEXT NOT NULL DEFAULT 'read',
            project_hash TEXT,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            duration_ms INTEGER,
            status TEXT NOT NULL DEFAULT 'running',
            retry_of_run_id TEXT,
            cost_usd REAL,
            input_tokens INTEGER,
            output_tokens INTEGER,
            last_message_hash TEXT,
            metadata_json TEXT NOT NULL DEFAULT '{}',
            FOREIGN KEY (retry_of_run_id) REFERENCES subagent_runs(run_id)
        );

        CREATE INDEX IF NOT EXISTS idx_runs_task_model
            ON subagent_runs(task_kind, lane, provider, model_id, reasoning_effort);
        CREATE INDEX IF NOT EXISTS idx_runs_status ON subagent_runs(status);

        CREATE TABLE IF NOT EXISTS run_evaluations (
            evaluation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            evaluated_at TEXT NOT NULL,
            evaluator_type TEXT NOT NULL,
            evaluator_model TEXT,
            outcome TEXT NOT NULL,
            correctness INTEGER NOT NULL CHECK (correctness BETWEEN 1 AND 5),
            completeness INTEGER NOT NULL CHECK (completeness BETWEEN 1 AND 5),
            judgment INTEGER NOT NULL CHECK (judgment BETWEEN 1 AND 5),
            efficiency INTEGER NOT NULL CHECK (efficiency BETWEEN 1 AND 5),
            confidence REAL NOT NULL CHECK (confidence BETWEEN 0 AND 1),
            checks_json TEXT NOT NULL DEFAULT '{}',
            note TEXT NOT NULL DEFAULT '',
            rubric_version TEXT NOT NULL DEFAULT '1',
            FOREIGN KEY (run_id) REFERENCES subagent_runs(run_id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_evaluations_run
            ON run_evaluations(run_id, evaluation_id);
        """
    )
    conn.execute(
        "INSERT INTO meta(key, value) VALUES('schema_version', ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (SCHEMA_VERSION,),
    )


def _merge_metadata(existing: str | None, additions: dict[str, Any] | None) -> str:
    try:
        merged = json.loads(existing or "{}")
    except json.JSONDecodeError:
        merged = {}
    if additions:
        merged.update(additions)
    return json.dumps(merged, ensure_ascii=False, sort_keys=True)


def start_run(
    conn: sqlite3.Connection,
    *,
    agent_id: str,
    agent_type: str,
    provider: str = "openai",
    lane: str = "primary",
    session_id: str | None = None,
    turn_id: str | None = None,
    model_id: str = "unknown",
    model_alias: str | None = None,
    reasoning_effort: str = "unknown",
    task_kind: str = "unknown",
    risk_class: str = "unknown",
    read_write_mode: str = "read",
    retry_of_run_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    existing = conn.execute(
        "SELECT * FROM subagent_runs WHERE agent_id = ?", (agent_id,)
    ).fetchone()
    if existing:
        merged_metadata = _merge_metadata(existing["metadata_json"], metadata)
        conn.execute(
            """
            UPDATE subagent_runs SET
                session_id=COALESCE(?, session_id), turn_id=COALESCE(?, turn_id),
                provider=?, lane=?, agent_type=?,
                model_id=CASE WHEN ? != 'unknown' THEN ? ELSE model_id END,
                model_alias=COALESCE(?, model_alias),
                reasoning_effort=CASE WHEN ? != 'unknown' THEN ? ELSE reasoning_effort END,
                task_kind=CASE WHEN ? != 'unknown' THEN ? ELSE task_kind END,
                risk_class=CASE WHEN ? != 'unknown' THEN ? ELSE risk_class END,
                read_write_mode=?, retry_of_run_id=COALESCE(?, retry_of_run_id),
                metadata_json=?
            WHERE agent_id=?
            """,
            (
                session_id,
                turn_id,
                provider,
                lane,
                agent_type,
                model_id,
                model_id,
                model_alias,
                reasoning_effort,
                reasoning_effort,
                task_kind,
                task_kind,
                risk_class,
                risk_class,
                read_write_mode,
                retry_of_run_id,
                merged_metadata,
                agent_id,
            ),
        )
    else:
        conn.execute(
            """
            INSERT INTO subagent_runs(
                run_id, session_id, turn_id, agent_id, provider, lane, agent_type,
                model_id, model_alias, reasoning_effort, task_kind, risk_class,
                read_write_mode, project_hash, started_at, status, retry_of_run_id,
                metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'running', ?, ?)
            """,
            (
                str(uuid.uuid4()),
                session_id,
                turn_id,
                agent_id,
                provider,
                lane,
                agent_type,
                model_id,
                model_alias,
                reasoning_effort,
                task_kind,
                risk_class,
                read_write_mode,
                project_hash(),
                utc_now(),
                retry_of_run_id,
                json.dumps(metadata or {}, ensure_ascii=False, sort_keys=True),
            ),
        )
    return dict(
        conn.execute("SELECT * FROM subagent_runs WHERE agent_id = ?", (agent_id,)).fetchone()
    )


def annotate_run(conn: sqlite3.Connection, agent_id: str, **fields: Any) -> dict[str, Any]:
    allowed = {
        "provider",
        "lane",
        "model_id",
        "model_alias",
        "model_snapshot",
        "reasoning_effort",
        "task_kind",
        "risk_class",
        "read_write_mode",
        "duration_ms",
        "cost_usd",
        "input_tokens",
        "output_tokens",
        "status",
    }
    row = conn.execute("SELECT * FROM subagent_runs WHERE agent_id = ?", (agent_id,)).fetchone()
    if not row:
        raise ValueError(f"Unknown agent_id: {agent_id}")
    updates: list[str] = []
    values: list[Any] = []
    metadata = fields.pop("metadata", None)
    for key, value in fields.items():
        if key in allowed and value is not None:
            updates.append(f"{key} = ?")
            values.append(value)
    if metadata:
        updates.append("metadata_json = ?")
        values.append(_merge_metadata(row["metadata_json"], metadata))
    if updates:
        values.append(agent_id)
        conn.execute(f"UPDATE subagent_runs SET {', '.join(updates)} WHERE agent_id = ?", values)
    return dict(
        conn.execute("SELECT * FROM subagent_runs WHERE agent_id = ?", (agent_id,)).fetchone()
    )


def mark_stopped(
    conn: sqlite3.Connection,
    *,
    agent_id: str,
    agent_type: str = "unknown",
    status: str = "pending_review",
    last_message: str | None = None,
    session_id: str | None = None,
    turn_id: str | None = None,
) -> dict[str, Any]:
    row = conn.execute("SELECT * FROM subagent_runs WHERE agent_id = ?", (agent_id,)).fetchone()
    if not row:
        start_run(
            conn,
            agent_id=agent_id,
            agent_type=agent_type,
            session_id=session_id,
            turn_id=turn_id,
        )
    conn.execute(
        """
        UPDATE subagent_runs SET completed_at=?, status=?, last_message_hash=?,
            session_id=COALESCE(?, session_id), turn_id=COALESCE(?, turn_id)
        WHERE agent_id=?
        """,
        (utc_now(), status, text_hash(last_message), session_id, turn_id, agent_id),
    )
    return dict(
        conn.execute("SELECT * FROM subagent_runs WHERE agent_id = ?", (agent_id,)).fetchone()
    )


def finish_evaluation(
    conn: sqlite3.Connection,
    *,
    agent_id: str,
    evaluator_type: str,
    outcome: str,
    correctness: int,
    completeness: int,
    judgment: int,
    efficiency: int,
    confidence: float,
    evaluator_model: str | None = None,
    checks: Any = None,
    note: str = "",
    rubric_version: str = "1",
) -> dict[str, Any]:
    if outcome not in VALID_OUTCOMES:
        raise ValueError(f"Invalid outcome: {outcome}")
    for name, value in {
        "correctness": correctness,
        "completeness": completeness,
        "judgment": judgment,
        "efficiency": efficiency,
    }.items():
        if not 1 <= value <= 5:
            raise ValueError(f"{name} must be 1..5")
    if not 0 <= confidence <= 1:
        raise ValueError("confidence must be 0..1")
    run = conn.execute("SELECT * FROM subagent_runs WHERE agent_id = ?", (agent_id,)).fetchone()
    if not run:
        raise ValueError(f"Unknown agent_id: {agent_id}")
    if isinstance(checks, str):
        try:
            normalized_checks = json.loads(checks)
        except json.JSONDecodeError as exc:
            raise ValueError(f"checks must be valid JSON: {exc}") from exc
    else:
        normalized_checks = checks or {}
    checks_json = json.dumps(normalized_checks, ensure_ascii=False, sort_keys=True)
    conn.execute("BEGIN IMMEDIATE")
    try:
        cursor = conn.execute(
            """
            INSERT INTO run_evaluations(
                run_id, evaluated_at, evaluator_type, evaluator_model, outcome,
                correctness, completeness, judgment, efficiency, confidence,
                checks_json, note, rubric_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run["run_id"],
                utc_now(),
                evaluator_type,
                evaluator_model,
                outcome,
                correctness,
                completeness,
                judgment,
                efficiency,
                confidence,
                checks_json,
                note[:1000],
                rubric_version,
            ),
        )
        conn.execute("UPDATE subagent_runs SET status='evaluated' WHERE run_id=?", (run["run_id"],))
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise
    return dict(
        conn.execute(
            "SELECT * FROM run_evaluations WHERE evaluation_id = ?", (cursor.lastrowid,)
        ).fetchone()
    )


def leaderboard_rows(
    conn: sqlite3.Connection,
    *,
    task_kind: str | None = None,
    lane: str | None = None,
    min_samples: int = 5,
) -> list[dict[str, Any]]:
    where = ["r.model_id != 'unknown'"]
    params: list[Any] = []
    if task_kind:
        where.append("r.task_kind = ?")
        params.append(task_kind)
    if lane:
        where.append("r.lane = ?")
        params.append(lane)
    query = f"""
        WITH latest AS (
            SELECT e.* FROM run_evaluations e
            JOIN (
                SELECT run_id, MAX(evaluation_id) AS evaluation_id
                FROM run_evaluations GROUP BY run_id
            ) x ON x.evaluation_id = e.evaluation_id
        )
        SELECT
            r.provider, r.lane, r.model_id, r.reasoning_effort, r.task_kind,
            COUNT(*) AS samples,
            AVG((e.correctness + e.completeness + e.judgment + e.efficiency) / 4.0) AS quality,
            AVG(CASE e.outcome WHEN 'accepted' THEN 1.0 WHEN 'accepted_with_edits' THEN 0.75 ELSE 0.0 END) AS success,
            AVG(e.confidence) AS confidence,
            AVG(r.duration_ms) AS avg_duration_ms
        FROM subagent_runs r JOIN latest e ON e.run_id = r.run_id
        WHERE {' AND '.join(where)}
        GROUP BY r.provider, r.lane, r.model_id, r.reasoning_effort, r.task_kind
    """
    rows = []
    for row in conn.execute(query, params).fetchall():
        item = dict(row)
        quality_norm = float(item["quality"] or 0) / 5.0
        evidence = min(1.0, int(item["samples"]) / max(1, min_samples))
        item["fit_score"] = round(
            (0.7 * quality_norm + 0.3 * float(item["success"] or 0)) * evidence, 4
        )
        item["eligible"] = int(item["samples"]) >= min_samples
        rows.append(item)
    return sorted(
        rows, key=lambda x: (x["eligible"], x["fit_score"], x["samples"]), reverse=True
    )


def recommendation(
    conn: sqlite3.Connection,
    *,
    task_kind: str,
    risk_class: str,
    read_write_mode: str,
    lane: str,
    min_samples: int,
) -> dict[str, Any]:
    rows = leaderboard_rows(conn, task_kind=task_kind, lane=lane, min_samples=min_samples)
    eligible = [row for row in rows if row["eligible"]]
    if eligible:
        best = eligible[0]
        return {
            "source": "empirical",
            "provider": best["provider"],
            "lane": lane,
            "model_id": best["model_id"],
            "reasoning_effort": best["reasoning_effort"],
            "samples": best["samples"],
            "fit_score": best["fit_score"],
            "note": "Use verification and human gates independently of this recommendation.",
        }
    if lane == "second_opinion":
        fallback = ("claude-code", "opus", "high")
    elif read_write_mode == "read" and risk_class in {"low", "medium"}:
        fallback = ("openai", "gpt-5.6-terra", "medium")
    else:
        fallback = ("openai", "gpt-5.6-sol", "high")
    return {
        "source": "cold_start_default",
        "provider": fallback[0],
        "lane": lane,
        "model_id": fallback[1],
        "reasoning_effort": fallback[2],
        "samples": rows[0]["samples"] if rows else 0,
        "fit_score": None,
        "note": (
            f"Fewer than {min_samples} comparable evaluated runs; "
            "do not treat this as learned routing."
        ),
    }


def _json_print(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def _hook_payload() -> dict[str, Any]:
    raw = sys.stdin.read()
    return json.loads(raw) if raw.strip() else {}


def handle_hook_start(conn: sqlite3.Connection) -> None:
    payload = _hook_payload()
    start_run(
        conn,
        agent_id=payload.get("agent_id") or f"unknown:{uuid.uuid4()}",
        agent_type=payload.get("agent_type") or "unknown",
        session_id=payload.get("session_id"),
        turn_id=payload.get("turn_id"),
        metadata={"hook_event": payload.get("hook_event_name", "SubagentStart")},
    )


def handle_hook_stop(conn: sqlite3.Connection) -> None:
    payload = _hook_payload()
    mark_stopped(
        conn,
        agent_id=payload.get("agent_id") or f"unknown:{uuid.uuid4()}",
        agent_type=payload.get("agent_type") or "unknown",
        session_id=payload.get("session_id"),
        turn_id=payload.get("turn_id"),
        last_message=payload.get("last_assistant_message"),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=None, help="Override SQLite database path")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init")
    sub.add_parser("db-path")
    sub.add_parser("hook-start")
    sub.add_parser("hook-stop")

    start = sub.add_parser("start")
    start.add_argument("--agent-id", required=True)
    start.add_argument("--agent-type", required=True)
    start.add_argument("--provider", default="openai")
    start.add_argument("--lane", choices=["primary", "second_opinion"], default="primary")
    start.add_argument("--session-id")
    start.add_argument("--turn-id")
    start.add_argument("--model-id", default="unknown")
    start.add_argument("--model-alias")
    start.add_argument("--reasoning", default="unknown")
    start.add_argument("--task-kind", default="unknown")
    start.add_argument("--risk", default="unknown")
    start.add_argument("--mode", choices=["read", "write"], default="read")
    start.add_argument("--retry-of")

    annotate = sub.add_parser("annotate")
    annotate.add_argument("--agent-id", required=True)
    annotate.add_argument("--provider")
    annotate.add_argument("--lane", choices=["primary", "second_opinion"])
    annotate.add_argument("--model-id")
    annotate.add_argument("--model-alias")
    annotate.add_argument("--model-snapshot")
    annotate.add_argument("--reasoning")
    annotate.add_argument("--task-kind")
    annotate.add_argument("--risk")
    annotate.add_argument("--mode", choices=["read", "write"])
    annotate.add_argument("--duration-ms", type=int)
    annotate.add_argument("--cost-usd", type=float)
    annotate.add_argument("--input-tokens", type=int)
    annotate.add_argument("--output-tokens", type=int)

    stop = sub.add_parser("stop")
    stop.add_argument("--agent-id", required=True)
    stop.add_argument("--agent-type", default="unknown")
    stop.add_argument("--status", default="pending_review")

    finish = sub.add_parser("finish")
    finish.add_argument("--agent-id", required=True)
    finish.add_argument("--evaluator-type", default="parent_agent")
    finish.add_argument("--evaluator-model")
    finish.add_argument("--outcome", choices=sorted(VALID_OUTCOMES), required=True)
    finish.add_argument("--correctness", type=int, required=True)
    finish.add_argument("--completeness", type=int, required=True)
    finish.add_argument("--judgment", type=int, required=True)
    finish.add_argument("--efficiency", type=int, required=True)
    finish.add_argument("--confidence", type=float, required=True)
    finish.add_argument("--checks-json", default="{}")
    finish.add_argument(
        "--check",
        action="append",
        default=[],
        help="Repeatable key=value check; safer than inline JSON in shells",
    )
    finish.add_argument("--note", default="")
    finish.add_argument("--rubric-version", default="1")

    recommend = sub.add_parser("recommend")
    recommend.add_argument("--task-kind", choices=sorted(VALID_TASK_KINDS), required=True)
    recommend.add_argument("--risk", choices=["low", "medium", "high"], required=True)
    recommend.add_argument("--mode", choices=["read", "write"], required=True)
    recommend.add_argument("--lane", choices=["primary", "second_opinion"], default="primary")
    recommend.add_argument("--min-samples", type=int, default=5)

    leaderboard = sub.add_parser("leaderboard")
    leaderboard.add_argument("--task-kind", choices=sorted(VALID_TASK_KINDS))
    leaderboard.add_argument("--lane", choices=["primary", "second_opinion"])
    leaderboard.add_argument("--min-samples", type=int, default=5)

    pending = sub.add_parser("pending")
    pending.add_argument("--session-id")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    path = args.db or default_db_path()
    if args.command == "db-path":
        print(Path(path).expanduser().resolve())
        return 0
    try:
        conn = connect(path)
        if args.command == "init":
            _json_print(
                {"db": str(Path(path).expanduser().resolve()), "schema_version": SCHEMA_VERSION}
            )
        elif args.command == "hook-start":
            handle_hook_start(conn)
            print("{}")
        elif args.command == "hook-stop":
            handle_hook_stop(conn)
            print("{}")
        elif args.command == "start":
            _json_print(
                start_run(
                    conn,
                    agent_id=args.agent_id,
                    agent_type=args.agent_type,
                    provider=args.provider,
                    lane=args.lane,
                    session_id=args.session_id,
                    turn_id=args.turn_id,
                    model_id=args.model_id,
                    model_alias=args.model_alias,
                    reasoning_effort=args.reasoning,
                    task_kind=args.task_kind,
                    risk_class=args.risk,
                    read_write_mode=args.mode,
                    retry_of_run_id=args.retry_of,
                )
            )
        elif args.command == "annotate":
            _json_print(
                annotate_run(
                    conn,
                    args.agent_id,
                    provider=args.provider,
                    lane=args.lane,
                    model_id=args.model_id,
                    model_alias=args.model_alias,
                    model_snapshot=args.model_snapshot,
                    reasoning_effort=args.reasoning,
                    task_kind=args.task_kind,
                    risk_class=args.risk,
                    read_write_mode=args.mode,
                    duration_ms=args.duration_ms,
                    cost_usd=args.cost_usd,
                    input_tokens=args.input_tokens,
                    output_tokens=args.output_tokens,
                )
            )
        elif args.command == "stop":
            _json_print(
                mark_stopped(
                    conn,
                    agent_id=args.agent_id,
                    agent_type=args.agent_type,
                    status=args.status,
                )
            )
        elif args.command == "finish":
            checks: Any = args.checks_json
            if args.check:
                checks = {}
                for item in args.check:
                    if "=" not in item:
                        raise ValueError("--check values must use key=value")
                    key, value = item.split("=", 1)
                    checks[key] = value
            _json_print(
                finish_evaluation(
                    conn,
                    agent_id=args.agent_id,
                    evaluator_type=args.evaluator_type,
                    evaluator_model=args.evaluator_model,
                    outcome=args.outcome,
                    correctness=args.correctness,
                    completeness=args.completeness,
                    judgment=args.judgment,
                    efficiency=args.efficiency,
                    confidence=args.confidence,
                    checks=checks,
                    note=args.note,
                    rubric_version=args.rubric_version,
                )
            )
        elif args.command == "recommend":
            _json_print(
                recommendation(
                    conn,
                    task_kind=args.task_kind,
                    risk_class=args.risk,
                    read_write_mode=args.mode,
                    lane=args.lane,
                    min_samples=args.min_samples,
                )
            )
        elif args.command == "leaderboard":
            _json_print(
                leaderboard_rows(
                    conn,
                    task_kind=args.task_kind,
                    lane=args.lane,
                    min_samples=args.min_samples,
                )
            )
        elif args.command == "pending":
            where = "WHERE status = 'pending_review'"
            params: list[Any] = []
            if args.session_id:
                where += " AND session_id = ?"
                params.append(args.session_id)
            _json_print(
                [
                    dict(row)
                    for row in conn.execute(f"SELECT * FROM subagent_runs {where}", params)
                ]
            )
        conn.close()
        return 0
    except Exception as exc:
        if args.command in {"hook-start", "hook-stop"}:
            print(f"agent-evals hook failed open: {exc}", file=sys.stderr)
            print("{}")
            return 0
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
