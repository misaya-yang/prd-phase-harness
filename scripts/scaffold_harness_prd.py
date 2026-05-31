#!/usr/bin/env python3
"""Scaffold a harness-style PRD phase folder from templates."""

from __future__ import annotations

import argparse
import datetime as dt
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="Output docs folder, for example docs/new_feature")
    parser.add_argument("--title", required=True, help="README title")
    parser.add_argument("--owner", default="Product/engineering", help="Roadmap owner")
    parser.add_argument("--purpose", required=True, help="One-sentence folder purpose")
    parser.add_argument("--prefix", default="PH", help="Phase ID prefix, for example PO or HE")
    parser.add_argument("--phase", action="append", required=True, help="Phase name. Repeat once per phase.")
    parser.add_argument("--repo-path", default=".", help="Repo path to put in GOAL_PROMPT")
    parser.add_argument("--force", action="store_true", help="Overwrite existing scaffold files")
    args = parser.parse_args()

    output = Path(args.output).expanduser()
    output.mkdir(parents=True, exist_ok=True)

    existing = [p for p in [output / "README.md", output / "phase-manifest.md"] if p.exists()]
    if existing and not args.force:
        paths = ", ".join(str(p) for p in existing)
        raise SystemExit(f"Refusing to overwrite existing files without --force: {paths}")

    docs_path = str(output)
    phases: list[dict[str, str]] = []
    for index, name in enumerate(args.phase):
        number = f"{index:02d}"
        pid = phase_id(args.prefix, index)
        slug = slugify(name)
        file_name = f"phase-{number}-{slug}.md"
        phases.append(
            {
                "number": number,
                "id": pid,
                "name": name,
                "slug": slug,
                "file": file_name,
                "depends_on": "none" if index == 0 else phase_id(args.prefix, index - 1),
            }
        )

    phase_order_rows = "\n".join(
        f"| Phase {p['number']} | {p['name']} | TODO: core outcome |" for p in phases
    )
    phase_index_rows = "\n".join(
        f"| {p['id']} | `{p['file']}` | {p['depends_on']} | TODO: goal target | TODO: validation | TODO: evidence |"
        for p in phases
    )
    validation_matrix_rows = "\n".join(
        f"| {p['id']} | TODO | TODO | TODO | TODO | TODO |" for p in phases
    )
    dependency_flow = "\n  -> ".join(f"{p['id']} {p['name']}" for p in phases)
    first = phases[0]
    goal_example = (
        f"Complete {first['id']} {first['name']} for `{args.repo_path}` by following "
        f"`{docs_path}/{first['file']}`; finish only after validation, regression, "
        "compliance, evidence, and acceptance gates pass or blockers are documented."
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
            "PRODUCT_THESIS": "TODO: summarize the product or engineering thesis.",
            "INPUT_SOURCES": "TODO: list PRD, Figma/design links, interviews, codebase docs, and assumptions.",
            "CURRENT_SHAPE": "TODO: summarize current system shape and relevant constraints.",
            "PHASE_ORDER_ROWS": phase_order_rows,
            "ROADMAP_COHESION": "TODO: explain why these phases are ordered this way.",
            "GLOBAL_NON_GOALS": "- TODO: list scope exclusions.",
            "STANDARD_VERIFICATION_COMMANDS": "```bash\nTODO: add project validation commands\n```",
            "REQUIRED_BROWSER_CHECKS": "TODO: list routes, viewports, devices, or write none.",
        },
    )
    manifest = render(
        read_template("phase-manifest.template.md"),
        {
            "TOPIC": args.title,
            "PREFIX": args.prefix.upper(),
            "DOCS_PATH": docs_path,
            "PHASE_INDEX_ROWS": phase_index_rows,
            "DEPENDENCY_FLOW": dependency_flow,
            "VALIDATION_MATRIX_ROWS": validation_matrix_rows,
            "GOAL_PROMPT_EXAMPLE": goal_example,
            "SHARED_AGENT_RULES": "- Stay inside phase boundaries.\n- Do not claim completion without evidence.\n- Document blockers explicitly.",
        },
    )

    (output / "README.md").write_text(readme, encoding="utf-8")
    (output / "phase-manifest.md").write_text(manifest, encoding="utf-8")

    phase_template = read_template("phase.template.md")
    for p in phases:
        path = output / p["file"]
        if path.exists() and not args.force:
            raise SystemExit(f"Refusing to overwrite existing phase without --force: {path}")
        rendered = render(
            phase_template,
            {
                "PHASE_NUMBER": p["number"],
                "PHASE_NAME": p["name"],
                "GOAL": "TODO: one clear outcome.",
                "ARCHITECTURE": "TODO: describe how this phase fits the existing system.",
                "TECH_STACK": "TODO: list frameworks, services, files, and tools.",
                "PHASE_ID": p["id"],
                "GOAL_TARGET": "TODO: single sentence target.",
                "REPO_PATH": args.repo_path,
                "PHASE_FILE": f"{docs_path}/{p['file']}",
                "GOAL_PROMPT_CONSTRAINTS": "TODO: key constraints",
                "DEPENDS_ON": p["depends_on"],
                "DOCS_PATH": docs_path,
                "PRIMARY_CONTEXT": "TODO: exact files/routes/design artifacts to inspect",
                "LIKELY_EDIT_PATHS": "TODO: bounded paths",
                "DO_NOT_EDIT": "TODO: protected paths and non-goals",
                "VALIDATION_COMMANDS": "TODO: commands",
                "BROWSER_CHECKS": "TODO: routes/viewports or none",
                "REGRESSION_SCOPE": "TODO: behavior that must still work",
                "COMPLIANCE_GATES": "TODO: privacy/security/a11y/data/content gates",
                "ACCEPTANCE_GATES": "TODO: deterministic acceptance gates",
                "EVIDENCE_OUTPUT": f"`{docs_path}/reports/{p['id'].lower()}-{p['slug']}-report.md`",
                "STOP_CONDITIONS": "TODO: when to stop and ask/document instead of guessing",
                "TASK_SPEC": "TODO: describe the behavior to build.",
                "IN_SCOPE": "- TODO",
                "OUT_OF_SCOPE": "- TODO",
                "CONTEXT_POLICY": "- TODO",
                "R1_NAME": "Requirement",
                "R1_BODY": "TODO: observable requirement.",
                "TEST_AND_REGRESSION_REQUIREMENTS": "TODO: tests, command checks, browser checks, evals.",
                "COMPLIANCE_AND_SAFETY_REQUIREMENTS": "TODO: privacy, auth, accessibility, migration, retention, content boundaries.",
                "EXECUTION_CAPTURE": "TODO: reports, screenshots, logs, tables, command summaries.",
                "EVALUATOR_PROTOCOL": "TODO: how to judge completion.",
                "ACCEPTANCE_CRITERIA": "- TODO",
                "RISKS": "- TODO",
            },
        )
        path.write_text(rendered, encoding="utf-8")

    print(f"Created harness PRD scaffold at {output}")
    print(f"Phases: {', '.join(p['id'] for p in phases)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
