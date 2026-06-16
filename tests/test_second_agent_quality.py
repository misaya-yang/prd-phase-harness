from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD = ROOT / "scripts" / "scaffold_harness_prd.py"


def run_scaffold(output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCAFFOLD),
            "--output",
            str(output),
            "--title",
            "Checkout Risk Review Harness",
            "--purpose",
            "Convert checkout risk work into a readable second-agent harness.",
            "--prefix",
            "CR",
            "--phase",
            "Baseline Audit",
            "--phase",
            "Checkout Risk API",
            "--phase",
            "Operator Review UI",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class SecondAgentQualityTests(unittest.TestCase):
    def scaffold(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        tmp = tempfile.TemporaryDirectory()
        output = Path(tmp.name) / "checkout_harness"
        result = run_scaffold(output)
        self.assertEqual(result.returncode, 0, result.stderr)
        return tmp, output

    def test_runtime_docs_are_actionable_without_bare_todos(self) -> None:
        tmp, output = self.scaffold()
        self.addCleanup(tmp.cleanup)

        runtime_files = [
            "README.md",
            "phase-manifest.md",
            "source-packet.md",
            "progress-log.md",
            "agent-handoff.md",
            "next-window-prompt.md",
            "continuity-ledger.md",
            "phase-00-baseline-audit.md",
            "phase-01-checkout-risk-api.md",
            "phase-02-operator-review-ui.md",
        ]
        for name in runtime_files:
            text = read(output / name)
            self.assertNotRegex(text, r"\bTODO\b", name)
            self.assertNotIn("{{", text, name)
            self.assertNotIn("}}", text, name)
            self.assertNotIn("none is not none", text, name)

    def test_next_window_prompt_contains_a_complete_second_agent_task_packet(self) -> None:
        tmp, output = self.scaffold()
        self.addCleanup(tmp.cleanup)

        prompt = read(output / "next-window-prompt.md")
        required_snippets = [
            "Target phase: CR-00",
            "Target phase file:",
            "Target feature-oracle item: CR-F001",
            "Open",
            "loop-contract.json",
            "loop-state.json",
            "feature-oracle.json",
            "continuity-ledger.md",
            "Work on exactly one phase and one feature-oracle item.",
            "Summarize code facts back into the source packet and continuity ledger",
            "Update the phase report, progress log, handoff file, continuity ledger, and oracle evidence",
        ]
        for snippet in required_snippets:
            self.assertIn(snippet, prompt)

    def test_handoff_progress_and_loop_state_agree_on_active_work(self) -> None:
        tmp, output = self.scaffold()
        self.addCleanup(tmp.cleanup)

        state = json.loads(read(output / "loop-state.json"))
        handoff = read(output / "agent-handoff.md")
        progress = read(output / "progress-log.md")
        oracle = json.loads(read(output / "feature-oracle.json"))
        first_feature = oracle["features"][0]

        self.assertEqual(state["active_phase"], "CR-00")
        self.assertEqual(state["active_feature"], "CR-F001")
        self.assertEqual(first_feature["id"], "CR-F001")
        self.assertEqual(first_feature["phase_id"], "CR-00")
        self.assertIn("Active role: planner", handoff)
        self.assertIn("Active feature-oracle item: CR-F001", handoff)
        self.assertIn("Required evidence before unlock:", handoff)
        self.assertIn("Active phase: CR-00", progress)
        self.assertIn("Active feature-oracle item: CR-F001", progress)

    def test_each_phase_declares_cross_phase_continuity_and_code_writeback(self) -> None:
        tmp, output = self.scaffold()
        self.addCleanup(tmp.cleanup)

        phases = [
            ("CR-00", "phase-00-baseline-audit.md", "none", "CR-01", "CR-F001"),
            ("CR-01", "phase-01-checkout-risk-api.md", "CR-00", "CR-02", "CR-F002"),
            ("CR-02", "phase-02-operator-review-ui.md", "CR-01", "none", "CR-F003"),
        ]
        for phase_id, file_name, depends_on, unlocks, feature_id in phases:
            text = read(output / file_name)
            self.assertIn("## Cross-Phase Continuity", text, file_name)
            self.assertIn(f"- Depends on: {depends_on}", text, file_name)
            self.assertIn(f"- Unlocks: {unlocks}", text, file_name)
            self.assertIn(f"- Feature-oracle item: {feature_id}", text, file_name)
            self.assertIn("## Code Summary Writeback", text, file_name)
            self.assertIn("source-packet.md", text, file_name)
            self.assertIn("continuity-ledger.md", text, file_name)
            self.assertIn("agent-handoff.md", text, file_name)
            self.assertRegex(text, rf"GOAL_PROMPT: Complete {phase_id} .*")

    def test_manifest_and_continuity_ledger_preserve_related_todo_chain(self) -> None:
        tmp, output = self.scaffold()
        self.addCleanup(tmp.cleanup)

        manifest = read(output / "phase-manifest.md")
        ledger = read(output / "continuity-ledger.md")
        self.assertIn("CR-00 Baseline Audit\n  -> CR-01 Checkout Risk API\n  -> CR-02 Operator Review UI", manifest)
        self.assertIn("| CR-00 | CR-F001 | none | CR-01 |", ledger)
        self.assertIn("| CR-01 | CR-F002 | CR-00 | CR-02 |", ledger)
        self.assertIn("| CR-02 | CR-F003 | CR-01 | none |", ledger)
        self.assertIn("Code Summary Writeback Rules", ledger)
        self.assertIn("Interface Boundary Ledger", ledger)


if __name__ == "__main__":
    unittest.main()
