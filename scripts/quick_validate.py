#!/usr/bin/env python3
"""Self-validate the PRD Phase Harness skill repository.

This runs the skill-level half of the Final Quality Gate as executable checks,
so "the skill itself is healthy" is a command instead of a prose checklist:

- SKILL.md exists and its YAML frontmatter has a valid `name` and `description`.
- Every file SKILL.md points at exists (references/*.md, scripts/*.py, assets/).
- No orphan reference docs (each references/*.md is cited by SKILL.md) and no
  orphan templates (each assets/*.template.md is read by the scaffold).
- scripts/*.py compile.
- The scaffold emits every runtime artifact and passes the structural validator
  with --allow-placeholders (a starter must always be executable).

It deliberately does NOT run the unittest suite (a test invokes this script, so
running the suite here would recurse). Run `python3 -m unittest discover tests`
for behavioral coverage, and `validate_harness_prd.py --strict`/`--completion-gate`
for generated harnesses.

Exit code 0 = healthy skill, 1 = problems found, 2 = bad invocation.
"""

from __future__ import annotations

import argparse
import json
import py_compile
import re
import subprocess
import sys
import tempfile
from pathlib import Path


NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NAME_MAX = 64
DESCRIPTION_MAX = 1024

# Runtime artifacts a finished scaffold must emit. Kept in sync with
# validate_harness_prd.RUNTIME_FILES; mirrored here to avoid importing it.
SCAFFOLD_RUNTIME_FILES = [
    "context-profile.json",
    "source-packet.md",
    "loop-contract.json",
    "loop-state.json",
    "feature-oracle.json",
    "progress-log.md",
    "agent-handoff.md",
    "continuity-ledger.md",
    "next-window-prompt.md",
]
SCAFFOLD_STRUCTURE_FILES = ["README.md", "phase-manifest.md"]


def parse_frontmatter(text: str) -> tuple[dict[str, str] | None, str | None]:
    """Parse the leading `---` YAML block into a flat key->value dict.

    Intentionally dependency-free (no PyYAML) to match the rest of the skill's
    stdlib-only scripts and stay portable across Codex/Claude Code environments.
    Only flat `key: value` pairs are needed here (name, description).
    """
    if not text.startswith("---"):
        return None, "SKILL.md does not begin with a '---' frontmatter block"
    lines = text.splitlines()
    closing = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            closing = index
            break
    if closing is None:
        return None, "SKILL.md frontmatter block is not closed with '---'"

    data: dict[str, str] = {}
    current_key: str | None = None
    for raw in lines[1:closing]:
        if not raw.strip():
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", raw)
        if match:
            current_key = match.group(1)
            data[current_key] = match.group(2).strip()
        elif current_key is not None and (raw.startswith(" ") or raw.startswith("\t")):
            # Folded continuation line for the previous key.
            data[current_key] = (data[current_key] + " " + raw.strip()).strip()
    return data, None


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def check_frontmatter(skill_dir: Path, skill_md: str, errors: list[str], warnings: list[str]) -> None:
    data, parse_error = parse_frontmatter(skill_md)
    if parse_error:
        errors.append(parse_error)
        return

    name = strip_quotes(data.get("name", ""))
    description = strip_quotes(data.get("description", ""))

    if not name:
        errors.append("SKILL.md frontmatter missing `name`")
    else:
        if not NAME_PATTERN.match(name):
            errors.append(f"SKILL.md `name` must be lowercase-with-hyphens: {name!r}")
        if len(name) > NAME_MAX:
            errors.append(f"SKILL.md `name` exceeds {NAME_MAX} chars: {len(name)}")
        if name != skill_dir.name:
            warnings.append(
                f"SKILL.md `name` ({name!r}) does not match the skill directory ({skill_dir.name!r})"
            )

    if not description:
        errors.append("SKILL.md frontmatter missing `description`")
    elif len(description) > DESCRIPTION_MAX:
        errors.append(f"SKILL.md `description` exceeds {DESCRIPTION_MAX} chars: {len(description)}")


def check_referenced_files(skill_dir: Path, skill_md: str, errors: list[str]) -> None:
    """Every references/*.md and scripts/*.py path named in SKILL.md must exist."""
    referenced = sorted(set(re.findall(r"(?:references/[\w./-]+\.md|scripts/[\w./-]+\.py)", skill_md)))
    for rel in referenced:
        if not (skill_dir / rel).exists():
            errors.append(f"SKILL.md references a missing file: {rel}")

    # assets/*.template.md is referenced via a glob in the Resource Map.
    assets = skill_dir / "assets"
    if "assets/" in skill_md:
        if not assets.is_dir():
            errors.append("SKILL.md references assets/ but the directory is missing")
        elif not any(assets.glob("*.template.md")):
            errors.append("assets/ has no *.template.md files but SKILL.md references them")


def check_no_orphans(skill_dir: Path, skill_md: str, errors: list[str], warnings: list[str]) -> None:
    """Flag reference docs not cited by SKILL.md and templates the scaffold never reads."""
    references_dir = skill_dir / "references"
    if references_dir.is_dir():
        for ref in sorted(references_dir.glob("*.md")):
            rel = f"references/{ref.name}"
            if rel not in skill_md:
                warnings.append(f"Orphan reference not cited by SKILL.md: {rel}")

    scaffold = skill_dir / "scripts" / "scaffold_harness_prd.py"
    assets_dir = skill_dir / "assets"
    if scaffold.exists() and assets_dir.is_dir():
        scaffold_src = scaffold.read_text(encoding="utf-8")
        used = set(re.findall(r"read_template\(\s*[\"']([^\"']+)[\"']", scaffold_src))
        for template in sorted(assets_dir.glob("*.template.md")):
            if template.name not in used:
                warnings.append(f"Orphan template never read by the scaffold: assets/{template.name}")


def check_scripts_compile(skill_dir: Path, errors: list[str]) -> None:
    scripts_dir = skill_dir / "scripts"
    for script in sorted(scripts_dir.glob("*.py")):
        try:
            py_compile.compile(str(script), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"Script fails to compile: scripts/{script.name}: {exc.msg}")


def check_scaffold_smoke(skill_dir: Path, errors: list[str]) -> None:
    """Generate a throwaway harness and confirm it validates with --allow-placeholders."""
    scaffold = skill_dir / "scripts" / "scaffold_harness_prd.py"
    validator = skill_dir / "scripts" / "validate_harness_prd.py"
    if not scaffold.exists() or not validator.exists():
        errors.append("Cannot run scaffold smoke test: scaffold or validator script is missing")
        return

    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / "self_check_harness"
        scaffold_result = subprocess.run(
            [
                sys.executable, str(scaffold),
                "--output", str(output),
                "--title", "Skill Self-Check Harness",
                "--purpose", "Confirm the scaffold emits an executable starter harness.",
                "--prefix", "SC",
                "--phase", "Baseline Audit",
                "--phase", "Implementation Slice",
            ],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        if scaffold_result.returncode != 0:
            errors.append(f"Scaffold smoke test failed to generate: {scaffold_result.stderr.strip()}")
            return

        for name in [*SCAFFOLD_STRUCTURE_FILES, *SCAFFOLD_RUNTIME_FILES]:
            if not (output / name).exists():
                errors.append(f"Scaffold smoke test did not emit {name}")

        validate_result = subprocess.run(
            [sys.executable, str(validator), str(output), "--allow-placeholders"],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        if validate_result.returncode != 0:
            errors.append(
                "Scaffold smoke test output failed --allow-placeholders validation:\n"
                + validate_result.stdout.strip()
            )


def validate_skill(skill_dir: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    skill_path = skill_dir / "SKILL.md"
    if not skill_path.exists():
        return [f"Missing SKILL.md in {skill_dir}"], warnings
    skill_md = skill_path.read_text(encoding="utf-8")

    check_frontmatter(skill_dir, skill_md, errors, warnings)
    check_referenced_files(skill_dir, skill_md, errors)
    check_no_orphans(skill_dir, skill_md, errors, warnings)
    check_scripts_compile(skill_dir, errors)
    check_scaffold_smoke(skill_dir, errors)
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "skill_dir",
        nargs="?",
        default=str(Path(__file__).resolve().parents[1]),
        help="Skill root to validate (defaults to this skill repository).",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of human-readable output")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).expanduser()
    if not skill_dir.is_dir():
        print(f"Not a directory: {skill_dir}", file=sys.stderr)
        return 2

    errors, warnings = validate_skill(skill_dir)
    result = {
        "skill_dir": str(skill_dir),
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
    }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        if errors:
            print("Skill self-validation failed")
            for error in errors:
                print(f"ERROR: {error}")
        else:
            print("Skill self-validation passed")
        for warning in warnings:
            print(f"WARNING: {warning}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
