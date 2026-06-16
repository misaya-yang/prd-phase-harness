from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD = ROOT / "scripts" / "scaffold_harness_prd.py"
VALIDATOR = ROOT / "scripts" / "validate_harness_prd.py"


def run_cmd(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=cwd or ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def write_minimal_harness(
    folder: Path,
    *,
    include_runtime_files: bool,
    oracle: dict | None = None,
    next_window_prompt: str | None = None,
) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "reports").mkdir()

    docs_path = str(folder)
    contract = {
        "schema_version": "prd-phase-harness/v3",
        "harness_role": "execution",
        "phase": {
            "id": "RT-00",
            "number": "00",
            "title": "Baseline Audit",
            "status": "ready",
            "type": "baseline",
            "repo_path": ".",
            "docs_path": docs_path,
            "phase_file": f"{docs_path}/phase-00-baseline-audit.md",
            "depends_on": [],
            "unlocks": [],
        },
        "goal": {
            "target": "Establish current system evidence before implementation.",
            "prompt": f"Complete RT-00 Baseline Audit for `.` by following `{docs_path}/phase-00-baseline-audit.md`; stay inside audit-only boundaries; finish only after validation, regression, compliance, rollback, evidence, and acceptance gates pass or blockers are documented.",
            "plan_required": True,
            "plan_output": f"{docs_path}/reports/rt-00-baseline-audit-plan.md",
            "completion_report": f"{docs_path}/reports/rt-00-baseline-audit-report.md",
        },
        "runtime": {
            "feature_oracle": f"{docs_path}/feature-oracle.json",
            "loop_contract": f"{docs_path}/loop-contract.json",
            "loop_state": f"{docs_path}/loop-state.json",
            "progress_log": f"{docs_path}/progress-log.md",
            "handoff": f"{docs_path}/agent-handoff.md",
            "next_window_prompt": f"{docs_path}/next-window-prompt.md",
            "session_boot": {
                "read_progress": True,
                "run_baseline_check": True,
                "update_progress_before_exit": True,
            },
            "agent_roles": ["planner", "generator", "evaluator"],
        },
        "context": {
            "read_first": [
                f"{docs_path}/README.md",
                f"{docs_path}/phase-manifest.md",
                f"{docs_path}/phase-00-baseline-audit.md",
            ],
            "primary_context": ["README.md", "scripts"],
            "context_budget": "focused",
            "do_not_load_unless": ["external dashboards"],
        },
        "boundaries": {
            "likely_edit_paths": ["docs/runtime-harness"],
            "do_not_edit": ["production systems"],
            "external_inputs": ["none"],
            "secrets_required": [],
        },
        "tool_policy": {
            "allowed_tools": ["repo search", "shell validation"],
            "approval_required": ["deployment"],
            "dangerous_commands": ["git reset --hard"],
        },
        "risk": {
            "tags": ["baseline"],
            "data_mutation": False,
            "migration_required": False,
            "browser_required": False,
            "ai_eval_required": False,
            "external_service_required": False,
            "release_blocking": False,
        },
        "validation": {
            "commands": [
                {
                    "id": "unit",
                    "cwd": ".",
                    "command": "python3 -m unittest discover tests",
                    "expected": "all tests pass",
                    "required": True,
                }
            ],
            "browser_checks": ["none for baseline"],
            "regression_scope": ["existing validator behavior remains stable"],
            "compliance_gates": ["no secrets are read or written"],
            "acceptance_gates": ["source packet and runtime files are present"],
            "rollback_plan": ["revert docs-only changes"],
        },
        "evidence": {
            "outputs": [f"{docs_path}/reports/rt-00-baseline-audit-report.md"],
            "required_artifacts": ["phase report", "progress log entry"],
            "waiver_policy": "Document waived gates with user, reason, risk, and dependent phase impact.",
            "next_phase_handoff": "Unlock only after the report states passed or waived.",
        },
        "stop_conditions": ["credentials are required"],
    }

    phase_text = f"""# Phase 00 - Baseline Audit

> For agentic workers: enter plan-first mode before editing.

**Goal:** Establish current system evidence before implementation.

**Architecture:** This phase records repo state and runtime evidence for later work.

**Tech Stack:** Python scripts, Markdown harness docs, JSON contracts.

---

## Machine Contract

```json
{json.dumps(contract, indent=2)}
```

## Coding Agent Contract

- PHASE_ID: RT-00
- GOAL_TARGET: Establish current system evidence before implementation.
- GOAL_PROMPT: Complete RT-00 Baseline Audit for `.` by following `{docs_path}/phase-00-baseline-audit.md`; stay inside audit-only boundaries; finish only after validation, regression, compliance, rollback, evidence, and acceptance gates pass or blockers are documented.
- DEPENDS_ON: none
- READ_FIRST: `{docs_path}/README.md`, `{docs_path}/phase-manifest.md`, this file
- PRIMARY_CONTEXT: README.md, scripts
- LIKELY_EDIT_PATHS: docs/runtime-harness
- DO_NOT_EDIT: production systems
- EXECUTION_MODE: plan-first; implement stepwise; verify before completion; write evidence before handoff
- VALIDATION_COMMANDS: python3 -m unittest discover tests
- BROWSER_CHECKS: none for baseline
- REGRESSION_SCOPE: existing validator behavior remains stable
- COMPLIANCE_GATES: no secrets are read or written
- ROLLBACK_PLAN: revert docs-only changes
- ACCEPTANCE_GATES: source packet and runtime files are present
- EVIDENCE_OUTPUT: `{docs_path}/reports/rt-00-baseline-audit-report.md`
- STOP_CONDITIONS: credentials are required

## Task Spec

Record baseline evidence for the harness.

## Problem Boundary

In scope:

- Inspect local harness files.

Out of scope:

- Deployments and production data.

## Context Policy

Before editing, inspect:

- README.md
- scripts

## Requirements

### R1 Baseline Evidence

Write evidence that future agents can load without hidden chat context.

## Test and Regression Requirements

Run `python3 -m unittest discover tests`.

## Compliance and Safety Requirements

Do not read secrets or mutate production data.

## Rollback and Recovery

Revert docs-only changes.

## Execution Capture

Write the phase report and progress-log update.

## Evaluator Protocol

Reject completion without report evidence and runtime files.

## Acceptance Criteria

- Runtime files exist.
- Report path is documented.

## Risks

- Missing runtime files could strand the next agent.
"""

    readme = """# Runtime Harness

## Harness Intent

Create an executable long-running agent harness.

## Coding Agent Loading Protocol

Open README, manifest, target phase, and runtime files before planning.

## Long-Running Runtime Protocol

Read progress, run baseline validation, work on one oracle item, and write handoff evidence.

## Source Packet

Source facts come from repository files.

## Runtime Artifacts

Feature oracle, progress log, handoff, and next-window prompt are required.

## Current System Shape

Python scripts generate and validate Markdown harness folders.

## Assumptions and Decisions

- The target repo is confirmed before execution.

## Phase Order

| Phase | Name | Core Outcome | Report |
| --- | --- | --- | --- |
| Phase 00 | Baseline Audit | Establish evidence | `reports/rt-00-baseline-audit-report.md` |

## New Window Prompt

Use `next-window-prompt.md` to restart a fresh agent window.

## Roadmap Cohesion

Baseline evidence unlocks implementation only after validator evidence exists.

## Shared Harness Rules

Plan before editing and write evidence before handoff.

## Global Non-Goals

- Production deployment.

## Global Compliance Gates

- Do not expose secrets.

## Standard Verification Commands

`python3 -m unittest discover tests`

## Required Browser or Runtime Checks

No browser checks for baseline.

## External Inputs and Approvals

No external approval is required for baseline.
"""
    manifest = f"""# Runtime Harness Phase Manifest

## Grep Usage

Use `rg -n "PHASE_ID: RT-00|GOAL_PROMPT" {docs_path}`.

## Phase Index

| PHASE_ID | File | Depends On | Goal Target | Main Validation | Evidence Output |
| --- | --- | --- | --- | --- | --- |
| RT-00 | `phase-00-baseline-audit.md` | none | Establish evidence | unit tests | `reports/rt-00-baseline-audit-report.md` |

## Phase Report Index

| PHASE_ID | Required Report |
| --- | --- |
| RT-00 | `reports/rt-00-baseline-audit-report.md` |

## Dependency Flow

RT-00 Baseline Audit

## Validation Matrix

| PHASE_ID | Mutates Data | Needs Browser/UI | Needs Agent/LLM Eval | Needs Migration | Needs External Service | Release Blocking |
| --- | --- | --- | --- | --- | --- | --- |
| RT-00 | no | no | no | no | no | no |

## Risk Matrix

| PHASE_ID | Primary Risk | Stop Condition |
| --- | --- | --- |
| RT-00 | missing evidence | credentials are required |

## Runtime Artifacts

| Artifact | Path | Agent Rule |
| --- | --- | --- |
| Loop Contract | `loop-contract.json` | run observe/select/execute/verify/record/decide |
| Loop State | `loop-state.json` | track active phase, feature, iteration, and decision |
| Feature Oracle | `feature-oracle.json` | update evidence only |
| Progress Log | `progress-log.md` | append session notes |
| Agent Handoff | `agent-handoff.md` | keep role handoffs concise |
| Next Window Prompt | `next-window-prompt.md` | restart fresh context |

## Agent Role Handoffs

- Planner writes contracts.
- Generator executes one item.
- Evaluator checks evidence.

## External Inputs Checklist

- No external inputs are required for baseline.

## Goal Setup Templates

Complete RT-00 Baseline Audit for `.` by following `{docs_path}/phase-00-baseline-audit.md`.

## Shared Agent Rules

Write the phase report before moving on.
"""

    (folder / "README.md").write_text(readme, encoding="utf-8")
    (folder / "phase-manifest.md").write_text(manifest, encoding="utf-8")
    (folder / "phase-00-baseline-audit.md").write_text(phase_text, encoding="utf-8")
    (folder / "reports" / "phase-report-template.md").write_text("# Report\n", encoding="utf-8")

    if include_runtime_files:
        (folder / "source-packet.md").write_text("# Source Packet\n\nRepo facts only.\n", encoding="utf-8")
        loop_contract = {
            "schema_version": "prd-phase-harness/loop-contract/v1",
            "goal": "Run one bounded phase until evidence proves pass, block, or fail.",
            "cycle": ["observe", "select", "execute", "verify", "record", "decide"],
            "max_iterations": 3,
            "state_file": f"{folder}/loop-state.json",
            "oracle_file": f"{folder}/feature-oracle.json",
            "done_when": [
                "selected phase report exists",
                "required validation evidence is recorded",
                "feature oracle status is passing, blocked, or waived",
            ],
            "continue_when": [
                "validator is clean",
                "work remains in the selected phase",
                "iteration is below max_iterations",
            ],
            "stop_when": [
                "credentials or approvals are missing",
                "validation fails outside phase scope",
                "edits outside boundary are required",
            ],
        }
        loop_state = {
            "schema_version": "prd-phase-harness/loop-state/v1",
            "active_phase": "RT-00",
            "active_feature": "RT-F001",
            "iteration": 0,
            "status": "planned",
            "last_decision": "start with baseline evidence",
            "next_action": "execute RT-00",
        }
        (folder / "loop-contract.json").write_text(json.dumps(loop_contract, indent=2), encoding="utf-8")
        (folder / "loop-state.json").write_text(json.dumps(loop_state, indent=2), encoding="utf-8")
        (folder / "progress-log.md").write_text("# Progress Log\n\n- Baseline pending.\n", encoding="utf-8")
        (folder / "agent-handoff.md").write_text("# Agent Handoff\n\nNext agent: run RT-00.\n", encoding="utf-8")
        prompt = next_window_prompt or f"""# Next Window Prompt

Use $prd-phase-harness to continue the harness at `{folder}`.

Target phase: RT-00
Target phase file: `{folder}/phase-00-baseline-audit.md`
Target feature-oracle item: RT-F001

Loading order:
1. Open `{folder}/README.md`.
2. Open `{folder}/phase-manifest.md`.
3. Open `{folder}/loop-contract.json`.
4. Open `{folder}/loop-state.json`.
5. Open `{folder}/feature-oracle.json`.
6. Open `{folder}/progress-log.md`.
7. Open `{folder}/agent-handoff.md`.
8. Open the target phase file and its PRIMARY_CONTEXT.

Execution rule:
- Work on exactly one phase and one feature-oracle item.
- Follow the loop cycle: observe, select, execute, verify, record, decide.
- Stay inside the phase edit boundaries.
- Run validation and runtime checks.
- Update the phase report, progress log, handoff file, and oracle evidence before claiming completion.

Stop conditions:
- Stop if credentials, production systems, destructive commands, or out-of-scope edits are required.
"""
        (folder / "next-window-prompt.md").write_text(prompt, encoding="utf-8")
        oracle_data = oracle or {
            "features": [
                {
                    "id": "RT-F001",
                    "phase_id": "RT-00",
                    "category": "runtime",
                    "description": "Harness runtime files are present.",
                    "steps": ["Open each runtime file.", "Confirm it has actionable content."],
                    "status": "failing",
                    "evidence": "",
                }
            ]
        }
        (folder / "feature-oracle.json").write_text(json.dumps(oracle_data, indent=2), encoding="utf-8")


class HarnessRuntimeTests(unittest.TestCase):
    def test_scaffold_emits_runtime_files_and_placeholder_validation_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "docs" / "runtime_harness"
            result = run_cmd(
                str(SCAFFOLD),
                "--output",
                str(output),
                "--title",
                "Runtime Harness",
                "--purpose",
                "Convert a rough request into a long-running agent harness.",
                "--prefix",
                "RT",
                "--phase",
                "Baseline Audit",
                "--phase",
                "Implementation Slice",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            for name in [
                "source-packet.md",
                "loop-contract.json",
                "loop-state.json",
                "feature-oracle.json",
                "progress-log.md",
                "agent-handoff.md",
                "next-window-prompt.md",
            ]:
                self.assertTrue((output / name).exists(), name)

            validation = run_cmd(str(VALIDATOR), str(output), "--allow-placeholders")
            self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)

    def test_strict_validation_requires_runtime_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(folder, include_runtime_files=False)

            result = run_cmd(str(VALIDATOR), str(folder), "--strict")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing runtime file: source-packet.md", result.stdout)
            self.assertIn("Missing runtime file: loop-contract.json", result.stdout)
            self.assertIn("Missing runtime file: loop-state.json", result.stdout)
            self.assertIn("Missing runtime file: feature-oracle.json", result.stdout)
            self.assertIn("Missing runtime file: progress-log.md", result.stdout)
            self.assertIn("Missing runtime file: agent-handoff.md", result.stdout)
            self.assertIn("Missing runtime file: next-window-prompt.md", result.stdout)

    def test_strict_validation_rejects_passing_oracle_without_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(
                folder,
                include_runtime_files=True,
                oracle={
                    "features": [
                        {
                            "id": "RT-F001",
                            "phase_id": "RT-00",
                            "category": "runtime",
                            "description": "Harness runtime files are present.",
                            "steps": ["Open each runtime file."],
                            "status": "passing",
                            "evidence": "",
                        }
                    ]
                },
            )

            result = run_cmd(str(VALIDATOR), str(folder), "--strict")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("feature-oracle.json feature RT-F001 is passing without evidence", result.stdout)

    def test_strict_validation_accepts_complete_runtime_harness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(folder, include_runtime_files=True)

            result = run_cmd(str(VALIDATOR), str(folder), "--strict", "--quality-score")

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Harness validation passed", result.stdout)

    def test_strict_validation_rejects_thin_next_window_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(
                folder,
                include_runtime_files=True,
                next_window_prompt="# Next Window Prompt\n\nComplete RT-00.\n",
            )

            result = run_cmd(str(VALIDATOR), str(folder), "--strict")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("next-window-prompt.md missing required prompt content", result.stdout)

    def test_strict_validation_rejects_orphan_oracle_phase(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(
                folder,
                include_runtime_files=True,
                oracle={
                    "features": [
                        {
                            "id": "RT-F001",
                            "phase_id": "RT-99",
                            "category": "runtime",
                            "description": "Harness runtime files are present.",
                            "steps": ["Open each runtime file."],
                            "status": "failing",
                            "evidence": "",
                        }
                    ]
                },
            )

            result = run_cmd(str(VALIDATOR), str(folder), "--strict")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("feature-oracle.json feature RT-F001 references unknown phase RT-99", result.stdout)

    def test_strict_validation_requires_oracle_coverage_for_each_phase(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(
                folder,
                include_runtime_files=True,
                oracle={
                    "features": [
                        {
                            "id": "RT-F999",
                            "phase_id": "RT-00",
                            "category": "runtime",
                            "description": "Harness runtime files are present.",
                            "steps": ["Open each runtime file."],
                            "status": "failing",
                            "evidence": "",
                        }
                    ]
                },
            )
            # Add a second executable phase that is intentionally not covered by the oracle.
            phase_two = (folder / "phase-00-baseline-audit.md").read_text(encoding="utf-8")
            phase_two = phase_two.replace("RT-00", "RT-01").replace("Phase 00", "Phase 01")
            phase_two = phase_two.replace("phase-00-baseline-audit", "phase-01-implementation-slice")
            phase_two = phase_two.replace('"number": "00"', '"number": "01"')
            (folder / "phase-01-implementation-slice.md").write_text(phase_two, encoding="utf-8")
            manifest_path = folder / "phase-manifest.md"
            manifest_text = manifest_path.read_text(encoding="utf-8")
            manifest_text = manifest_text.replace(
                "| RT-00 | `phase-00-baseline-audit.md` | none | Establish evidence | unit tests | `reports/rt-00-baseline-audit-report.md` |",
                "| RT-00 | `phase-00-baseline-audit.md` | none | Establish evidence | unit tests | `reports/rt-00-baseline-audit-report.md` |\n"
                "| RT-01 | `phase-01-implementation-slice.md` | RT-00 | Implement slice | unit tests | `reports/rt-01-baseline-audit-report.md` |",
            )
            manifest_text = manifest_text.replace(
                "| RT-00 | `reports/rt-00-baseline-audit-report.md` |",
                "| RT-00 | `reports/rt-00-baseline-audit-report.md` |\n"
                "| RT-01 | `reports/rt-01-baseline-audit-report.md` |",
            )
            manifest_path.write_text(manifest_text, encoding="utf-8")

            result = run_cmd(str(VALIDATOR), str(folder), "--strict")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("feature-oracle.json has no feature for phase RT-01", result.stdout)

    def test_strict_validation_rejects_incomplete_loop_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(folder, include_runtime_files=True)
            (folder / "loop-contract.json").write_text(
                json.dumps(
                    {
                        "schema_version": "prd-phase-harness/loop-contract/v1",
                        "goal": "Run a loop.",
                        "cycle": ["observe", "select", "execute"],
                        "max_iterations": 3,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            result = run_cmd(str(VALIDATOR), str(folder), "--strict")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("loop-contract.json missing cycle step: verify", result.stdout)
            self.assertIn("loop-contract.json missing cycle step: record", result.stdout)
            self.assertIn("loop-contract.json missing cycle step: decide", result.stdout)

    def test_strict_validation_rejects_loop_state_orphan_feature(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(folder, include_runtime_files=True)
            state = json.loads((folder / "loop-state.json").read_text(encoding="utf-8"))
            state["active_feature"] = "RT-F999"
            (folder / "loop-state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")

            result = run_cmd(str(VALIDATOR), str(folder), "--strict")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("loop-state.json active_feature RT-F999 is not in feature-oracle.json", result.stdout)


if __name__ == "__main__":
    unittest.main()
