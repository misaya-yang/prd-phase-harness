# PRD Phase Harness

Agent-ready PRD phase harness skill for Codex, Claude Code, and other goal-mode coding agents.

This repository packages a portable skill that turns full PRDs, Figma UI, existing codebases, research notes, or rough oral requests into a harness-style phase folder:

- `README.md` for roadmap, product thesis, loading protocol, and shared rules
- `phase-manifest.md` for a compact agent index, dependency flow, validation matrix, and goal prompt templates
- `phase-XX-*.md` files with bounded task contracts, context policy, requirements, tests, compliance gates, evidence capture, and stop conditions

## Why This Exists

Goal-mode coding agents are strongest when the work is not only described, but made executable. A normal PRD explains intent. A phase harness gives an agent context policy, edit boundaries, validation commands, regression scope, compliance gates, evidence outputs, and acceptance criteria.

The result is a more reliable workflow:

1. Load the folder-level roadmap.
2. Pick exactly one phase from the manifest.
3. Start from the phase's `GOAL_PROMPT`.
4. Plan before editing.
5. Execute inside bounded paths.
6. Run validation and regression checks.
7. Capture durable evidence.
8. Move to the next phase only after gates pass.

## Install

Clone this repository and copy or symlink it into your Codex skills directory:

```bash
git clone https://github.com/misaya-yang/prd-phase-harness.git
mkdir -p ~/.codex/skills
cp -R prd-phase-harness ~/.codex/skills/prd-phase-harness
```

For compatible Claude Code skill workflows, keep `SKILL.md`, `references/`, `assets/`, and `scripts/` together.

## Use

Invoke the skill with a request like:

```text
Use $prd-phase-harness to turn this PRD or rough product request into a harness-style phase folder with README, manifest, bounded phase specs, tests, and acceptance gates.
```

Good inputs include:

- A complete PRD
- A Figma URL or screenshot set
- A codebase plus a feature request
- Research notes
- A rough oral requirement such as "I want to add a publishing workflow"

## Scaffold

The helper script creates a starter folder that you can then tighten with project-specific context:

```bash
python3 scripts/scaffold_harness_prd.py \
  --output docs/new_feature_harness \
  --title "New Feature Harness PRD Roadmap" \
  --owner "Product/engineering" \
  --purpose "Convert the feature request into bounded agent implementation phases." \
  --prefix NF \
  --phase "Baseline Audit" \
  --phase "Core Data Model" \
  --phase "User Experience" \
  --phase "Release Gates"
```

## Repository Layout

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── assets/
│   ├── README.template.md
│   ├── phase-manifest.template.md
│   └── phase.template.md
├── references/
│   ├── phase-folder-spec.md
│   └── research-notes.md
└── scripts/
    └── scaffold_harness_prd.py
```

## Core Contract

Every phase file should be assignable as a standalone agent goal and include these grep-friendly anchors:

- `PHASE_ID`
- `GOAL_TARGET`
- `GOAL_PROMPT`
- `DEPENDS_ON`
- `READ_FIRST`
- `PRIMARY_CONTEXT`
- `LIKELY_EDIT_PATHS`
- `DO_NOT_EDIT`
- `EXECUTION_MODE`
- `VALIDATION_COMMANDS`
- `BROWSER_CHECKS`
- `REGRESSION_SCOPE`
- `COMPLIANCE_GATES`
- `ACCEPTANCE_GATES`
- `EVIDENCE_OUTPUT`
- `STOP_CONDITIONS`

## Validation

Local validation used before publishing:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/.codex/skills/prd-phase-harness
python3 -m py_compile ~/.codex/skills/prd-phase-harness/scripts/scaffold_harness_prd.py
python3 ~/.codex/skills/prd-phase-harness/scripts/scaffold_harness_prd.py --output /tmp/prd-phase-harness-smoke --title "Smoke Harness" --purpose "Smoke test scaffold generation." --prefix SM --phase "Baseline Audit" --phase "Implementation" --phase "Release Gates" --force
```

## License

No license is currently included. Add one before treating this as open-source reusable software.
