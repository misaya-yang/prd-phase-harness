from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable


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


def update_phase_contract(phase_path: Path, update: Callable[[dict[str, Any]], None]) -> None:
    text = phase_path.read_text(encoding="utf-8")
    match = re.search(r"## Machine Contract.*?```json\s*(.*?)\s*```", text, re.DOTALL)
    if not match:
        raise AssertionError(f"Missing Machine Contract in {phase_path}")
    contract = json.loads(match.group(1))
    update(contract)
    phase_path.write_text(
        text[: match.start(1)] + json.dumps(contract, indent=2) + text[match.end(1) :],
        encoding="utf-8",
    )


def actor_report_text(status: str = "passed", *, whole_demand: bool = False) -> str:
    whole = (
        "\n## Whole-Demand Regression\n\n"
        "whole-demand regression: passed for all completed feature-oracle items, including RT-F001.\n"
        if whole_demand
        else ""
    )
    return (
        "# RT-00 Actor Report\n\n"
        f"**Status:** {status}\n\n"
        "## Summary\n\n"
        "The actor completed the bounded phase work and recorded durable evidence for critic review.\n\n"
        "## Validation Evidence\n\n"
        "| Gate | Command or Check | Result | Notes |\n"
        "| --- | --- | --- | --- |\n"
        "| Unit | python3 -m unittest discover tests | passed | Output captured in this report. |\n"
        "| Regression | targeted harness regression | passed | Existing runtime behavior stayed stable. |\n\n"
        "## Minimal Change and Review\n\n"
        "Changed files stayed inside the phase boundary. No unrelated refactor, rename, or public contract change was included.\n\n"
        "## Feature Oracle Updates\n\n"
        "| Feature ID | Old Status | New Status | Evidence |\n"
        "| --- | --- | --- | --- |\n"
        "| RT-F001 | failing | passing | Actor report plus independent critic artifact. |\n"
        f"{whole}"
    )


def critic_report_text(
    actor_report: Path,
    *,
    verdict: str = "approved",
    include_actor_report: bool = True,
    whole_demand: bool = False,
) -> str:
    actor_line = f"Actor Report Reviewed: {actor_report}\n\n" if include_actor_report else ""
    whole = (
        "Whole-demand regression reviewed: whole-demand regression evidence was present and coherent.\n\n"
        if whole_demand
        else ""
    )
    return (
        "# RT-00 Critic Review\n\n"
        "Critic: independent-subagent\n\n"
        f"Critic Verdict: {verdict}\n\n"
        "Phase: RT-00\n\n"
        "Feature: RT-F001\n\n"
        f"{actor_line}"
        "Findings: actor report, changed-file scope, validation evidence, feature oracle status, and regression impact were reviewed.\n\n"
        f"{whole}"
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
            "context_profile": f"{docs_path}/context-profile.json",
            "feature_oracle": f"{docs_path}/feature-oracle.json",
            "loop_contract": f"{docs_path}/loop-contract.json",
            "loop_state": f"{docs_path}/loop-state.json",
            "progress_log": f"{docs_path}/progress-log.md",
            "handoff": f"{docs_path}/agent-handoff.md",
            "continuity_ledger": f"{docs_path}/continuity-ledger.md",
            "next_window_prompt": f"{docs_path}/next-window-prompt.md",
            "session_boot": {
                "read_progress": True,
                "run_baseline_check": True,
                "update_progress_before_exit": True,
            },
            "agent_roles": ["planner", "generator", "critic"],
        },
        "context": {
            "read_first": [
                f"{docs_path}/loop-state.json",
                f"{docs_path}/context-profile.json",
                f"{docs_path}/phase-00-baseline-audit.md",
            ],
            "primary_context": ["README.md", "scripts"],
            "context_budget": "focused",
            "do_not_load_unless": [
                "source-packet.md only for targeted lookup or writeback",
                "continuity-ledger.md only for dependency boundary lookup or writeback",
                "feature-oracle.json only for selected feature item",
                "progress-log.md only when status history is unclear",
                "external dashboards only after approval",
            ],
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
            "regression_scope": [
                "existing validator behavior remains stable",
                "terminal whole-demand regression covers completed feature-oracle items",
            ],
            "compliance_gates": ["no secrets are read or written"],
            "acceptance_gates": [
                "source packet and runtime files are present",
                "independent critic evidence confirms requirement coverage",
                "minimal-change scope note is recorded",
                "whole-demand regression is recorded for terminal completion",
            ],
            "rollback_plan": ["revert docs-only changes"],
        },
        "evidence": {
            "outputs": [f"{docs_path}/reports/rt-00-baseline-audit-report.md"],
            "required_artifacts": [
                "phase report",
                "progress log entry",
                "feature-oracle evidence",
                "continuity-ledger update",
                "source-packet code summary",
                "handoff update",
                "independent critic evidence",
                "minimal-change scope note",
            ],
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
- GOAL_PROMPT: Complete RT-00 Baseline Audit for `.` by following `{docs_path}/phase-00-baseline-audit.md`; stay inside audit-only boundaries; finish only after validation, regression, review, compliance, rollback, evidence, and acceptance gates pass or blockers are documented.
- DEPENDS_ON: none
- READ_FIRST: `{docs_path}/context-profile.json`, `{docs_path}/loop-state.json`, this file
- PRIMARY_CONTEXT: README.md, scripts
- LIKELY_EDIT_PATHS: docs/runtime-harness
- DO_NOT_EDIT: production systems
- EXECUTION_MODE: plan-first; implement stepwise; verify before completion; write evidence before handoff
- VALIDATION_COMMANDS: python3 -m unittest discover tests
- BROWSER_CHECKS: none for baseline
- REGRESSION_SCOPE: existing validator behavior remains stable; terminal whole-demand regression covers completed feature-oracle items
- COMPLIANCE_GATES: no secrets are read or written
- ROLLBACK_PLAN: revert docs-only changes
- ACCEPTANCE_GATES: source packet and runtime files are present; independent critic evidence confirms requirement coverage; minimal-change scope note is recorded; whole-demand regression is recorded for terminal completion
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

Run `python3 -m unittest discover tests` and record independent critic evidence, minimal-change scope, and terminal whole-demand regression.

## Compliance and Safety Requirements

Do not read secrets or mutate production data.

## Rollback and Recovery

Revert docs-only changes.

## Execution Capture

Write the phase report and progress-log update.

## Critic Protocol

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

Open context profile, loop state, and target phase before planning; defer broad runtime files.

## Long-Running Runtime Protocol

Read progress, run baseline validation, work on one oracle item, and write handoff evidence.

## Source Packet

Source facts come from repository files.

## Runtime Artifacts

Context profile, feature oracle, progress log, handoff, continuity ledger, and next-window prompt are required.

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
| Context Profile | `context-profile.json` | load first and follow progressive disclosure |
| Loop Contract | `loop-contract.json` | run observe/select/execute/verify/record/decide |
| Loop State | `loop-state.json` | track active phase, feature, iteration, and decision |
| Feature Oracle | `feature-oracle.json` | update evidence only |
| Progress Log | `progress-log.md` | append session notes |
| Agent Handoff | `agent-handoff.md` | keep role handoffs concise |
| Continuity Ledger | `continuity-ledger.md` | preserve phase boundaries |
| Next Window Prompt | `next-window-prompt.md` | restart fresh context |

## Agent Role Handoffs

- Planner writes contracts.
- Generator executes one item.
- Critic checks evidence.

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
        context_profile = {
            "schema_version": "prd-phase-harness/context-profile/v1",
            "strategy": "progressive disclosure for runtime harness tests",
            "caps": {
                "cold_start_max_files": 3,
                "read_first_max_files": 4,
                "primary_context_max_items": 4,
            },
            "cold_start": {
                "required_files": [
                    f"{folder}/context-profile.json",
                    f"{folder}/loop-state.json",
                    "target phase file",
                ],
                "rule": "Do not load the full docs folder or every runtime artifact during cold start.",
            },
            "roles": {
                "actor": {
                    "required_files": [
                        f"{folder}/context-profile.json",
                        f"{folder}/loop-state.json",
                        "target phase file",
                    ],
                    "primary_context": ["README.md", "scripts"],
                    "defer": [f"{folder}/source-packet.md", f"{folder}/continuity-ledger.md"],
                },
                "critic": {
                    "required_files": ["actor report", "critic-verdict template", "target phase file"],
                    "primary_context": ["changed files or diff", "validation evidence"],
                },
            },
            "deferred": {
                "README.md": "do not load by default; open only when intent is unclear",
                "phase-manifest.md": "do not load by default; open only when target phase is unknown",
                "source-packet.md": "do not load by default; open only named sections for code fact lookup or writeback",
                "loop-contract.json": "do not load by default; open only if loop semantics are unclear",
                "feature-oracle.json": "do not load whole file by default; inspect only the selected feature item",
                "progress-log.md": "do not load whole file by default; inspect only recent entries when blockers or status are unclear",
                "agent-handoff.md": "do not load by default; open only when next action is unclear",
                "continuity-ledger.md": "do not load whole file by default; inspect only dependency rows or writeback sections",
                "next-window-prompt.md": "do not load by default; open only when preparing a fresh context window",
            },
        }
        (folder / "context-profile.json").write_text(json.dumps(context_profile, indent=2), encoding="utf-8")
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
        (folder / "continuity-ledger.md").write_text(
            "# Continuity Ledger\n\nRT-00 links RT-F001 to baseline evidence.\n",
            encoding="utf-8",
        )
        prompt = next_window_prompt or f"""# Next Window Prompt

Use $prd-phase-harness to continue the harness at `{folder}`.

Target phase: RT-00
Target phase file: `{folder}/phase-00-baseline-audit.md`
Target feature-oracle item: RT-F001

Loading order:
1. Open `{folder}/context-profile.json`.
2. Open `{folder}/loop-state.json`.
3. Open `{folder}/phase-00-baseline-audit.md`.
4. Do not load README, manifest, full source packet, full oracle, progress log, handoff, continuity ledger, or prior reports unless the context profile trigger applies.

Execution rule:
- Work on exactly one phase and one feature-oracle item.
- Follow the loop cycle: observe, select, execute, verify, record, decide.
- Stay inside the phase edit boundaries.
- Run validation and runtime checks.
- Summarize code facts into the source packet and continuity ledger.
- Update the phase report, progress log, handoff file, continuity ledger, and oracle evidence before claiming completion.
- Preserve progressive disclosure and open deferred files only when the trigger applies.

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
                "context-profile.json",
                "source-packet.md",
                "loop-contract.json",
                "loop-state.json",
                "feature-oracle.json",
                "progress-log.md",
                "agent-handoff.md",
                "continuity-ledger.md",
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
            self.assertIn("Missing runtime file: context-profile.json", result.stdout)
            self.assertIn("Missing runtime file: source-packet.md", result.stdout)
            self.assertIn("Missing runtime file: loop-contract.json", result.stdout)
            self.assertIn("Missing runtime file: loop-state.json", result.stdout)
            self.assertIn("Missing runtime file: feature-oracle.json", result.stdout)
            self.assertIn("Missing runtime file: progress-log.md", result.stdout)
            self.assertIn("Missing runtime file: agent-handoff.md", result.stdout)
            self.assertIn("Missing runtime file: continuity-ledger.md", result.stdout)
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

    def test_completion_gate_accepts_verified_feature_and_passed_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(folder, include_runtime_files=True)
            report_path = folder / "reports" / "rt-00-baseline-audit-report.md"
            report_path.write_text(actor_report_text(whole_demand=True), encoding="utf-8")
            critic_path = folder / "reports" / "rt-00-critic-review.md"
            critic_path.write_text(critic_report_text(report_path, whole_demand=True), encoding="utf-8")
            oracle = json.loads((folder / "feature-oracle.json").read_text(encoding="utf-8"))
            oracle["features"][0]["status"] = "passing"
            oracle["features"][0]["evidence"] = [str(report_path), str(critic_path)]
            (folder / "feature-oracle.json").write_text(json.dumps(oracle, indent=2), encoding="utf-8")
            state = json.loads((folder / "loop-state.json").read_text(encoding="utf-8"))
            state["status"] = "verified"
            (folder / "loop-state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")

            result = run_cmd(str(VALIDATOR), str(folder), "--strict", "--completion-gate", "--quality-score")

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Harness validation passed", result.stdout)

    def test_completion_gate_rejects_unfinished_oracle_and_running_loop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(folder, include_runtime_files=True)

            result = run_cmd(str(VALIDATOR), str(folder), "--strict", "--completion-gate")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("completion gate requires loop-state.status verified or waived; found planned", result.stdout)
            self.assertIn("completion gate requires feature RT-F001 (RT-00) to be passing or waived; found failing", result.stdout)
            self.assertIn("completion gate requires feature RT-F001 to cite report and critic artifacts", result.stdout)

    def test_completion_gate_rejects_passing_feature_with_blocked_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(folder, include_runtime_files=True)
            report_path = folder / "reports" / "rt-00-baseline-audit-report.md"
            report_path.write_text(actor_report_text(status="blocked"), encoding="utf-8")
            critic_path = folder / "reports" / "rt-00-critic-review.md"
            critic_path.write_text(critic_report_text(report_path), encoding="utf-8")
            oracle = json.loads((folder / "feature-oracle.json").read_text(encoding="utf-8"))
            oracle["features"][0]["status"] = "passing"
            oracle["features"][0]["evidence"] = [str(report_path), str(critic_path)]
            (folder / "feature-oracle.json").write_text(json.dumps(oracle, indent=2), encoding="utf-8")
            state = json.loads((folder / "loop-state.json").read_text(encoding="utf-8"))
            state["status"] = "verified"
            (folder / "loop-state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")

            result = run_cmd(str(VALIDATOR), str(folder), "--strict", "--completion-gate", "--quality-score")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("completion gate feature RT-F001 cites incomplete report", result.stdout)
            self.assertIn("blocked", result.stdout)
            self.assertIn("Quality score: 49 (not-ready)", result.stdout)

    def test_completion_gate_rejects_actor_report_without_critic_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(folder, include_runtime_files=True)
            report_path = folder / "reports" / "rt-00-baseline-audit-report.md"
            report_path.write_text(actor_report_text(whole_demand=True), encoding="utf-8")
            oracle = json.loads((folder / "feature-oracle.json").read_text(encoding="utf-8"))
            oracle["features"][0]["status"] = "passing"
            oracle["features"][0]["evidence"] = str(report_path)
            (folder / "feature-oracle.json").write_text(json.dumps(oracle, indent=2), encoding="utf-8")
            state = json.loads((folder / "loop-state.json").read_text(encoding="utf-8"))
            state["status"] = "verified"
            (folder / "loop-state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")

            result = run_cmd(str(VALIDATOR), str(folder), "--strict", "--completion-gate")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("completion gate requires feature RT-F001 to cite an independent critic artifact", result.stdout)

    def test_completion_gate_rejects_critic_changes_requested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(folder, include_runtime_files=True)
            report_path = folder / "reports" / "rt-00-baseline-audit-report.md"
            report_path.write_text(actor_report_text(whole_demand=True), encoding="utf-8")
            critic_path = folder / "reports" / "rt-00-critic-review.md"
            critic_path.write_text(critic_report_text(report_path, verdict="changes requested"), encoding="utf-8")
            oracle = json.loads((folder / "feature-oracle.json").read_text(encoding="utf-8"))
            oracle["features"][0]["status"] = "passing"
            oracle["features"][0]["evidence"] = [str(report_path), str(critic_path)]
            (folder / "feature-oracle.json").write_text(json.dumps(oracle, indent=2), encoding="utf-8")
            state = json.loads((folder / "loop-state.json").read_text(encoding="utf-8"))
            state["status"] = "verified"
            (folder / "loop-state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")

            result = run_cmd(str(VALIDATOR), str(folder), "--strict", "--completion-gate")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("completion gate critic rejected feature RT-F001", result.stdout)
            self.assertIn("changes_requested", result.stdout)

    def test_completion_gate_rejects_actor_report_with_embedded_critic_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(folder, include_runtime_files=True)
            report_path = folder / "reports" / "rt-00-baseline-audit-report.md"
            report_path.write_text(
                actor_report_text()
                + "\nCritic: independent-subagent\n\n"
                + "Critic Verdict: approved\n\n"
                + "Phase: RT-00\n\n"
                + "Feature: RT-F001\n\n",
                encoding="utf-8",
            )
            oracle = json.loads((folder / "feature-oracle.json").read_text(encoding="utf-8"))
            oracle["features"][0]["status"] = "passing"
            oracle["features"][0]["evidence"] = str(report_path)
            (folder / "feature-oracle.json").write_text(json.dumps(oracle, indent=2), encoding="utf-8")

            result = run_cmd(str(VALIDATOR), str(folder), "--strict", "--completion-gate", "--phase", "RT-00")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("requires separate actor and critic artifacts", result.stdout)

    def test_completion_gate_rejects_evidence_thin_actor_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(folder, include_runtime_files=True)
            report_path = folder / "reports" / "rt-00-baseline-audit-report.md"
            critic_path = folder / "reports" / "rt-00-critic-review.md"
            report_path.write_text("# RT-00 Report\n\n**Status:** passed\n", encoding="utf-8")
            critic_path.write_text(critic_report_text(report_path), encoding="utf-8")
            oracle = json.loads((folder / "feature-oracle.json").read_text(encoding="utf-8"))
            oracle["features"][0]["status"] = "passing"
            oracle["features"][0]["evidence"] = [str(report_path), str(critic_path)]
            (folder / "feature-oracle.json").write_text(json.dumps(oracle, indent=2), encoding="utf-8")

            result = run_cmd(str(VALIDATOR), str(folder), "--strict", "--completion-gate", "--phase", "RT-00")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("actor report for feature RT-F001 is evidence-thin", result.stdout)

    def test_completion_gate_rejects_critic_without_actor_report_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(folder, include_runtime_files=True)
            report_path = folder / "reports" / "rt-00-baseline-audit-report.md"
            critic_path = folder / "reports" / "rt-00-critic-review.md"
            report_path.write_text(actor_report_text(), encoding="utf-8")
            critic_path.write_text(
                critic_report_text(report_path, include_actor_report=False),
                encoding="utf-8",
            )
            oracle = json.loads((folder / "feature-oracle.json").read_text(encoding="utf-8"))
            oracle["features"][0]["status"] = "passing"
            oracle["features"][0]["evidence"] = [str(report_path), str(critic_path)]
            (folder / "feature-oracle.json").write_text(json.dumps(oracle, indent=2), encoding="utf-8")

            result = run_cmd(str(VALIDATOR), str(folder), "--strict", "--completion-gate", "--phase", "RT-00")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must reference the reviewed actor report path", result.stdout)

    def test_full_completion_gate_rejects_missing_terminal_whole_demand_regression(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(folder, include_runtime_files=True)
            report_path = folder / "reports" / "rt-00-baseline-audit-report.md"
            critic_path = folder / "reports" / "rt-00-critic-review.md"
            report_path.write_text(actor_report_text(), encoding="utf-8")
            critic_path.write_text(critic_report_text(report_path), encoding="utf-8")
            oracle = json.loads((folder / "feature-oracle.json").read_text(encoding="utf-8"))
            oracle["features"][0]["status"] = "passing"
            oracle["features"][0]["evidence"] = [str(report_path), str(critic_path)]
            (folder / "feature-oracle.json").write_text(json.dumps(oracle, indent=2), encoding="utf-8")
            state = json.loads((folder / "loop-state.json").read_text(encoding="utf-8"))
            state["status"] = "verified"
            (folder / "loop-state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")

            result = run_cmd(str(VALIDATOR), str(folder), "--strict", "--completion-gate")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("terminal actor report with non-placeholder whole-demand regression evidence", result.stdout)
            self.assertIn("terminal independent critic approval of whole-demand regression evidence", result.stdout)

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

    def test_strict_validation_rejects_phase_without_execution_load_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(folder, include_runtime_files=True)
            phase_path = folder / "phase-00-baseline-audit.md"

            def remove_load_files(contract: dict[str, object]) -> None:
                read_first = contract["context"]["read_first"]  # type: ignore[index]
                contract["context"]["read_first"] = [  # type: ignore[index]
                    item
                    for item in read_first
                    if not str(item).endswith(("context-profile.json", "loop-state.json"))
                ]

            update_phase_contract(phase_path, remove_load_files)

            result = run_cmd(str(VALIDATOR), str(folder), "--strict")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("phase-00-baseline-audit.md context.read_first missing hot-path file context-profile.json", result.stdout)
            self.assertIn("phase-00-baseline-audit.md context.read_first missing hot-path file loop-state.json", result.stdout)

    def test_strict_validation_rejects_eager_deferred_context_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(folder, include_runtime_files=True)
            phase_path = folder / "phase-00-baseline-audit.md"

            def add_deferred_loads(contract: dict[str, object]) -> None:
                contract["context"]["read_first"] = [  # type: ignore[index]
                    f"{folder}/context-profile.json",
                    f"{folder}/loop-state.json",
                    f"{folder}/phase-00-baseline-audit.md",
                    f"{folder}/source-packet.md",
                    f"{folder}/feature-oracle.json",
                ]

            update_phase_contract(phase_path, add_deferred_loads)

            result = run_cmd(str(VALIDATOR), str(folder), "--strict")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("context.read_first exceeds progressive disclosure budget", result.stdout)
            self.assertIn("context.read_first eagerly loads deferred file source-packet.md", result.stdout)
            self.assertIn("context.read_first eagerly loads deferred file feature-oracle.json", result.stdout)

    def test_strict_validation_rejects_missing_context_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(folder, include_runtime_files=True)
            (folder / "context-profile.json").unlink()

            result = run_cmd(str(VALIDATOR), str(folder), "--strict")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing runtime file: context-profile.json", result.stdout)

    def test_strict_validation_rejects_context_profile_budget_overrun(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(folder, include_runtime_files=True)
            profile_path = folder / "context-profile.json"
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
            profile["cold_start"]["required_files"].extend(
                [str(folder / "README.md"), str(folder / "source-packet.md")]
            )
            profile_path.write_text(json.dumps(profile, indent=2), encoding="utf-8")

            result = run_cmd(str(VALIDATOR), str(folder), "--strict")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("context-profile.json cold_start.required_files exceeds cap", result.stdout)
            self.assertIn("cold_start.required_files must not eagerly load deferred file README.md", result.stdout)
            self.assertIn("cold_start.required_files must not eagerly load deferred file source-packet.md", result.stdout)

    def test_strict_validation_rejects_invalid_context_profile_caps_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(folder, include_runtime_files=True)
            profile_path = folder / "context-profile.json"
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
            profile["caps"]["cold_start_max_files"] = "many"
            profile["caps"]["read_first_max_files"] = 99
            profile_path.write_text(json.dumps(profile, indent=2), encoding="utf-8")

            result = run_cmd(str(VALIDATOR), str(folder), "--strict")

            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("Traceback", result.stdout + result.stderr)
            self.assertIn("context-profile.json caps.cold_start_max_files must be a positive integer", result.stdout)
            self.assertIn("context-profile.json caps.read_first_max_files must be <= hard cap 4", result.stdout)

    def test_strict_validation_rejects_actor_profile_eager_source_packet_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(folder, include_runtime_files=True)
            profile_path = folder / "context-profile.json"
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
            profile["roles"]["actor"]["required_files"].append(str(folder / "source-packet.md"))
            profile_path.write_text(json.dumps(profile, indent=2), encoding="utf-8")

            result = run_cmd(str(VALIDATOR), str(folder), "--strict")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("context-profile.json roles.actor.required_files exceeds cap", result.stdout)
            self.assertIn("context-profile.json actor role must not eagerly load source-packet.md", result.stdout)

    def test_strict_validation_rejects_phase_without_evidence_writeback_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(folder, include_runtime_files=True)
            phase_path = folder / "phase-00-baseline-audit.md"

            def remove_writeback_artifacts(contract: dict[str, object]) -> None:
                required = contract["evidence"]["required_artifacts"]  # type: ignore[index]
                contract["evidence"]["required_artifacts"] = [  # type: ignore[index]
                    item
                    for item in required
                    if item not in {"feature-oracle evidence", "source-packet code summary", "handoff update"}
                ]

            update_phase_contract(phase_path, remove_writeback_artifacts)

            result = run_cmd(str(VALIDATOR), str(folder), "--strict")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("phase-00-baseline-audit.md evidence.required_artifacts missing execution evidence: feature oracle", result.stdout)
            self.assertIn("phase-00-baseline-audit.md evidence.required_artifacts missing execution evidence: source packet", result.stdout)
            self.assertIn("phase-00-baseline-audit.md evidence.required_artifacts missing execution evidence: handoff", result.stdout)

    def test_strict_validation_rejects_draft_phase_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(folder, include_runtime_files=True)
            phase_path = folder / "phase-00-baseline-audit.md"
            phase_path.write_text(
                phase_path.read_text(encoding="utf-8").replace('"status": "ready"', '"status": "draft"'),
                encoding="utf-8",
            )

            result = run_cmd(str(VALIDATOR), str(folder), "--strict")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("phase-00-baseline-audit.md strict validation requires phase.status other than draft", result.stdout)

    def test_strict_validation_rejects_scaffold_discovery_as_only_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(folder, include_runtime_files=True)
            phase_path = folder / "phase-00-baseline-audit.md"
            phase_text = phase_path.read_text(encoding="utf-8")
            phase_text = phase_text.replace('"id": "unit"', '"id": "repo-validation-discovery"')
            phase_path.write_text(phase_text, encoding="utf-8")

            result = run_cmd(str(VALIDATOR), str(folder), "--strict")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("phase-00-baseline-audit.md strict validation requires concrete validation commands beyond scaffold discovery", result.stdout)

    def test_strict_validation_rejects_missing_review_and_minimal_change_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(folder, include_runtime_files=True)
            phase_path = folder / "phase-00-baseline-audit.md"
            phase_text = phase_path.read_text(encoding="utf-8")
            phase_text = phase_text.replace("independent critic evidence confirms requirement coverage", "phase evidence confirms requirement coverage")
            phase_text = phase_text.replace('"independent critic evidence",', '"phase evidence",')
            phase_text = phase_text.replace("minimal-change scope note is recorded", "scope note is recorded")
            phase_text = phase_text.replace('"minimal-change scope note",', '"scope note",')
            phase_text = phase_text.replace("minimal-change", "scope")
            phase_path.write_text(phase_text, encoding="utf-8")

            result = run_cmd(str(VALIDATOR), str(folder), "--strict")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("phase-00-baseline-audit.md missing independent critic evidence gate", result.stdout)
            self.assertIn("phase-00-baseline-audit.md missing minimal-change scope gate", result.stdout)

    def test_strict_validation_rejects_terminal_phase_without_whole_demand_regression(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "runtime_harness"
            write_minimal_harness(folder, include_runtime_files=True)
            phase_path = folder / "phase-00-baseline-audit.md"
            phase_text = phase_path.read_text(encoding="utf-8")
            phase_path.write_text(
                phase_text.replace("whole-demand regression", "full coverage"),
                encoding="utf-8",
            )

            result = run_cmd(str(VALIDATOR), str(folder), "--strict")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("phase-00-baseline-audit.md terminal phase missing whole-demand regression gate", result.stdout)

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
