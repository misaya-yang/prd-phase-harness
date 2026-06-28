from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUICK_VALIDATE = ROOT / "scripts" / "quick_validate.py"


def run_quick_validate(skill_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(QUICK_VALIDATE), str(skill_dir)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def copy_skill(dest_parent: Path) -> Path:
    dest = dest_parent / "skill_copy"
    shutil.copytree(ROOT, dest, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    return dest


class SkillSelfValidationTests(unittest.TestCase):
    def test_real_skill_repository_passes(self) -> None:
        result = run_quick_validate(ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Skill self-validation passed", result.stdout)

    def test_detects_dangling_referenced_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = copy_skill(Path(tmp))
            # Remove a reference SKILL.md still points at: a dangling pointer
            # is exactly the failure class this self-check exists to catch.
            (skill / "references" / "security-protocol.md").unlink()

            result = run_quick_validate(skill)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("references a missing file: references/security-protocol.md", result.stdout)

    def test_detects_missing_script_referenced_in_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = copy_skill(Path(tmp))
            (skill / "scripts" / "validate_harness_prd.py").unlink()

            result = run_quick_validate(skill)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("scripts/validate_harness_prd.py", result.stdout)

    def test_detects_invalid_frontmatter_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = copy_skill(Path(tmp))
            skill_md = skill / "SKILL.md"
            text = skill_md.read_text(encoding="utf-8")
            text = text.replace("name: prd-phase-harness", "name: Bad Name", 1)
            skill_md.write_text(text, encoding="utf-8")

            result = run_quick_validate(skill)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("`name` must be lowercase-with-hyphens", result.stdout)

    def test_orphan_reference_is_warning_not_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = copy_skill(Path(tmp))
            # A reference doc that SKILL.md never cites should warn, not fail.
            (skill / "references" / "unused-note.md").write_text("# Unused\n", encoding="utf-8")

            result = run_quick_validate(skill)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Orphan reference not cited by SKILL.md: references/unused-note.md", result.stdout)


if __name__ == "__main__":
    unittest.main()
