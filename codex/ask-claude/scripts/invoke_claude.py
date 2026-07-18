#!/usr/bin/env python3
"""Invoke Claude Code as a bounded read-only second-opinion agent."""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any


RESULT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["complete", "blocked", "uncertain"]},
        "summary": {"type": "string"},
        "answer": {"type": "string"},
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "severity": {
                        "type": "string",
                        "enum": ["critical", "high", "medium", "low", "info"],
                    },
                    "title": {"type": "string"},
                    "detail": {"type": "string"},
                    "evidence": {"type": "string"},
                    "recommendation": {"type": "string"},
                },
                "required": ["severity", "title", "detail", "evidence", "recommendation"],
                "additionalProperties": False,
            },
        },
        "checks": {"type": "array", "items": {"type": "string"}},
        "uncertainties": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["status", "summary", "answer", "findings", "checks", "uncertainties"],
    "additionalProperties": False,
}


def load_eval_module():
    skills_dir = Path(__file__).resolve().parents[2]
    module_path = skills_dir / "agent-evals" / "scripts" / "agent_evals.py"
    spec = importlib.util.spec_from_file_location("agent_evals_store", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load eval store: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extract_structured(payload: dict[str, Any]) -> Any:
    for key in ("structured_output", "structuredOutput"):
        if key in payload:
            return payload[key]
    result = payload.get("result")
    if isinstance(result, dict):
        return result
    if isinstance(result, str):
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {
                "status": "uncertain",
                "summary": result[:1000],
                "answer": result,
                "findings": [],
                "checks": [],
                "uncertainties": ["Claude did not return schema-valid structured output."],
            }
    return {
        "status": "uncertain",
        "summary": "Claude returned no structured result.",
        "answer": "",
        "findings": [],
        "checks": [],
        "uncertainties": ["Missing structured output."],
    }


def model_usage(payload: dict[str, Any]) -> dict[str, Any]:
    usage = payload.get("modelUsage") or payload.get("model_usage") or {}
    return usage if isinstance(usage, dict) else {}


def total_metric(usage: dict[str, Any], *keys: str) -> int | None:
    values = []
    for item in usage.values():
        if not isinstance(item, dict):
            continue
        for key in keys:
            if key in item and isinstance(item[key], (int, float)):
                values.append(int(item[key]))
                break
    return sum(values) if values else None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt-file", type=Path, required=True)
    parser.add_argument("--cwd", type=Path, default=Path.cwd())
    parser.add_argument("--task-kind", required=True)
    parser.add_argument("--risk", choices=["low", "medium", "high"], required=True)
    parser.add_argument("--model", default="opus")
    parser.add_argument("--effort", choices=["low", "medium", "high", "xhigh", "max"], default="high")
    parser.add_argument("--allow-web", action="store_true")
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--db", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    prompt_path = args.prompt_file.expanduser().resolve()
    cwd = args.cwd.expanduser().resolve()
    if not prompt_path.is_file():
        print(json.dumps({"error": f"Prompt file not found: {prompt_path}"}), file=sys.stderr)
        return 2
    if not cwd.is_dir():
        print(json.dumps({"error": f"Working directory not found: {cwd}"}), file=sys.stderr)
        return 2
    claude = shutil.which("claude")
    if not claude:
        print(json.dumps({"error": "Claude Code CLI is not installed or not on PATH."}), file=sys.stderr)
        return 2

    evals = load_eval_module()
    conn = evals.connect(args.db)
    agent_id = f"claude:{uuid.uuid4()}"
    run = evals.start_run(
        conn,
        agent_id=agent_id,
        agent_type="claude-code-readonly",
        provider="claude-code",
        lane="second_opinion",
        model_id=args.model,
        model_alias=args.model,
        reasoning_effort=args.effort,
        task_kind=args.task_kind,
        risk_class=args.risk,
        read_write_mode="read",
        metadata={"adapter_version": "1"},
    )

    tools = ["Read", "Glob", "Grep"]
    if args.allow_web:
        tools.extend(["WebSearch", "WebFetch"])
    contract = """

You are an independent second-opinion agent. Work read-only.
Do not edit files, run shell commands, create commits, send messages, or take external actions.
Inspect only the material needed for the request. Separate verified evidence from inference.
Return exactly the requested JSON schema. If evidence is insufficient, use status "uncertain"
or "blocked" instead of guessing.
"""
    prompt = prompt_path.read_text(encoding="utf-8") + contract
    command = [
        claude,
        "--print",
        "--output-format",
        "json",
        "--json-schema",
        json.dumps(RESULT_SCHEMA, separators=(",", ":")),
        "--model",
        args.model,
        "--effort",
        args.effort,
        "--permission-mode",
        "plan",
        "--safe-mode",
        "--no-session-persistence",
        "--tools",
        ",".join(tools),
        "--disallowed-tools",
        "Bash,Edit,Write,NotebookEdit",
    ]

    try:
        completed = subprocess.run(
            command,
            input=prompt,
            text=True,
            encoding="utf-8",
            capture_output=True,
            cwd=cwd,
            timeout=args.timeout,
            check=False,
        )
        if completed.returncode != 0:
            evals.mark_stopped(
                conn,
                agent_id=agent_id,
                agent_type="claude-code-readonly",
                status="failed",
                last_message=completed.stderr,
            )
            result = {
                "agent_id": agent_id,
                "run_id": run["run_id"],
                "status": "failed",
                "error": completed.stderr.strip()[:2000],
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return completed.returncode or 1

        payload = json.loads(completed.stdout)
        usage = model_usage(payload)
        actual_models = sorted(usage.keys())
        alias_matches = [
            model for model in actual_models if args.model.lower() in model.lower()
        ]
        if len(alias_matches) == 1:
            actual_model = alias_matches[0]
        elif len(actual_models) == 1:
            actual_model = actual_models[0]
        else:
            actual_model = args.model
        duration_ms = payload.get("duration_ms") or payload.get("durationMs")
        cost_usd = payload.get("total_cost_usd") or payload.get("totalCostUsd")
        input_tokens = total_metric(usage, "inputTokens", "input_tokens")
        output_tokens = total_metric(usage, "outputTokens", "output_tokens")
        evals.annotate_run(
            conn,
            agent_id,
            model_id=actual_model,
            model_alias=args.model,
            duration_ms=duration_ms,
            cost_usd=cost_usd,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            metadata={
                "actual_models": actual_models,
                "claude_session_id": payload.get("session_id") or payload.get("sessionId"),
            },
        )
        structured = extract_structured(payload)
        evals.mark_stopped(
            conn,
            agent_id=agent_id,
            agent_type="claude-code-readonly",
            status="pending_review",
            last_message=json.dumps(structured, ensure_ascii=False),
        )
        result = {
            "agent_id": agent_id,
            "run_id": run["run_id"],
            "status": "pending_review",
            "requested_model": args.model,
            "actual_models": actual_models,
            "reasoning_effort": args.effort,
            "duration_ms": duration_ms,
            "cost_usd": cost_usd,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "result": structured,
        }
        rendered = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output:
            output_path = args.output.expanduser().resolve()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(rendered + "\n", encoding="utf-8")
        print(rendered)
        return 0
    except subprocess.TimeoutExpired:
        evals.mark_stopped(
            conn,
            agent_id=agent_id,
            agent_type="claude-code-readonly",
            status="failed",
            last_message="Claude Code invocation timed out.",
        )
        print(
            json.dumps(
                {
                    "agent_id": agent_id,
                    "run_id": run["run_id"],
                    "status": "failed",
                    "error": f"Claude Code timed out after {args.timeout} seconds.",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 124
    except Exception as exc:
        evals.mark_stopped(
            conn,
            agent_id=agent_id,
            agent_type="claude-code-readonly",
            status="failed",
            last_message=str(exc),
        )
        print(
            json.dumps(
                {
                    "agent_id": agent_id,
                    "run_id": run["run_id"],
                    "status": "failed",
                    "error": str(exc),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
