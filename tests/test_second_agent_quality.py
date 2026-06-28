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
            "context-profile.json",
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
            "context-profile.json",
            "loop-state.json",
            "Work on exactly one phase and one feature-oracle item.",
            "Summarize code facts back into targeted source-packet and continuity-ledger sections",
            "Update the phase report, progress log, handoff file, continuity ledger, and oracle evidence",
            "independent critic/subagent",
            "Treat `--strict` as structure readiness only",
            "--completion-gate --phase CR-00",
            "Preserve progressive disclosure",
        ]
        for snippet in required_snippets:
            self.assertIn(snippet, prompt)
        self.assertNotIn("Open `", prompt.split("Execution rule:", 1)[0].replace("Open `", "", 3))

    def test_scaffold_uses_repo_validation_discovery_not_python_unit_default(self) -> None:
        tmp, output = self.scaffold()
        self.addCleanup(tmp.cleanup)

        readme = read(output / "README.md")
        phase = read(output / "phase-00-baseline-audit.md")
        combined = readme + phase

        self.assertNotIn("python3 -m unittest discover tests", combined)
        self.assertIn("Starter validation discovery command", readme)
        self.assertIn("This command is not completion evidence by itself", readme)

        # The discovery command lives in the phase's single JSON contract.
        match = re.search(r"## Machine Contract.*?```json\s*(.*?)\s*```", phase, re.DOTALL)
        self.assertIsNotNone(match)
        contract = json.loads(match.group(1))
        command = contract["validation"]["commands"][0]
        self.assertEqual(command["id"], "repo-validation-discovery")
        self.assertTrue(command["command"].startswith("rg --files"))
        self.assertIn("package.json", command["command"])
        self.assertIn("baseline report records the concrete", command["expected"])

    def test_handoff_progress_and_loop_state_agree_on_active_work(self) -> None:
        tmp, output = self.scaffold()
        self.addCleanup(tmp.cleanup)

        state = json.loads(read(output / "loop-state.json"))
        profile = json.loads(read(output / "context-profile.json"))
        handoff = read(output / "agent-handoff.md")
        critic_template = read(output / "reports" / "critic-verdict-template.md")
        progress = read(output / "progress-log.md")
        oracle = json.loads(read(output / "feature-oracle.json"))
        first_feature = oracle["features"][0]

        self.assertEqual(state["active_phase"], "CR-00")
        self.assertEqual(state["active_feature"], "CR-F001")
        self.assertIn("progressive disclosure", profile["strategy"])
        self.assertLessEqual(len(profile["cold_start"]["required_files"]), 3)
        self.assertIn("source-packet.md", json.dumps(profile["deferred"]))
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
            # Cross-phase cohesion now lives in a compact grep header instead of
            # repeated prose sections.
            self.assertIn(f"- PHASE_ID: {phase_id}", text, file_name)
            self.assertIn(f"- DEPENDS_ON: {depends_on}", text, file_name)
            self.assertIn(f"- UNLOCKS: {unlocks}", text, file_name)
            self.assertIn(f"- FEATURE: {feature_id}", text, file_name)

            # The single JSON contract still mandates code-summary writeback and
            # carries the runnable goal prompt and dependency wiring.
            match = re.search(r"## Machine Contract.*?```json\s*(.*?)\s*```", text, re.DOTALL)
            self.assertIsNotNone(match, file_name)
            contract = json.loads(match.group(1))
            self.assertTrue(contract["goal"]["prompt"].startswith(f"Complete {phase_id} "), file_name)
            artifacts = " ".join(contract["evidence"]["required_artifacts"]).lower()
            self.assertIn("continuity-ledger", artifacts, file_name)
            self.assertIn("source-packet", artifacts, file_name)
            self.assertIn("handoff", artifacts, file_name)
            self.assertEqual(contract["phase"]["depends_on"], [] if depends_on == "none" else [depends_on], file_name)
            self.assertEqual(contract["phase"]["unlocks"], [] if unlocks == "none" else [unlocks], file_name)

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

    def test_scaffold_embeds_long_cycle_delivery_quality_gates(self) -> None:
        tmp, output = self.scaffold()
        self.addCleanup(tmp.cleanup)

        readme = read(output / "README.md")
        manifest = read(output / "phase-manifest.md")
        handoff = read(output / "agent-handoff.md")
        source_packet = read(output / "source-packet.md")
        context_profile = read(output / "context-profile.json")
        critic_template = read(output / "reports" / "critic-verdict-template.md")
        first_phase = read(output / "phase-00-baseline-audit.md")
        final_phase = read(output / "phase-02-operator-review-ui.md")

        for text in [readme, manifest, handoff, source_packet, final_phase]:
            self.assertIn("whole-demand regression", text)
            self.assertIn("critic", text.lower())
        self.assertIn("progressive disclosure", context_profile)
        self.assertIn("critic", context_profile.lower())

        self.assertNotIn("whole-demand regression", first_phase)
        self.assertIn("context compaction", readme)
        self.assertIn("context-profile.json", readme)
        self.assertIn("Load first", manifest)
        self.assertIn("`--strict` is structure readiness, not completion proof", readme)
        self.assertIn("--completion-gate", manifest)
        self.assertIn("blocked/partial report", handoff)
        self.assertIn("Critic Verdict", critic_template)
        self.assertIn("Actor Report Reviewed", critic_template)
        self.assertIn("independent", critic_template)
        self.assertIn("smallest requirement-satisfying change", readme)
        self.assertIn("Requirements and Gate Map", source_packet)
        self.assertIn("Delivery Quality Gates", manifest)
        self.assertIn("minimal-change scope", handoff)

        match = re.search(r"## Machine Contract.*?```json\s*(.*?)\s*```", final_phase, re.DOTALL)
        self.assertIsNotNone(match)
        contract = json.loads(match.group(1))
        acceptance = " ".join(contract["validation"]["acceptance_gates"])
        regression = " ".join(contract["validation"]["regression_scope"])
        artifacts = " ".join(contract["evidence"]["required_artifacts"])
        self.assertIn("whole-demand regression", acceptance)
        self.assertIn("critic", acceptance)
        self.assertIn("context compaction", acceptance)
        self.assertIn("whole-demand regression", regression)
        self.assertIn("critic evidence", artifacts)
        self.assertIn("minimal-change scope note", artifacts)


if __name__ == "__main__":
    unittest.main()
