#!/usr/bin/env python3
"""Validate a harness-style PRD phase folder."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_CONTRACT_KEYS = [
    "PHASE_ID",
    "GOAL_TARGET",
    "GOAL_PROMPT",
    "DEPENDS_ON",
    "READ_FIRST",
    "PRIMARY_CONTEXT",
    "LIKELY_EDIT_PATHS",
    "DO_NOT_EDIT",
    "EXECUTION_MODE",
    "VALIDATION_COMMANDS",
    "BROWSER_CHECKS",
    "REGRESSION_SCOPE",
    "COMPLIANCE_GATES",
    "ROLLBACK_PLAN",
    "ACCEPTANCE_GATES",
    "EVIDENCE_OUTPUT",
    "STOP_CONDITIONS",
]

REQUIRED_PHASE_SECTIONS = [
    "## Machine Contract",
    "## Coding Agent Contract",
    "## Task Spec",
    "## Problem Boundary",
    "## Context Policy",
    "## Requirements",
    "## Test and Regression Requirements",
    "## Compliance and Safety Requirements",
    "## Rollback and Recovery",
    "## Execution Capture",
    "## Evaluator Protocol",
    "## Acceptance Criteria",
    "## Risks",
]

REQUIRED_README_SECTIONS = [
    "## Harness Intent",
    "## Coding Agent Loading Protocol",
    "## Long-Running Runtime Protocol",
    "## Source Packet",
    "## Runtime Artifacts",
    "## Current System Shape",
    "## Assumptions and Decisions",
    "## Phase Order",
    "## New Window Prompt",
    "## Roadmap Cohesion",
    "## Shared Harness Rules",
    "## Global Non-Goals",
    "## Global Compliance Gates",
    "## Standard Verification Commands",
    "## Required Browser or Runtime Checks",
    "## External Inputs and Approvals",
]

REQUIRED_MANIFEST_SECTIONS = [
    "## Grep Usage",
    "## Phase Index",
    "## Phase Report Index",
    "## Dependency Flow",
    "## Validation Matrix",
    "## Risk Matrix",
    "## Goal Setup Templates",
    "## Runtime Artifacts",
    "## Agent Role Handoffs",
    "## Shared Agent Rules",
    "## External Inputs Checklist",
]

REQUIRED_JSON_PATHS = [
    ("schema_version",),
    ("harness_role",),
    ("phase", "id"),
    ("phase", "number"),
    ("phase", "title"),
    ("phase", "status"),
    ("phase", "phase_file"),
    ("phase", "depends_on"),
    ("phase", "unlocks"),
    ("goal", "target"),
    ("goal", "prompt"),
    ("goal", "plan_required"),
    ("goal", "plan_output"),
    ("goal", "completion_report"),
    ("runtime", "feature_oracle"),
    ("runtime", "loop_contract"),
    ("runtime", "loop_state"),
    ("runtime", "progress_log"),
    ("runtime", "handoff"),
    ("runtime", "continuity_ledger"),
    ("runtime", "next_window_prompt"),
    ("runtime", "session_boot"),
    ("runtime", "agent_roles"),
    ("context", "read_first"),
    ("context", "primary_context"),
    ("context", "context_budget"),
    ("boundaries", "likely_edit_paths"),
    ("boundaries", "do_not_edit"),
    ("tool_policy", "allowed_tools"),
    ("tool_policy", "approval_required"),
    ("risk", "tags"),
    ("validation", "commands"),
    ("validation", "browser_checks"),
    ("validation", "regression_scope"),
    ("validation", "compliance_gates"),
    ("validation", "acceptance_gates"),
    ("validation", "rollback_plan"),
    ("evidence", "outputs"),
    ("evidence", "required_artifacts"),
    ("stop_conditions",),
]

RUNTIME_FILES = [
    "source-packet.md",
    "loop-contract.json",
    "loop-state.json",
    "feature-oracle.json",
    "progress-log.md",
    "agent-handoff.md",
    "continuity-ledger.md",
    "next-window-prompt.md",
]

ORACLE_STATUS_VALUES = {"failing", "passing", "blocked", "waived"}
LOOP_STATUS_VALUES = {"planned", "running", "needs_evaluation", "verified", "blocked", "failed", "waived"}
LOOP_CYCLE_STEPS = ["observe", "select", "execute", "verify", "record", "decide"]
COMPLETION_FEATURE_STATUSES = {"passing", "waived"}
COMPLETION_LOOP_STATUSES = {"verified", "waived"}
PASSING_REPORT_STATUSES = {"pass", "passed", "passing", "complete", "completed", "verified", "waived"}
INCOMPLETE_REPORT_STATUSES = {"blocked", "partial", "failed", "failing", "not-ready", "not ready", "incomplete"}
PASSING_CRITIC_VERDICTS = {"approved", "waived"}
INCOMPLETE_CRITIC_VERDICTS = {"changes_requested", "blocked", "failed", "partial", "rejected"}
ACTOR_REPORT_REQUIRED_MARKERS = [
    "Validation Evidence",
    "Feature Oracle Updates",
    "Minimal Change",
]

NEXT_WINDOW_PROMPT_REQUIREMENTS = {
    "skill": ["prd-phase-harness"],
    "target phase": ["target phase"],
    "target phase file": ["target phase file"],
    "loading order": ["loading order", "cold-start protocol"],
    "one phase and feature": ["one phase", "feature-oracle"],
    "loop cycle": ["loop cycle", "observe, select, execute, verify, record, decide"],
    "edit boundaries": ["edit boundaries", "edit boundary", "stay inside", "read-only", "read only", "likely_edit_paths"],
    "validation": ["validation"],
    "evidence": ["evidence"],
    "continuity ledger": ["continuity-ledger", "continuity ledger"],
    "code summary writeback": ["source packet", "code facts", "code-summary", "summarize code"],
    "stop conditions": ["stop conditions", "stop if", "stop and document"],
}

VAGUE_PATTERNS = [
    r"\bas needed\b",
    r"\betc\.?\b",
    r"\brelevant files\b",
    r"\brelated files\b",
    r"\brun tests\b",
    r"\bverify manually\b",
    r"\bmake sure it works\b",
    r"\bimprove ux\b",
    r"\bmake it robust\b",
    r"\bclean up\b",
]

RISK_GATE_RULES = {
    "ui": ("validation", "browser_checks"),
    "frontend": ("validation", "browser_checks"),
    "browser": ("validation", "browser_checks"),
    "figma": ("validation", "browser_checks"),
    "ai": ("validation", "acceptance_gates"),
    "agent": ("validation", "acceptance_gates"),
    "llm": ("validation", "acceptance_gates"),
    "eval": ("validation", "acceptance_gates"),
    "migration": ("validation", "rollback_plan"),
    "schema": ("validation", "rollback_plan"),
    "database": ("validation", "rollback_plan"),
    "auth": ("validation", "compliance_gates"),
    "payment": ("validation", "compliance_gates"),
    "security": ("validation", "compliance_gates"),
}

EXECUTION_READINESS_FILES = [
    "README.md",
    "phase-manifest.md",
    "source-packet.md",
    "loop-contract.json",
    "loop-state.json",
    "feature-oracle.json",
    "progress-log.md",
    "agent-handoff.md",
    "continuity-ledger.md",
    "next-window-prompt.md",
]

EXECUTION_EVIDENCE_TERMS = [
    ("phase report", ["phase report"]),
    ("progress log", ["progress log", "progress-log"]),
    ("feature oracle", ["feature oracle", "feature-oracle", "oracle evidence"]),
    ("continuity ledger", ["continuity ledger", "continuity-ledger"]),
    ("source packet", ["source packet", "source-packet"]),
    ("handoff", ["handoff"]),
]


def find_heading(text: str, heading: str) -> bool:
    return re.search(rf"^{re.escape(heading)}\s*$", text, re.MULTILINE) is not None


def extract_contract_value(text: str, key: str) -> str | None:
    match = re.search(rf"^\s*-\s*{re.escape(key)}:\s*(.+?)\s*$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def extract_json_contract(text: str) -> dict[str, Any] | None:
    match = re.search(r"## Machine Contract.*?```json\s*(.*?)\s*```", text, re.DOTALL)
    if not match:
        return None
    return json.loads(match.group(1))


def get_path(data: dict[str, Any], path: tuple[str, ...]) -> Any:
    current: Any = data
    for part in path:
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        if value.lower() == "none":
            return []
        return [item.strip() for item in re.split(r"[,;]", value) if item.strip()]
    return [value]


def textify(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True)


def has_placeholder(text: str) -> bool:
    return bool(re.search(r"\b(TODO|TBD)\b|{{[^}]+}}", text))


def is_concrete_list(value: Any, *, allow_placeholders: bool) -> bool:
    items = as_list(value)
    if not items:
        return False
    if allow_placeholders:
        return True
    rendered = " ".join(textify(item) for item in items).lower()
    if has_placeholder(rendered):
        return False
    return rendered not in {"none", "n/a", "unknown"}


def is_non_empty_text(value: Any, *, allow_placeholders: bool) -> bool:
    if not isinstance(value, str):
        return False
    if not value.strip():
        return False
    if not allow_placeholders and has_placeholder(value):
        return False
    return True


def phase_files(folder: Path) -> list[Path]:
    files: list[Path] = []
    for path in folder.glob("phase-*.md"):
        if re.match(r"phase-\d{2}-[a-z0-9][a-z0-9-]*\.md$", path.name):
            files.append(path)
    return sorted(files)


def contains_vague_language(value: Any) -> list[str]:
    rendered = textify(value).lower()
    return [pattern for pattern in VAGUE_PATTERNS if re.search(pattern, rendered)]


def text_contains_any(text: str, alternatives: list[str]) -> bool:
    lower = text.lower()
    return any(alternative in lower for alternative in alternatives)


def missing_next_window_prompt_content(text: str) -> list[str]:
    lower = text.lower()
    missing: list[str] = []
    for label, alternatives in NEXT_WINDOW_PROMPT_REQUIREMENTS.items():
        if label == "one phase and feature":
            if "one phase" not in lower or "feature-oracle" not in lower:
                missing.append(label)
            continue
        if not any(needle in lower for needle in alternatives):
            missing.append(label)
    return missing


def validate_json_contract(
    *,
    path: Path,
    text: str,
    data: dict[str, Any] | None,
    markdown_values: dict[str, str],
    allow_placeholders: bool,
    strict: bool,
) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    if data is None:
        errors.append(f"{path.name} missing parseable Machine Contract JSON block")
        return errors, warnings, {}

    for json_path in REQUIRED_JSON_PATHS:
        value = get_path(data, json_path)
        if value is None:
            errors.append(f"{path.name} machine contract missing: {'.'.join(json_path)}")
        elif isinstance(value, (str, list, dict)) and not allow_placeholders and has_placeholder(textify(value)):
            errors.append(f"{path.name} machine contract placeholder: {'.'.join(json_path)}")

    phase = data.get("phase", {}) if isinstance(data.get("phase"), dict) else {}
    goal = data.get("goal", {}) if isinstance(data.get("goal"), dict) else {}
    validation = data.get("validation", {}) if isinstance(data.get("validation"), dict) else {}
    risk = data.get("risk", {}) if isinstance(data.get("risk"), dict) else {}
    runtime = data.get("runtime", {}) if isinstance(data.get("runtime"), dict) else {}

    json_phase_id = phase.get("id")
    md_phase_id = markdown_values.get("PHASE_ID")
    if json_phase_id and md_phase_id and json_phase_id != md_phase_id:
        errors.append(f"{path.name} PHASE_ID mismatch: JSON {json_phase_id} vs Markdown {md_phase_id}")

    phase_file = phase.get("phase_file", "")
    if path.name not in str(phase_file):
        warnings.append(f"{path.name} machine contract phase.phase_file does not include file name")

    prompt = goal.get("prompt", "")
    if json_phase_id and json_phase_id not in str(prompt):
        errors.append(f"{path.name} goal.prompt does not include phase id {json_phase_id}")
    if path.name not in str(prompt):
        warnings.append(f"{path.name} goal.prompt does not include phase file name")

    commands = validation.get("commands", [])
    if not isinstance(commands, list) or not commands:
        errors.append(f"{path.name} validation.commands must be a non-empty array")
    else:
        for index, command in enumerate(commands):
            if not isinstance(command, dict):
                errors.append(f"{path.name} validation.commands[{index}] must be an object")
                continue
            for key in ["id", "cwd", "command", "expected", "required"]:
                if key not in command:
                    errors.append(f"{path.name} validation.commands[{index}] missing {key}")

    outputs = as_list(get_path(data, ("evidence", "outputs")))
    if not outputs:
        errors.append(f"{path.name} evidence.outputs must name durable artifacts")
    elif not any("reports/" in str(output) or "screenshot" in str(output).lower() for output in outputs):
        warnings.append(f"{path.name} evidence.outputs does not appear to include reports/ or screenshots")

    if strict and not allow_placeholders:
        status = str(phase.get("status", "")).lower()
        if status == "draft":
            errors.append(f"{path.name} strict validation requires phase.status other than draft")

        if goal.get("plan_required") is not True:
            errors.append(f"{path.name} strict validation requires goal.plan_required true")
        plan_output = str(goal.get("plan_output", ""))
        if "reports/" not in plan_output:
            errors.append(f"{path.name} goal.plan_output must point to a reports/ artifact")
        completion_report = str(goal.get("completion_report", ""))
        if "reports/" not in completion_report:
            errors.append(f"{path.name} goal.completion_report must point to a reports/ artifact")
        if completion_report and not any(completion_report == str(output) for output in outputs):
            errors.append(f"{path.name} evidence.outputs must include goal.completion_report")

        read_first_text = textify(get_path(data, ("context", "read_first"))).lower()
        phase_file_name = Path(str(phase.get("phase_file", path.name))).name
        for required_file in [*EXECUTION_READINESS_FILES, phase_file_name]:
            if required_file.lower() not in read_first_text:
                errors.append(f"{path.name} context.read_first missing execution file {required_file}")
        if not is_concrete_list(get_path(data, ("context", "primary_context")), allow_placeholders=False):
            errors.append(f"{path.name} context.primary_context must be a non-empty concrete list")
        if not is_concrete_list(get_path(data, ("boundaries", "likely_edit_paths")), allow_placeholders=False):
            errors.append(f"{path.name} boundaries.likely_edit_paths must be a non-empty concrete list")
        if not is_concrete_list(get_path(data, ("boundaries", "do_not_edit")), allow_placeholders=False):
            errors.append(f"{path.name} boundaries.do_not_edit must be a non-empty concrete list")

        if commands and not any(isinstance(command, dict) and command.get("required") is True for command in commands):
            errors.append(f"{path.name} validation.commands must include at least one required command")
        for index, command in enumerate(commands if isinstance(commands, list) else []):
            if not isinstance(command, dict):
                continue
            for key in ["cwd", "command", "expected"]:
                if not is_non_empty_text(str(command.get(key, "")), allow_placeholders=False):
                    errors.append(f"{path.name} validation.commands[{index}].{key} must be concrete")

        required_artifact_text = textify(get_path(data, ("evidence", "required_artifacts"))).lower()
        for label, alternatives in EXECUTION_EVIDENCE_TERMS:
            if not text_contains_any(required_artifact_text, alternatives):
                errors.append(f"{path.name} evidence.required_artifacts missing execution evidence: {label}")
        if not is_non_empty_text(str(get_path(data, ("evidence", "next_phase_handoff"))), allow_placeholders=False):
            errors.append(f"{path.name} evidence.next_phase_handoff must be concrete")

        for runtime_key in ["feature_oracle", "loop_contract", "loop_state", "progress_log", "handoff", "continuity_ledger", "next_window_prompt"]:
            runtime_path = runtime.get(runtime_key)
            if not is_non_empty_text(runtime_path, allow_placeholders=False):
                errors.append(f"{path.name} runtime.{runtime_key} must name a concrete artifact path")

        agent_roles = [str(role).lower() for role in as_list(runtime.get("agent_roles"))]
        for required_role in ["planner", "generator", "critic"]:
            if required_role not in agent_roles:
                errors.append(f"{path.name} runtime.agent_roles missing {required_role}")

        session_boot = runtime.get("session_boot", {})
        if not isinstance(session_boot, dict):
            errors.append(f"{path.name} runtime.session_boot must be an object")
        else:
            for key in ["read_progress", "run_baseline_check", "update_progress_before_exit"]:
                if session_boot.get(key) is not True:
                    errors.append(f"{path.name} runtime.session_boot.{key} must be true")

        for json_path in REQUIRED_JSON_PATHS:
            value = get_path(data, json_path)
            vague = contains_vague_language(value)
            if vague:
                errors.append(f"{path.name} vague language in {'.'.join(json_path)}: {', '.join(vague)}")

        risk_tags = [str(tag).lower() for tag in as_list(risk.get("tags"))]
        for tag in risk_tags:
            required_path = RISK_GATE_RULES.get(tag)
            if required_path and not is_concrete_list(get_path(data, required_path), allow_placeholders=False):
                errors.append(
                    f"{path.name} risk tag '{tag}' requires concrete {'.'.join(required_path)}"
                )

        if commands and all(
            isinstance(command, dict) and command.get("id") == "repo-validation-discovery"
            for command in commands
        ):
            errors.append(f"{path.name} strict validation requires concrete validation commands beyond scaffold discovery")

        quality_gate_text = " ".join(
            textify(value).lower()
            for value in [
                validation.get("regression_scope"),
                validation.get("acceptance_gates"),
                get_path(data, ("evidence", "required_artifacts")),
            ]
        )
        if "critic" not in quality_gate_text:
            errors.append(f"{path.name} missing independent critic evidence gate")
        if "minimal-change" not in quality_gate_text and "minimal change" not in quality_gate_text:
            errors.append(f"{path.name} missing minimal-change scope gate")
        if not as_list(phase.get("unlocks")) and "whole-demand regression" not in quality_gate_text:
            errors.append(f"{path.name} terminal phase missing whole-demand regression gate")

    return errors, warnings, data


def validate_runtime_artifacts(
    folder: Path,
    *,
    allow_placeholders: bool,
    strict: bool,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for file_name in RUNTIME_FILES:
        path = folder / file_name
        if not path.exists():
            errors.append(f"Missing runtime file: {file_name}")
            continue
        if not allow_placeholders:
            text = path.read_text(encoding="utf-8")
            if has_placeholder(text):
                errors.append(f"{file_name} contains TODO/TBD/template placeholders")
            if strict and file_name == "next-window-prompt.md":
                missing = missing_next_window_prompt_content(text)
                if missing:
                    errors.append(
                        "next-window-prompt.md missing required prompt content: "
                        + ", ".join(missing)
                    )

    oracle_path = folder / "feature-oracle.json"
    if not oracle_path.exists():
        return errors, warnings

    try:
        oracle = json.loads(oracle_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"feature-oracle.json parse error: {exc}")
        return errors, warnings

    features = oracle.get("features") if isinstance(oracle, dict) else None
    if not isinstance(features, list) or not features:
        errors.append("feature-oracle.json must contain a non-empty features array")
        return errors, warnings

    seen_ids: set[str] = set()
    for index, feature in enumerate(features):
        if not isinstance(feature, dict):
            errors.append(f"feature-oracle.json features[{index}] must be an object")
            continue
        feature_id = str(feature.get("id") or f"features[{index}]")
        if feature_id in seen_ids:
            errors.append(f"feature-oracle.json duplicate feature id: {feature_id}")
        seen_ids.add(feature_id)

        for key in ["id", "phase_id", "category", "description", "steps", "status", "evidence"]:
            if key not in feature:
                errors.append(f"feature-oracle.json feature {feature_id} missing {key}")

        status = str(feature.get("status", "")).lower()
        if status not in ORACLE_STATUS_VALUES:
            errors.append(
                f"feature-oracle.json feature {feature_id} has invalid status {status!r}"
            )

        steps = feature.get("steps")
        if not isinstance(steps, list) or not steps:
            errors.append(f"feature-oracle.json feature {feature_id} must include non-empty steps")

        if strict and not allow_placeholders:
            for key in ["id", "category", "description", "status"]:
                if not is_non_empty_text(str(feature.get(key, "")), allow_placeholders=False):
                    errors.append(f"feature-oracle.json feature {feature_id} has empty {key}")
            if has_placeholder(textify(feature)):
                errors.append(f"feature-oracle.json feature {feature_id} contains placeholder text")
            if status in {"passing", "waived"} and not is_non_empty_text(
                str(feature.get("evidence", "")),
                allow_placeholders=False,
            ):
                errors.append(
                    f"feature-oracle.json feature {feature_id} is {status} without evidence"
                )
            if status == "blocked" and not is_non_empty_text(
                str(feature.get("notes", "")),
                allow_placeholders=False,
            ):
                warnings.append(
                    f"feature-oracle.json feature {feature_id} is blocked without notes"
                )

    return errors, warnings


def read_json_file(path: Path, label: str) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, [f"Missing runtime file: {label}"]
    except json.JSONDecodeError as exc:
        return None, [f"{label} parse error: {exc}"]
    if not isinstance(data, dict):
        return None, [f"{label} must contain a JSON object"]
    return data, []


def normalize_report_status(value: str) -> str:
    status = re.sub(r"[`*_]", "", value.strip().lower())
    status = re.sub(r"\s+", " ", status)
    if status.startswith("pass"):
        return "passed"
    if status.startswith("complete"):
        return "completed"
    if status.startswith("verify"):
        return "verified"
    if status.startswith("waive"):
        return "waived"
    if status.startswith("block"):
        return "blocked"
    if status.startswith("partial"):
        return "partial"
    if status.startswith("fail"):
        return "failed"
    if status.startswith("incomplete"):
        return "incomplete"
    return status


def normalize_critic_verdict(value: str) -> str:
    verdict = re.sub(r"[`*_]", "", value.strip().lower())
    verdict = re.sub(r"[\s-]+", "_", verdict)
    if verdict.startswith("approve") or verdict.startswith("pass"):
        return "approved"
    if verdict.startswith("waive"):
        return "waived"
    if verdict.startswith("change") or verdict.startswith("request"):
        return "changes_requested"
    if verdict.startswith("block"):
        return "blocked"
    if verdict.startswith("reject"):
        return "rejected"
    if verdict.startswith("fail"):
        return "failed"
    if verdict.startswith("partial"):
        return "partial"
    return verdict


def extract_report_status(text: str) -> str | None:
    for line in text.splitlines():
        clean = re.sub(r"[`*]", "", line).strip()
        match = re.match(r"(?i)^(?:[-]\s*)?status\s*:\s*(.+?)\s*$", clean)
        if match:
            return normalize_report_status(match.group(1))
    return None


def extract_critic_verdict(text: str) -> str | None:
    for line in text.splitlines():
        clean = re.sub(r"[`*]", "", line).strip()
        match = re.match(r"(?i)^(?:[-]\s*)?(?:critic|evaluator|reviewer)\s+verdict\s*:\s*(.+?)\s*$", clean)
        if match:
            return normalize_critic_verdict(match.group(1))
    return None


def extract_report_field(text: str, field: str) -> str | None:
    pattern = re.compile(rf"(?i)^(?:[-]\s*)?{re.escape(field)}\s*:\s*(.+?)\s*$")
    for line in text.splitlines():
        clean = re.sub(r"[`*]", "", line).strip()
        match = pattern.match(clean)
        if match:
            return match.group(1).strip()
    return None


def has_independent_critic_marker(text: str) -> bool:
    for line in text.splitlines():
        clean = re.sub(r"[`*]", "", line).strip().lower()
        if not re.match(r"^(?:[-]\s*)?(?:critic|evaluator|reviewer)\s*:", clean):
            continue
        if re.search(r"\b(independent|subagent|sub-agent|fresh context|separate agent|critic agent)\b", clean):
            return True
    return False


def has_actor_report_substance(text: str) -> bool:
    if has_placeholder(text):
        return False
    if len(textify(text).strip()) < 400:
        return False
    return all(marker.lower() in text.lower() for marker in ACTOR_REPORT_REQUIRED_MARKERS)


def has_whole_demand_regression_evidence(text: str) -> bool:
    if has_placeholder(text):
        return False
    lower = text.lower()
    if "whole-demand regression" not in lower:
        return False
    incomplete_markers = [
        "whole-demand regression: todo",
        "whole-demand regression: blocked",
        "whole-demand regression: partial",
        "whole-demand regression is blocked",
        "whole-demand regression blocked",
    ]
    return not any(marker in lower for marker in incomplete_markers)


def normalize_path_for_match(path: Path) -> str:
    return str(path).replace("\\", "/")


def critic_references_actor_report(
    critic_text: str,
    actor_report_path: Path,
    raw_actor_path: str,
) -> bool:
    reviewed = extract_report_field(critic_text, "Actor Report Reviewed")
    if not reviewed:
        reviewed = extract_report_field(critic_text, "Actor Report")
    if not reviewed:
        return False
    reviewed_clean = reviewed.strip().strip("`'\".,:;")
    actor_abs = normalize_path_for_match(actor_report_path)
    actor_name = normalize_path_for_match(Path(raw_actor_path))
    reviewed_norm = normalize_path_for_match(Path(reviewed_clean))
    return (
        reviewed_clean == raw_actor_path.strip().strip("`'\".,:;")
        or reviewed_norm == actor_abs
        or reviewed_norm == actor_name
        or actor_abs.endswith("/" + reviewed_clean.replace("\\", "/"))
        or actor_abs in critic_text
        or raw_actor_path in critic_text
    )


def evidence_path_strings(value: Any) -> list[str]:
    paths: list[str] = []
    if isinstance(value, str):
        paths.extend(re.findall(r"[\w./@+-]+\.md", value))
        return paths
    if isinstance(value, dict):
        path = value.get("path")
        if isinstance(path, str):
            paths.append(path)
        for key in ["evidence", "summary", "notes"]:
            paths.extend(evidence_path_strings(value.get(key)))
        return paths
    if isinstance(value, list):
        for item in value:
            paths.extend(evidence_path_strings(item))
    return paths


def resolve_evidence_path(folder: Path, raw_path: str) -> Path | None:
    cleaned = raw_path.strip().strip("`'\".,:;")
    path = Path(cleaned)
    if path.is_absolute():
        return path if path.exists() else None
    for base in [folder, *folder.parents]:
        candidate = base / cleaned
        if candidate.exists():
            return candidate
    return None


def validate_completion_gate(
    folder: Path,
    *,
    phase_id: str | None,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    oracle, oracle_errors = read_json_file(folder / "feature-oracle.json", "feature-oracle.json")
    errors.extend(oracle_errors)
    if not oracle:
        return errors, warnings

    features = oracle.get("features")
    if not isinstance(features, list) or not features:
        errors.append("completion gate requires feature-oracle.json features")
        return errors, warnings

    selected = [
        feature
        for feature in features
        if isinstance(feature, dict) and (phase_id is None or feature.get("phase_id") == phase_id)
    ]
    if phase_id is not None and not selected:
        errors.append(f"completion gate found no feature-oracle items for phase {phase_id}")
        return errors, warnings

    if phase_id is None:
        state, state_errors = read_json_file(folder / "loop-state.json", "loop-state.json")
        errors.extend(state_errors)
        if state:
            status = str(state.get("status", "")).lower()
            if status not in COMPLETION_LOOP_STATUSES:
                errors.append(
                    "completion gate requires loop-state.status verified or waived; "
                    f"found {status or 'missing'}"
                )

    terminal_phase_id = None
    if phase_id is None and selected:
        terminal_phase_id = str(selected[-1].get("phase_id") or "")
    terminal_actor_regression = False
    terminal_critic_regression = False

    for index, feature in enumerate(selected):
        feature_id = str(feature.get("id") or f"features[{index}]")
        feature_phase = str(feature.get("phase_id") or "unknown-phase")
        status = str(feature.get("status", "")).lower()
        if status not in COMPLETION_FEATURE_STATUSES:
            errors.append(
                f"completion gate requires feature {feature_id} ({feature_phase}) "
                f"to be passing or waived; found {status or 'missing'}"
            )

        evidence_paths = evidence_path_strings(feature.get("evidence"))
        if not evidence_paths:
            errors.append(f"completion gate requires feature {feature_id} to cite report and critic artifacts")
            continue

        actor_reports: list[tuple[str, Path, str, str]] = []
        critic_reports: list[tuple[str, Path, str, str]] = []

        for raw_evidence_path in evidence_paths:
            evidence_path = resolve_evidence_path(folder, raw_evidence_path)
            if evidence_path is None:
                errors.append(
                    f"completion gate evidence for feature {feature_id} references missing artifact {raw_evidence_path}"
                )
                continue
            try:
                evidence_text = evidence_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                warnings.append(f"completion gate could not read artifact as UTF-8: {evidence_path}")
                continue

            report_status = extract_report_status(evidence_text)
            critic_verdict = extract_critic_verdict(evidence_text)
            if report_status is not None and critic_verdict is not None:
                errors.append(
                    f"completion gate requires separate actor and critic artifacts for feature {feature_id}; "
                    f"single file contains both Status and Critic Verdict: {evidence_path}"
                )
                continue

            if report_status is not None:
                actor_reports.append((raw_evidence_path, evidence_path, evidence_text, report_status))
                if report_status in INCOMPLETE_REPORT_STATUSES:
                    errors.append(
                        f"completion gate feature {feature_id} cites incomplete report {evidence_path}: {report_status}"
                    )
                elif report_status in PASSING_REPORT_STATUSES:
                    if not has_actor_report_substance(evidence_text):
                        errors.append(
                            f"completion gate actor report for feature {feature_id} is evidence-thin "
                            f"or still contains placeholders: {evidence_path}"
                        )
                    if (
                        phase_id is None
                        and terminal_phase_id
                        and feature_phase == terminal_phase_id
                        and has_whole_demand_regression_evidence(evidence_text)
                    ):
                        terminal_actor_regression = True
                else:
                    errors.append(
                        f"completion gate report for feature {feature_id} has unrecognized status "
                        f"{report_status!r}: {evidence_path}"
                    )

            if critic_verdict is not None:
                critic_reports.append((raw_evidence_path, evidence_path, evidence_text, critic_verdict))
                if feature_id not in evidence_text or feature_phase not in evidence_text:
                    errors.append(
                        f"completion gate critic artifact for feature {feature_id} must reference "
                        f"feature {feature_id} and phase {feature_phase}: {evidence_path}"
                    )
                if not has_independent_critic_marker(evidence_text):
                    errors.append(
                        f"completion gate critic artifact for feature {feature_id} must state an "
                        f"independent critic/subagent/fresh-context reviewer: {evidence_path}"
                    )
                if critic_verdict in INCOMPLETE_CRITIC_VERDICTS:
                    errors.append(
                        f"completion gate critic rejected feature {feature_id} in {evidence_path}: {critic_verdict}"
                    )
                elif critic_verdict in PASSING_CRITIC_VERDICTS:
                    if critic_verdict == "waived" and not extract_report_field(evidence_text, "Waiver Reason"):
                        errors.append(
                            f"completion gate waived critic artifact for feature {feature_id} must include "
                            f"Waiver Reason: {evidence_path}"
                        )
                    if (
                        phase_id is None
                        and terminal_phase_id
                        and feature_phase == terminal_phase_id
                        and "whole-demand regression" in evidence_text.lower()
                    ):
                        terminal_critic_regression = True
                else:
                    errors.append(
                        f"completion gate critic artifact for feature {feature_id} has unrecognized verdict "
                        f"{critic_verdict!r}: {evidence_path}"
                    )

        passed_actor_reports = [
            actor
            for actor in actor_reports
            if actor[3] in PASSING_REPORT_STATUSES and has_actor_report_substance(actor[2])
        ]
        approved_critic_reports = [
            critic
            for critic in critic_reports
            if critic[3] in PASSING_CRITIC_VERDICTS
        ]

        if not actor_reports:
            errors.append(
                f"completion gate requires feature {feature_id} to cite an actor phase report with a Status line"
            )
        elif not passed_actor_reports:
            errors.append(
                f"completion gate requires feature {feature_id} to cite at least one passed or waived substantive actor report"
            )

        if not critic_reports:
            errors.append(
                f"completion gate requires feature {feature_id} to cite an independent critic artifact "
                "with Critic Verdict"
            )
        elif not approved_critic_reports:
            errors.append(
                f"completion gate requires feature {feature_id} to cite at least one approved or waived critic verdict"
            )

        for raw_critic_path, critic_path, critic_text, critic_verdict in approved_critic_reports:
            del raw_critic_path, critic_verdict
            if any(critic_path.resolve() == actor_path.resolve() for _, actor_path, _, _ in actor_reports):
                errors.append(
                    f"completion gate critic artifact for feature {feature_id} must be a separate file "
                    f"from the actor report: {critic_path}"
                )
            if passed_actor_reports and not any(
                critic_references_actor_report(critic_text, actor_path, raw_actor_path)
                for raw_actor_path, actor_path, _, _ in passed_actor_reports
            ):
                errors.append(
                    f"completion gate critic artifact for feature {feature_id} must reference the reviewed "
                    f"actor report path: {critic_path}"
                )

    if phase_id is None and selected:
        if not terminal_actor_regression:
            errors.append(
                "completion gate full-demand claim requires terminal actor report with non-placeholder "
                "whole-demand regression evidence"
            )
        if not terminal_critic_regression:
            errors.append(
                "completion gate full-demand claim requires terminal independent critic approval of "
                "whole-demand regression evidence"
            )

    return errors, warnings


def validate_loop_files(
    folder: Path,
    *,
    allow_placeholders: bool,
    strict: bool,
    phase_ids: set[str] | None = None,
    feature_ids: set[str] | None = None,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not strict or allow_placeholders:
        return errors, warnings

    contract, contract_errors = read_json_file(folder / "loop-contract.json", "loop-contract.json")
    errors.extend(contract_errors)
    state, state_errors = read_json_file(folder / "loop-state.json", "loop-state.json")
    errors.extend(state_errors)

    if contract:
        for key in ["schema_version", "goal", "cycle", "max_iterations", "state_file", "oracle_file", "done_when", "continue_when", "stop_when"]:
            if key not in contract:
                errors.append(f"loop-contract.json missing {key}")
        cycle = [str(step).lower() for step in as_list(contract.get("cycle"))]
        for step in LOOP_CYCLE_STEPS:
            if step not in cycle:
                errors.append(f"loop-contract.json missing cycle step: {step}")
        max_iterations = contract.get("max_iterations")
        if not isinstance(max_iterations, int) or max_iterations < 1:
            errors.append("loop-contract.json max_iterations must be a positive integer")
        for key in ["done_when", "continue_when", "stop_when"]:
            if not is_concrete_list(contract.get(key), allow_placeholders=False):
                errors.append(f"loop-contract.json {key} must be a non-empty concrete list")

    if state:
        for key in ["schema_version", "active_phase", "active_feature", "iteration", "status", "last_decision", "next_action"]:
            if key not in state:
                errors.append(f"loop-state.json missing {key}")
        status = str(state.get("status", "")).lower()
        if status not in LOOP_STATUS_VALUES:
            errors.append(f"loop-state.json has invalid status {status!r}")
        iteration = state.get("iteration")
        if not isinstance(iteration, int) or iteration < 0:
            errors.append("loop-state.json iteration must be a non-negative integer")
        active_phase = state.get("active_phase")
        if phase_ids is not None and active_phase not in phase_ids:
            errors.append(f"loop-state.json active_phase {active_phase} is not in phase files")
        active_feature = state.get("active_feature")
        if feature_ids is not None and active_feature not in feature_ids:
            errors.append(f"loop-state.json active_feature {active_feature} is not in feature-oracle.json")

    return errors, warnings


def validate_oracle_phase_alignment(
    folder: Path,
    *,
    phase_ids: set[str],
    allow_placeholders: bool,
    strict: bool,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not strict or allow_placeholders:
        return errors, warnings

    oracle_path = folder / "feature-oracle.json"
    if not oracle_path.exists():
        return errors, warnings

    try:
        oracle = json.loads(oracle_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return errors, warnings

    features = oracle.get("features") if isinstance(oracle, dict) else None
    if not isinstance(features, list):
        return errors, warnings

    covered_phase_ids: set[str] = set()
    for index, feature in enumerate(features):
        if not isinstance(feature, dict):
            continue
        feature_id = str(feature.get("id") or f"features[{index}]")
        phase_id = feature.get("phase_id")
        if not isinstance(phase_id, str) or not phase_id.strip():
            errors.append(f"feature-oracle.json feature {feature_id} missing phase_id")
            continue
        if has_placeholder(phase_id):
            errors.append(f"feature-oracle.json feature {feature_id} has placeholder phase_id")
            continue
        if phase_id not in phase_ids:
            errors.append(
                f"feature-oracle.json feature {feature_id} references unknown phase {phase_id}"
            )
            continue
        covered_phase_ids.add(phase_id)

    for phase_id in sorted(phase_ids - covered_phase_ids):
        errors.append(f"feature-oracle.json has no feature for phase {phase_id}")

    return errors, warnings


def feature_ids_from_oracle(folder: Path) -> set[str]:
    oracle_path = folder / "feature-oracle.json"
    if not oracle_path.exists():
        return set()
    try:
        oracle = json.loads(oracle_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    features = oracle.get("features") if isinstance(oracle, dict) else None
    if not isinstance(features, list):
        return set()
    ids: set[str] = set()
    for feature in features:
        if isinstance(feature, dict) and isinstance(feature.get("id"), str):
            ids.add(feature["id"])
    return ids


def score_quality(errors: list[str], warnings: list[str], phase_count: int) -> dict[str, Any]:
    raw = 100
    raw -= min(70, len(errors) * 10)
    raw -= min(20, len(warnings) * 3)
    raw += min(5, phase_count)
    score = max(0, min(100, raw))
    if errors:
        score = min(score, 49)
    if score >= 90:
        band = "excellent"
    elif score >= 75:
        band = "usable"
    elif score >= 50:
        band = "needs-work"
    else:
        band = "not-ready"
    return {"score": score, "band": band}


def validate_folder(
    folder: Path,
    *,
    allow_placeholders: bool,
    strict: bool,
    completion_gate: bool,
    completion_phase: str | None,
) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    metadata: dict[str, Any] = {"phase_count": 0, "phase_ids": []}

    readme = folder / "README.md"
    manifest = folder / "phase-manifest.md"
    phases = phase_files(folder)

    if not readme.exists():
        errors.append("Missing README.md")
    if not manifest.exists():
        errors.append("Missing phase-manifest.md")
    if not phases:
        errors.append("Missing numbered phase files matching phase-XX-<slug>.md")
    if errors:
        return errors, warnings, metadata

    readme_text = readme.read_text(encoding="utf-8")
    manifest_text = manifest.read_text(encoding="utf-8")

    for section in REQUIRED_README_SECTIONS:
        if not find_heading(readme_text, section):
            errors.append(f"README.md missing section: {section}")

    for section in REQUIRED_MANIFEST_SECTIONS:
        if not find_heading(manifest_text, section):
            errors.append(f"phase-manifest.md missing section: {section}")

    if not allow_placeholders:
        for doc_path, text in [(readme, readme_text), (manifest, manifest_text)]:
            if has_placeholder(text):
                errors.append(f"{doc_path.name} contains TODO/TBD/template placeholders")

    runtime_errors, runtime_warnings = validate_runtime_artifacts(
        folder,
        allow_placeholders=allow_placeholders,
        strict=strict,
    )
    errors.extend(runtime_errors)
    warnings.extend(runtime_warnings)

    phase_ids: dict[str, Path] = {}
    deps: dict[str, list[str]] = {}
    ordered_ids: list[str] = []

    for path in phases:
        text = path.read_text(encoding="utf-8")
        if not re.search(r"^# Phase \d{2} - .+", text, re.MULTILINE):
            errors.append(f"{path.name} missing '# Phase XX - Name' title")

        for section in REQUIRED_PHASE_SECTIONS:
            if not find_heading(text, section):
                errors.append(f"{path.name} missing section: {section}")

        markdown_values: dict[str, str] = {}
        for key in REQUIRED_CONTRACT_KEYS:
            value = extract_contract_value(text, key)
            if value is None:
                errors.append(f"{path.name} missing contract key: {key}")
                continue
            if value.lower() in {"", "todo", "tbd"}:
                errors.append(f"{path.name} has empty/placeholder contract key: {key}")
            markdown_values[key] = value

        try:
            json_contract = extract_json_contract(text)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name} Machine Contract JSON parse error: {exc}")
            json_contract = None

        json_errors, json_warnings, parsed = validate_json_contract(
            path=path,
            text=text,
            data=json_contract,
            markdown_values=markdown_values,
            allow_placeholders=allow_placeholders,
            strict=strict,
        )
        errors.extend(json_errors)
        warnings.extend(json_warnings)

        phase_id = markdown_values.get("PHASE_ID") or get_path(parsed, ("phase", "id"))
        if phase_id:
            phase_id = str(phase_id)
            ordered_ids.append(phase_id)
            if phase_id in phase_ids:
                errors.append(f"Duplicate PHASE_ID: {phase_id}")
            phase_ids[phase_id] = path
            if phase_id not in manifest_text:
                errors.append(f"Manifest does not mention PHASE_ID {phase_id}")
            if path.name not in manifest_text:
                errors.append(f"Manifest does not mention file {path.name}")

        json_deps = get_path(parsed, ("phase", "depends_on"))
        dep_ids = [str(item) for item in as_list(json_deps)]
        if not dep_ids:
            dep_ids = [
                item.strip()
                for item in re.split(r"[, ]+", markdown_values.get("DEPENDS_ON", "none"))
                if item.strip() and item.strip().lower() != "none"
            ]
        if phase_id:
            deps[str(phase_id)] = dep_ids

        if not allow_placeholders and has_placeholder(text):
            errors.append(f"{path.name} contains TODO/TBD/template placeholders")

    for phase_id, dep_ids in deps.items():
        for dep_id in dep_ids:
            if dep_id not in phase_ids:
                errors.append(f"{phase_id} depends on unknown phase {dep_id}")
            elif ordered_ids.index(dep_id) > ordered_ids.index(phase_id):
                errors.append(f"{phase_id} depends on later phase {dep_id}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, chain: list[str]) -> None:
        if node in visiting:
            errors.append("Dependency cycle: " + " -> ".join(chain + [node]))
            return
        if node in visited:
            return
        visiting.add(node)
        for dep in deps.get(node, []):
            if dep in deps:
                visit(dep, chain + [node])
        visiting.remove(node)
        visited.add(node)

    for phase_id in deps:
        visit(phase_id, [])

    oracle_errors, oracle_warnings = validate_oracle_phase_alignment(
        folder,
        phase_ids=set(phase_ids),
        allow_placeholders=allow_placeholders,
        strict=strict,
    )
    errors.extend(oracle_errors)
    warnings.extend(oracle_warnings)

    loop_errors, loop_warnings = validate_loop_files(
        folder,
        phase_ids=set(phase_ids),
        feature_ids=feature_ids_from_oracle(folder),
        allow_placeholders=allow_placeholders,
        strict=strict,
    )
    errors.extend(loop_errors)
    warnings.extend(loop_warnings)

    if completion_gate:
        completion_errors, completion_warnings = validate_completion_gate(
            folder,
            phase_id=completion_phase,
        )
        errors.extend(completion_errors)
        warnings.extend(completion_warnings)

    reports_template = folder / "reports" / "phase-report-template.md"
    if not reports_template.exists():
        warnings.append("Missing reports/phase-report-template.md")

    metadata["phase_count"] = len(phases)
    metadata["phase_ids"] = ordered_ids
    return errors, warnings, metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", help="Harness docs folder to validate")
    parser.add_argument("--allow-placeholders", action="store_true", help="Allow TODO/TBD/template placeholders")
    parser.add_argument("--strict", action="store_true", help="Enable semantic lint and risk-triggered gate checks")
    parser.add_argument(
        "--completion-gate",
        action="store_true",
        help="Fail unless selected feature-oracle items and cited reports prove completion.",
    )
    parser.add_argument(
        "--phase",
        help="Limit --completion-gate to one phase id, for example RABC-07.",
    )
    parser.add_argument("--quality-score", action="store_true", help="Emit a simple readiness score")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of human-readable output")
    args = parser.parse_args()

    folder = Path(args.folder).expanduser()
    if not folder.exists() or not folder.is_dir():
        print(f"Not a directory: {folder}", file=sys.stderr)
        return 2

    errors, warnings, metadata = validate_folder(
        folder,
        allow_placeholders=args.allow_placeholders,
        strict=args.strict,
        completion_gate=args.completion_gate,
        completion_phase=args.phase,
    )
    result: dict[str, Any] = {
        "folder": str(folder),
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "metadata": metadata,
    }
    if args.quality_score:
        result["quality"] = score_quality(errors, warnings, metadata.get("phase_count", 0))

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        if errors:
            print("Harness validation failed")
            for error in errors:
                print(f"ERROR: {error}")
        else:
            print("Harness validation passed")
        for warning in warnings:
            print(f"WARNING: {warning}")
        if args.quality_score:
            quality = result["quality"]
            print(f"Quality score: {quality['score']} ({quality['band']})")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
