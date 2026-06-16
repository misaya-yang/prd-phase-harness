#!/usr/bin/env python3
"""Scaffold a harness-style PRD phase folder from templates."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "phase"


def read_template(name: str) -> str:
    return (ASSETS / name).read_text(encoding="utf-8")


def render(template: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def phase_id(prefix: str, index: int) -> str:
    return f"{prefix.upper()}-{index:02d}"


def phase_contract(
    *,
    phase: dict[str, str],
    phases: list[dict[str, str]],
    index: int,
    repo_path: str,
    docs_path: str,
) -> str:
    dep = [] if phase["depends_on"] == "none" else [phase["depends_on"]]
    unlocks = [phases[index + 1]["id"]] if index + 1 < len(phases) else []
    phase_file = f"{docs_path}/{phase['file']}"
    report = f"{docs_path}/{phase['report']}"
    feature_oracle = f"{docs_path}/feature-oracle.json"
    loop_contract = f"{docs_path}/loop-contract.json"
    loop_state = f"{docs_path}/loop-state.json"
    progress_log = f"{docs_path}/progress-log.md"
    agent_handoff = f"{docs_path}/agent-handoff.md"
    next_window_prompt = f"{docs_path}/next-window-prompt.md"
    prompt = (
        f"Complete {phase['id']} {phase['name']} for `{repo_path}` by following `{phase_file}`; "
        "TODO: key constraints; stay inside the named edit boundaries; finish only after validation, "
        "regression, compliance, rollback, evidence, and acceptance gates pass or blockers are documented."
    )
    contract = {
        "schema_version": "prd-phase-harness/v3",
        "harness_role": "execution",
        "phase": {
            "id": phase["id"],
            "number": phase["number"],
            "title": phase["name"],
            "status": "draft",
            "type": "baseline" if index == 0 else "implementation",
            "repo_path": repo_path,
            "docs_path": docs_path,
            "phase_file": phase_file,
            "depends_on": dep,
            "unlocks": unlocks,
        },
        "goal": {
            "target": "TODO: single sentence target.",
            "prompt": prompt,
            "plan_required": True,
            "plan_output": f"{docs_path}/reports/{phase['id'].lower()}-{phase['slug']}-plan.md",
            "completion_report": report,
        },
        "runtime": {
            "feature_oracle": feature_oracle,
            "loop_contract": loop_contract,
            "loop_state": loop_state,
            "progress_log": progress_log,
            "handoff": agent_handoff,
            "next_window_prompt": next_window_prompt,
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
                loop_contract,
                loop_state,
                feature_oracle,
                progress_log,
                agent_handoff,
                next_window_prompt,
                phase_file,
            ],
            "primary_context": ["TODO: exact files/routes/design artifacts to inspect"],
            "context_budget": "focused",
            "do_not_load_unless": ["TODO: unrelated files; expand only when a blocker is documented"],
        },
        "boundaries": {
            "likely_edit_paths": ["TODO: bounded paths"],
            "do_not_edit": ["TODO: protected paths and non-goals"],
            "external_inputs": ["TODO: credentials, dashboards, Figma, deployment, DNS, or none"],
            "secrets_required": [],
        },
        "tool_policy": {
            "allowed_tools": ["repo search", "shell validation"],
            "approval_required": [
                "production data mutation",
                "destructive commands",
                "external service changes",
                "deployment",
            ],
            "dangerous_commands": ["git reset --hard", "rm -rf", "production migration"],
        },
        "risk": {
            "tags": ["baseline" if index == 0 else "implementation"],
            "data_mutation": "unknown",
            "migration_required": "unknown",
            "browser_required": "unknown",
            "ai_eval_required": "unknown",
            "external_service_required": "unknown",
            "release_blocking": "unknown",
        },
        "validation": {
            "commands": [
                {
                    "id": "TODO-validation",
                    "cwd": repo_path,
                    "command": "TODO: command",
                    "expected": "TODO: expected result",
                    "required": True,
                }
            ],
            "browser_checks": ["TODO: routes/viewports or none"],
            "regression_scope": ["TODO: behavior that must still work"],
            "compliance_gates": ["TODO: privacy/security/a11y/data/content gates"],
            "acceptance_gates": ["TODO: deterministic acceptance gates"],
            "rollback_plan": ["TODO: rollback notes, migration reversal, feature flag, or none"],
        },
        "evidence": {
            "outputs": [report],
            "required_artifacts": ["phase report"],
            "waiver_policy": "Only mark a gate waived when the user explicitly waives it or the report documents a blocker and remaining evidence.",
            "next_phase_handoff": "State whether dependent phases are unlocked and what the next agent must know.",
        },
        "stop_conditions": ["TODO: when to stop and ask/document instead of guessing"],
    }
    return json.dumps(contract, indent=2)


def fail_if_exists(paths: list[Path], force: bool) -> None:
    existing = [path for path in paths if path.exists()]
    if existing and not force:
        joined = ", ".join(str(path) for path in existing)
        raise SystemExit(f"Refusing to overwrite existing files without --force: {joined}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="Output docs folder, for example docs/new_feature")
    parser.add_argument("--title", required=True, help="README title")
    parser.add_argument("--owner", default="Product/engineering", help="Roadmap owner")
    parser.add_argument("--purpose", required=True, help="One-sentence folder purpose")
    parser.add_argument("--prefix", default="PH", help="Phase ID prefix, for example PO, EMAIL, or HE")
    parser.add_argument("--phase", action="append", required=True, help="Phase name. Repeat once per phase.")
    parser.add_argument("--repo-path", default=".", help="Repo path to put in GOAL_PROMPT")
    parser.add_argument("--force", action="store_true", help="Overwrite existing scaffold files")
    parser.add_argument(
        "--no-report-template",
        action="store_true",
        help="Do not create reports/phase-report-template.md",
    )
    parser.add_argument(
        "--source-packet",
        action="store_true",
        help="Deprecated no-op. source-packet.md is now created by default.",
    )
    parser.add_argument(
        "--no-source-packet",
        action="store_true",
        help="Do not create source-packet.md",
    )
    args = parser.parse_args()

    output = Path(args.output).expanduser()
    reports_dir = output / "reports"
    report_template_path = reports_dir / "phase-report-template.md"

    output.mkdir(parents=True, exist_ok=True)
    if not args.no_report_template:
        reports_dir.mkdir(parents=True, exist_ok=True)

    phases: list[dict[str, str]] = []
    for index, name in enumerate(args.phase):
        number = f"{index:02d}"
        pid = phase_id(args.prefix, index)
        slug = slugify(name)
        file_name = f"phase-{number}-{slug}.md"
        report_name = f"reports/{pid.lower()}-{slug}-report.md"
        phases.append(
            {
                "number": number,
                "id": pid,
                "name": name,
                "slug": slug,
                "file": file_name,
                "report": report_name,
                "depends_on": "none" if index == 0 else phase_id(args.prefix, index - 1),
            }
        )

    source_packet_enabled = not args.no_source_packet
    source_packet_path = output / "source-packet.md"
    runtime_paths = [
        output / "loop-contract.json",
        output / "loop-state.json",
        output / "feature-oracle.json",
        output / "progress-log.md",
        output / "agent-handoff.md",
        output / "next-window-prompt.md",
    ]
    output_files = [output / "README.md", output / "phase-manifest.md"]
    output_files.extend(output / phase["file"] for phase in phases)
    output_files.extend(runtime_paths)
    if not args.no_report_template:
        output_files.append(report_template_path)
    if source_packet_enabled:
        output_files.append(source_packet_path)
    fail_if_exists(output_files, args.force)

    docs_path = str(output)
    phase_order_rows = "\n".join(
        f"| Phase {phase['number']} | {phase['name']} | TODO: core outcome | `{phase['report']}` |"
        for phase in phases
    )
    phase_index_rows = "\n".join(
        f"| {phase['id']} | `{phase['file']}` | {phase['depends_on']} | TODO: goal target | TODO: validation | `{phase['report']}` |"
        for phase in phases
    )
    phase_report_rows = "\n".join(
        f"| {phase['id']} | `{phase['report']}` |" for phase in phases
    )
    validation_matrix_rows = "\n".join(
        f"| {phase['id']} | TODO | TODO | TODO | TODO | TODO | TODO |" for phase in phases
    )
    risk_matrix_rows = "\n".join(
        f"| {phase['id']} | TODO: primary risk | TODO: stop condition |" for phase in phases
    )
    dependency_flow = "\n  -> ".join(f"{phase['id']} {phase['name']}" for phase in phases)
    first = phases[0]
    goal_example = (
        f"Complete {first['id']} {first['name']} for `{args.repo_path}` by following "
        f"`{docs_path}/{first['file']}`; stay inside named edit boundaries; finish only after "
        "validation, regression, compliance, rollback, evidence, and acceptance gates pass or "
        "blockers are documented."
    )

    today = dt.date.today().isoformat()
    readme = render(
        read_template("README.template.md"),
        {
            "TITLE": args.title,
            "DATE": today,
            "OWNER": args.owner,
            "PURPOSE": args.purpose,
            "DOCS_PATH": docs_path,
            "PRODUCT_THESIS": "TODO: summarize the product or engineering thesis as executable intent.",
            "INPUT_SOURCES": "- TODO: list PRD, Figma/design links, interviews, codebase docs, research, and assumptions.",
            "CURRENT_SHAPE": "TODO: summarize current system shape, architecture, constraints, and known risks.",
            "ASSUMPTIONS_AND_DECISIONS": "- TODO: list assumptions and decisions that should survive chat context.",
            "PHASE_ORDER_ROWS": phase_order_rows,
            "LOOP_CONTRACT_PATH": f"{docs_path}/loop-contract.json",
            "LOOP_STATE_PATH": f"{docs_path}/loop-state.json",
            "FEATURE_ORACLE_PATH": f"{docs_path}/feature-oracle.json",
            "PROGRESS_LOG_PATH": f"{docs_path}/progress-log.md",
            "AGENT_HANDOFF_PATH": f"{docs_path}/agent-handoff.md",
            "NEXT_WINDOW_PROMPT_PATH": f"{docs_path}/next-window-prompt.md",
            "ROADMAP_COHESION": "TODO: explain why these phases are ordered this way and what each dependency protects.",
            "SHARED_HARNESS_RULES": "- Stay inside phase boundaries.\n- Plan before editing.\n- Do not claim completion without durable evidence.\n- Document blockers and user waivers explicitly.",
            "GLOBAL_NON_GOALS": "- TODO: list scope exclusions and future ideas that must not leak into phases.",
            "GLOBAL_COMPLIANCE_GATES": "- TODO: privacy, auth, a11y, security, data retention, content, licensing, or migration gates.",
            "STANDARD_VERIFICATION_COMMANDS": "```bash\nTODO: add project validation commands\n```",
            "REQUIRED_BROWSER_CHECKS": "TODO: list routes, viewports, devices, evals, or write none.",
            "EXTERNAL_INPUTS_AND_APPROVALS": "- TODO: list credentials, dashboards, deployment, migrations, DNS, Figma access, or write none.",
        },
    )
    manifest = render(
        read_template("phase-manifest.template.md"),
        {
            "TOPIC": args.title,
            "PREFIX": args.prefix.upper(),
            "DOCS_PATH": docs_path,
            "PHASE_INDEX_ROWS": phase_index_rows,
            "PHASE_REPORT_ROWS": phase_report_rows,
            "DEPENDENCY_FLOW": dependency_flow,
            "VALIDATION_MATRIX_ROWS": validation_matrix_rows,
            "RISK_MATRIX_ROWS": risk_matrix_rows,
            "LOOP_CONTRACT_PATH": f"{docs_path}/loop-contract.json",
            "LOOP_STATE_PATH": f"{docs_path}/loop-state.json",
            "FEATURE_ORACLE_PATH": f"{docs_path}/feature-oracle.json",
            "PROGRESS_LOG_PATH": f"{docs_path}/progress-log.md",
            "AGENT_HANDOFF_PATH": f"{docs_path}/agent-handoff.md",
            "NEXT_WINDOW_PROMPT_PATH": f"{docs_path}/next-window-prompt.md",
            "GOAL_PROMPT_EXAMPLE": goal_example,
            "SHARED_AGENT_RULES": "- Use the exact phase `GOAL_PROMPT` when starting a goal.\n- Open only `READ_FIRST` and `PRIMARY_CONTEXT` before planning.\n- Expand edit scope only when a blocker is documented.\n- Write the phase report before moving on.",
            "EXTERNAL_INPUTS_CHECKLIST": "- TODO: list inputs not guaranteed to exist in the repo.",
        },
    )

    (output / "README.md").write_text(readme, encoding="utf-8")
    (output / "phase-manifest.md").write_text(manifest, encoding="utf-8")

    if source_packet_enabled:
        source_packet = render(
            read_template("source-packet.template.md"),
            {
                "TITLE": args.title,
                "DATE": today,
                "DOCS_PATH": docs_path,
            },
        )
        source_packet_path.write_text(source_packet, encoding="utf-8")

    loop_contract = {
        "schema_version": "prd-phase-harness/loop-contract/v1",
        "goal": "Run one bounded phase and one feature-oracle item until evidence proves pass, block, or fail.",
        "cycle": ["observe", "select", "execute", "verify", "record", "decide"],
        "max_iterations": 3,
        "state_file": f"{docs_path}/loop-state.json",
        "oracle_file": f"{docs_path}/feature-oracle.json",
        "progress_file": f"{docs_path}/progress-log.md",
        "handoff_file": f"{docs_path}/agent-handoff.md",
        "done_when": [
            "Selected phase report exists.",
            "Required validation evidence is recorded.",
            "Feature oracle status is passing, blocked, or waived.",
        ],
        "continue_when": [
            "Validator is clean.",
            "Work remains in the selected phase.",
            "Iteration is below max_iterations.",
        ],
        "stop_when": [
            "Credentials or approvals are missing.",
            "Validation fails outside phase scope.",
            "Edits outside the phase boundary are required.",
        ],
    }
    (output / "loop-contract.json").write_text(
        json.dumps(loop_contract, indent=2) + "\n",
        encoding="utf-8",
    )

    loop_state = {
        "schema_version": "prd-phase-harness/loop-state/v1",
        "active_phase": first["id"],
        "active_feature": f"{args.prefix.upper()}-F001",
        "iteration": 0,
        "status": "planned",
        "last_decision": "Start with the first phase and collect baseline evidence.",
        "next_action": f"Execute {first['id']} by following {docs_path}/{first['file']}.",
    }
    (output / "loop-state.json").write_text(
        json.dumps(loop_state, indent=2) + "\n",
        encoding="utf-8",
    )

    feature_oracle = {
        "schema_version": "prd-phase-harness/feature-oracle/v1",
        "instructions": {
            "allowed_edits": "Coding agents may update only status, evidence, and notes fields unless the user explicitly changes scope.",
            "completion_rule": "A feature is passing only after end-to-end evidence exists.",
            "status_values": ["failing", "passing", "blocked", "waived"],
        },
        "features": [
            {
                "id": f"{args.prefix.upper()}-F{index + 1:03d}",
                "phase_id": phase["id"],
                "category": "phase",
                "description": f"{phase['name']} phase completes its bounded goal and writes durable evidence.",
                "steps": [
                    f"Open {docs_path}/{phase['file']}.",
                    "Execute only the assigned phase contract.",
                    f"Write {docs_path}/{phase['report']} with validation evidence.",
                ],
                "status": "failing",
                "evidence": "",
                "notes": "",
            }
            for index, phase in enumerate(phases)
        ],
    }
    (output / "feature-oracle.json").write_text(
        json.dumps(feature_oracle, indent=2) + "\n",
        encoding="utf-8",
    )

    progress_log = render(
        read_template("progress-log.template.md"),
        {
            "TITLE": args.title,
            "DATE": today,
            "DOCS_PATH": docs_path,
        },
    )
    (output / "progress-log.md").write_text(progress_log, encoding="utf-8")

    handoff = render(
        read_template("agent-handoff.template.md"),
        {
            "TITLE": args.title,
            "DATE": today,
            "DOCS_PATH": docs_path,
            "FIRST_PHASE_ID": first["id"],
            "FIRST_PHASE_FILE": f"{docs_path}/{first['file']}",
            "FEATURE_ORACLE_PATH": f"{docs_path}/feature-oracle.json",
            "PROGRESS_LOG_PATH": f"{docs_path}/progress-log.md",
        },
    )
    (output / "agent-handoff.md").write_text(handoff, encoding="utf-8")

    next_prompt = render(
        read_template("next-window-prompt.template.md"),
        {
            "TITLE": args.title,
            "DOCS_PATH": docs_path,
            "FIRST_PHASE_ID": first["id"],
            "FIRST_PHASE_FILE": f"{docs_path}/{first['file']}",
        },
    )
    (output / "next-window-prompt.md").write_text(next_prompt, encoding="utf-8")

    if not args.no_report_template:
        report_template = render(
            read_template("phase-report.template.md"),
            {
                "PHASE_ID": "PHASE-ID",
                "PHASE_NAME": "Phase Name",
            },
        )
        report_template_path.write_text(report_template, encoding="utf-8")

    phase_template = read_template("phase.template.md")
    for index, phase in enumerate(phases):
        contract_json = phase_contract(
            phase=phase,
            phases=phases,
            index=index,
            repo_path=args.repo_path,
            docs_path=docs_path,
        )
        rendered = render(
            phase_template,
            {
                "PHASE_NUMBER": phase["number"],
                "PHASE_NAME": phase["name"],
                "GOAL": "TODO: one clear outcome.",
                "ARCHITECTURE": "TODO: describe how this phase fits the existing system.",
                "TECH_STACK": "TODO: list frameworks, services, files, and tools.",
                "PHASE_CONTRACT_JSON": contract_json,
                "PHASE_ID": phase["id"],
                "GOAL_TARGET": "TODO: single sentence target.",
                "REPO_PATH": args.repo_path,
                "PHASE_FILE": f"{docs_path}/{phase['file']}",
                "GOAL_PROMPT_CONSTRAINTS": "TODO: key constraints",
                "DEPENDS_ON": phase["depends_on"],
                "DOCS_PATH": docs_path,
                "LOOP_CONTRACT_PATH": f"{docs_path}/loop-contract.json",
                "LOOP_STATE_PATH": f"{docs_path}/loop-state.json",
                "PRIMARY_CONTEXT": "TODO: exact files/routes/design artifacts to inspect",
                "LIKELY_EDIT_PATHS": "TODO: bounded paths",
                "DO_NOT_EDIT": "TODO: protected paths and non-goals",
                "VALIDATION_COMMANDS": "TODO: commands",
                "BROWSER_CHECKS": "TODO: routes/viewports or none",
                "REGRESSION_SCOPE": "TODO: behavior that must still work",
                "COMPLIANCE_GATES": "TODO: privacy/security/a11y/data/content gates",
                "ROLLBACK_PLAN": "TODO: rollback notes, migration reversal, feature flag, or none",
                "ACCEPTANCE_GATES": "TODO: deterministic acceptance gates",
                "EVIDENCE_OUTPUT": f"`{docs_path}/{phase['report']}`",
                "STOP_CONDITIONS": "TODO: when to stop and ask/document instead of guessing",
                "FEATURE_ORACLE_PATH": f"{docs_path}/feature-oracle.json",
                "PROGRESS_LOG_PATH": f"{docs_path}/progress-log.md",
                "AGENT_HANDOFF_PATH": f"{docs_path}/agent-handoff.md",
                "NEXT_WINDOW_PROMPT_PATH": f"{docs_path}/next-window-prompt.md",
                "TASK_SPEC": "TODO: describe the behavior to build or evidence to collect.",
                "IN_SCOPE": "- TODO",
                "OUT_OF_SCOPE": "- TODO",
                "CONTEXT_POLICY": "- TODO",
                "R1_NAME": "Requirement",
                "R1_BODY": "TODO: observable requirement.",
                "TEST_AND_REGRESSION_REQUIREMENTS": "TODO: tests, command checks, browser checks, evals.",
                "COMPLIANCE_AND_SAFETY_REQUIREMENTS": "TODO: privacy, auth, accessibility, migration, retention, content boundaries.",
                "ROLLBACK_AND_RECOVERY": "TODO: recovery path, rollback command, migration note, feature flag, or none.",
                "EXECUTION_CAPTURE": "TODO: reports, screenshots, logs, tables, command summaries.",
                "REPORT_TEMPLATE": f"`{docs_path}/reports/phase-report-template.md`",
                "EVALUATOR_PROTOCOL": "TODO: how to judge completion.",
                "ACCEPTANCE_CRITERIA": "- TODO",
                "RISKS": "- TODO",
            },
        )
        (output / phase["file"]).write_text(rendered, encoding="utf-8")

    print(f"Created harness PRD scaffold at {output}")
    print(f"Phases: {', '.join(phase['id'] for phase in phases)}")
    if not args.no_report_template:
        print(f"Report template: {report_template_path}")
    if source_packet_enabled:
        print(f"Source packet: {source_packet_path}")
    print("Runtime artifacts: loop-contract.json, loop-state.json, feature-oracle.json, progress-log.md, agent-handoff.md, next-window-prompt.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
