# PRD Phase Harness

Agent-executable PRD phase harness skill for Codex, Claude Code, and other goal-mode coding agents.

This repository packages a portable skill that converts PRDs, Figma designs, rough feature requests, or existing roadmap docs into a cold-start execution folder:

- `source-packet.md` for request facts, trust boundaries, assumptions, risks, and approvals
- `context-profile.json` for progressive-disclosure hot paths, deferred triggers, role load profiles, and context caps
- `loop-contract.json` and `loop-state.json` for the observe/select/execute/verify/record/decide control loop
- `feature-oracle.json` for end-to-end feature/test cases that stay visible across sessions
- `continuity-ledger.md` for phase relatedness, code-summary writeback, and interface boundary decisions
- `progress-log.md`, `agent-handoff.md`, and `next-window-prompt.md` for fresh-window recovery
- `README.md` for folder-level operating protocol
- `phase-manifest.md` for dependency flow, validation matrix, risk matrix, reports, and goal prompts
- `phase-XX-*.md` files with machine-readable JSON contracts and grep-friendly coding-agent contracts
- `reports/` for actor phase reports, independent critic verdicts, blockers, screenshots, eval tables, and handoff notes

## Why This Exists

Long-running coding agents do not fail only because the model is weak. They fail when a large product goal is handed over without a runtime harness: no bounded context, no edit boundary, no feature oracle, no regression bank, no durable report, and no dependency unlock rule.

A normal PRD says what the product should become. A Goal Harness says how a fresh agent should continue the work safely.

```text
intent -> context profile -> source packet -> loop contract -> loop state -> feature oracle -> continuity ledger -> phase map -> machine contract -> actor report -> independent critic verdict -> dependency unlock
```

## Install

Clone this repository and copy or symlink it into your skill directory:

```bash
git clone https://github.com/misaya-yang/prd-phase-harness.git
mkdir -p ~/.codex/skills
cp -R prd-phase-harness ~/.codex/skills/prd-phase-harness
```

For Claude Code or other Agent Skills-compatible workflows, keep `SKILL.md`, `references/`, `assets/`, and `scripts/` together.

## Use

```text
Use $prd-phase-harness to convert this PRD, Figma design, rough feature request, or existing roadmap into an executable long-running agent harness with source packet, context profile, loop contract, loop state, feature oracle, continuity ledger, progress log, planner/generator/critic handoff, critic verdict template, next-window prompt, manifest, machine contracts, phase reports, validation gates, completion gates, regression scope, and unlock rules.
```

## Scaffold

```bash
python3 scripts/scaffold_harness_prd.py \
  --output docs/new_feature_harness \
  --title "New Feature Harness PRD Roadmap" \
  --owner "Product/engineering" \
  --purpose "Convert the feature request into bounded agent implementation phases." \
  --prefix NF \
  --phase "Baseline Audit" \
  --phase "Core Model and API" \
  --phase "User Experience" \
  --phase "Release Gates"
```

The scaffold is a starter, not a finished harness. It creates runtime artifacts by default, including a continuity ledger that ties phases, feature-oracle items, code-summary writeback, and handoff boundaries together. Run the baseline phase to inspect code and write concrete facts back before implementation phases proceed.

## Validate

```bash
python3 scripts/validate_harness_prd.py docs/new_feature_harness --allow-placeholders
python3 scripts/validate_harness_prd.py docs/new_feature_harness --strict --quality-score
```

After actor and independent critic evidence exists, use completion gates before declaring a phase or full demand complete:

```bash
python3 scripts/validate_harness_prd.py docs/new_feature_harness --strict --completion-gate --phase NF-02 --quality-score
python3 scripts/validate_harness_prd.py docs/new_feature_harness --strict --completion-gate --quality-score
```

The validator checks structure, JSON machine contracts, runtime artifacts, loop cycle/state, feature-oracle evidence, continuity files, phase IDs, dependency order, report paths, critic artifacts, command objects, risk-triggered gates, placeholders, and vague language. `--strict` proves the harness is executable; `--completion-gate` is required before calling one phase or the full demand complete.

## Repository Layout

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── assets/
│   ├── README.template.md
│   ├── agent-handoff.template.md
│   ├── continuity-ledger.template.md
│   ├── critic-verdict.template.md
│   ├── next-window-prompt.template.md
│   ├── phase-manifest.template.md
│   ├── phase-report.template.md
│   ├── phase.template.md
│   ├── progress-log.template.md
│   └── source-packet.template.md
├── references/
│   ├── agent-adapters.md
│   ├── builder-protocol.md
│   ├── long-running-agent-protocol.md
│   ├── phase-contract-schema.md
│   ├── phase-folder-spec.md
│   ├── phase-runner-protocol.md
│   ├── research-notes.md
│   └── security-protocol.md
└── scripts/
    ├── scaffold_harness_prd.py
    └── validate_harness_prd.py
```

## Core Idea

Every phase should be a cold-start executable unit with:

- Machine Contract JSON
- loop contract and loop state
- feature oracle and progress log
- continuity ledger for cross-phase relatedness and code-summary writeback
- planner/generator/critic handoff
- independent critic verdict artifact
- copy-ready next-window prompt
- `GOAL_PROMPT`
- `READ_FIRST`
- `PRIMARY_CONTEXT`
- `LIKELY_EDIT_PATHS`
- `DO_NOT_EDIT`
- validation commands
- browser/runtime checks
- regression scope
- compliance gates
- rollback plan
- evidence output
- stop conditions

## License

No license is currently included. Add one before treating this as open-source reusable software.
