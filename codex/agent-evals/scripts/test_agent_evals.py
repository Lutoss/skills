from __future__ import annotations

import importlib.util
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("agent_evals.py")
SPEC = importlib.util.spec_from_file_location("agent_evals_under_test", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
agent_evals = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agent_evals)


class AgentEvalsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.db = Path(self.tempdir.name) / "evals.sqlite3"
        conn = agent_evals.connect(self.db)
        conn.close()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_start_stop_finish_and_privacy_hashes(self) -> None:
        conn = agent_evals.connect(self.db)
        run = agent_evals.start_run(
            conn,
            agent_id="agent-1",
            agent_type="explorer-terra",
            model_id="gpt-5.6-terra",
            reasoning_effort="medium",
            task_kind="codebase_exploration",
            risk_class="low",
            read_write_mode="read",
        )
        self.assertEqual(run["status"], "running")
        stopped = agent_evals.mark_stopped(
            conn,
            agent_id="agent-1",
            last_message="private result text",
        )
        self.assertEqual(stopped["status"], "pending_review")
        self.assertNotIn("private result text", stopped["last_message_hash"])
        evaluation = agent_evals.finish_evaluation(
            conn,
            agent_id="agent-1",
            evaluator_type="parent_agent",
            outcome="accepted",
            correctness=5,
            completeness=5,
            judgment=4,
            efficiency=5,
            confidence=0.9,
            checks={"references": "pass"},
        )
        self.assertEqual(evaluation["outcome"], "accepted")
        status = conn.execute(
            "SELECT status FROM subagent_runs WHERE agent_id='agent-1'"
        ).fetchone()[0]
        self.assertEqual(status, "evaluated")
        conn.close()

    def test_empirical_recommendation_requires_minimum_samples(self) -> None:
        conn = agent_evals.connect(self.db)
        for index in range(5):
            agent_id = f"terra-{index}"
            agent_evals.start_run(
                conn,
                agent_id=agent_id,
                agent_type="explorer-terra",
                model_id="gpt-5.6-terra",
                reasoning_effort="medium",
                task_kind="research_primary_sources",
                risk_class="low",
                read_write_mode="read",
            )
            agent_evals.mark_stopped(conn, agent_id=agent_id)
            agent_evals.finish_evaluation(
                conn,
                agent_id=agent_id,
                evaluator_type="parent_agent",
                outcome="accepted",
                correctness=5,
                completeness=4,
                judgment=4,
                efficiency=5,
                confidence=0.9,
            )
        result = agent_evals.recommendation(
            conn,
            task_kind="research_primary_sources",
            risk_class="low",
            read_write_mode="read",
            lane="primary",
            min_samples=5,
        )
        self.assertEqual(result["source"], "empirical")
        self.assertEqual(result["model_id"], "gpt-5.6-terra")
        conn.close()

    def test_parallel_writes(self) -> None:
        def write(index: int) -> None:
            conn = agent_evals.connect(self.db)
            agent_id = f"parallel-{index}"
            agent_evals.start_run(
                conn,
                agent_id=agent_id,
                agent_type="worker-sol",
                model_id="gpt-5.6-sol",
                reasoning_effort="high",
                task_kind="implementation_clear_spec",
                risk_class="medium",
                read_write_mode="write",
            )
            agent_evals.mark_stopped(conn, agent_id=agent_id)
            agent_evals.finish_evaluation(
                conn,
                agent_id=agent_id,
                evaluator_type="deterministic",
                outcome="accepted",
                correctness=5,
                completeness=5,
                judgment=4,
                efficiency=4,
                confidence=1.0,
            )
            conn.close()

        with ThreadPoolExecutor(max_workers=6) as executor:
            list(executor.map(write, range(12)))
        conn = agent_evals.connect(self.db)
        count = conn.execute(
            "SELECT COUNT(*) FROM subagent_runs WHERE agent_id LIKE 'parallel-%'"
        ).fetchone()[0]
        self.assertEqual(count, 12)
        conn.close()

    def test_rejects_invalid_checks_json(self) -> None:
        conn = agent_evals.connect(self.db)
        agent_evals.start_run(conn, agent_id="bad-checks", agent_type="tester")
        with self.assertRaisesRegex(ValueError, "valid JSON"):
            agent_evals.finish_evaluation(
                conn,
                agent_id="bad-checks",
                evaluator_type="parent_agent",
                outcome="accepted",
                correctness=5,
                completeness=5,
                judgment=5,
                efficiency=5,
                confidence=1.0,
                checks="{not-json}",
            )
        conn.close()


if __name__ == "__main__":
    unittest.main()
