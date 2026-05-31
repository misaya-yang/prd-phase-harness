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
    "## Source Packet",
    "## Current System Shape",
    "## Phase Order",
    "## Shared Harness Rules",
]

REQUIRED_MANIFEST_SECTIONS = [
    "## Grep Usage",
    "## Phase Index",
    "## Phase Report Index",
    "## Dependency Flow",
    "## Validation Matrix",
    "## Goal Setup Templates",
    "## Shared Agent Rules",
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


def phase_files(folder: Path) -> list[Path]:
    files: list[Path] = []
    for path in folder.glob("phase-*.md"):
        if re.match(r"phase-\d{2}-[a-z0-9][a-z0-9-]*\.md$", path.name):
            files.append(path)
    return sorted(files)


def contains_vague_language(value: Any) -> list[str]:
    rendered = textify(value).lower()
    return [pattern for pattern in VAGUE_PATTERNS if re.search(pattern, rendered)]


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

    return errors, warnings, data


def score_quality(errors: list[str], warnings: list[str], phase_count: int) -> dict[str, Any]:
    raw = 100
    raw -= min(70, len(errors) * 10)
    raw -= min(20, len(warnings) * 3)
    raw += min(5, phase_count)
    score = max(0, min(100, raw))
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
