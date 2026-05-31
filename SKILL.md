---
name: prd-phase-harness
description: Create agent-ready PRD phase folders from a full PRD, Figma UI, existing codebase, research notes, or rough oral product request. Use when Codex or Claude Code needs to decompose ambiguous product/engineering work into a docs folder with README, phase manifest, bounded phase markdown files, strong machine-readable metadata, requirements, tests, compliance/safety gates, plan-first execution instructions, evidence capture, and acceptance criteria for sequential agent implementation.
---

# PRD Phase Harness

## Overview

Use this skill to turn product intent into a harness-style execution folder. The output should let a coding agent open one phase file, understand exactly what to do, make a plan, execute within boundaries, run tests/regression checks, capture evidence, and then move to the next phase only when gates pass.

This skill is optimized for AI-readable markdown, not stakeholder prose. Prefer dense metadata, stable grep anchors, bounded edit paths, deterministic validation, and explicit stop conditions.

## Workflow

1. Classify the input:
   - Full PRD plus UI/design: extract product thesis, users, journeys, screens, data flows, technical constraints, and visual QA.
   - Existing codebase plus request: inspect current docs, routes, package scripts, tests, schema, and architecture before proposing phases.
   - Rough oral request: infer a compact product thesis, ask only for blocking details, then write assumptions explicitly.
2. Build a context packet:
   - Use `rg --files`, `rg -n`, package scripts, existing docs, and relevant design artifacts.
   - Reuse the repo's existing PRD/phase style when present.
   - For Figma URLs or provided UI, use available Figma/design tools or screenshots to extract screen inventory and verification needs.
3. Design the phase map:
   - Create one baseline/audit phase first unless the project already has a fresh baseline.
   - Split work into phases that a coding agent can finish independently in one focused run.
   - Order phases by dependency, risk, and feedback value.
   - Keep non-goals and future ideas out of executable phases unless they are required gates.
4. Create a folder under `docs/<kebab-topic>/` unless the user specifies another path.
5. Write:
   - `README.md`: roadmap, product thesis, loading protocol, phase order, shared rules, verification commands.
   - `phase-manifest.md`: compact machine index with grep hints, dependencies, validation matrix, and goal prompt templates.
   - `phase-XX-<slug>.md`: one bounded phase module per phase.
6. Before finishing, run a lint/readability pass:
   - Every phase has a complete `Coding Agent Contract`.
   - Every `GOAL_PROMPT` is directly executable.
   - Every phase has tests/regression checks and acceptance gates.
   - Dependencies are acyclic.
   - Edit boundaries and non-goals are explicit.

## Required Shape

Use the detailed spec in `references/phase-folder-spec.md` when creating or reviewing a folder. Load it when you need section templates, field definitions, validation checklists, or examples.

Each phase file must include these sections in this order unless adapting to an existing repo convention:

- Title
- Goal
- Architecture
- Tech Stack
- Coding Agent Contract
- Task Spec
- Problem Boundary
- Context Policy
- Product or Engineering Requirements
- Test and Regression Requirements
- Compliance and Safety Requirements
- Execution Capture
- Evaluator Protocol
- Acceptance Criteria
- Risks

The `Coding Agent Contract` is authoritative and must use grep-friendly anchors:

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

## Harness Rules

- Make phases observable: require command output summaries, reports, screenshots, traces, or tables where useful.
- Make phases debuggable: require failure attribution and blocker notes instead of silent skipping.
- Make phases bounded: name likely edit paths and do-not-edit paths.
- Make phases safe: include privacy, permissions, data mutation, migration, accessibility, security, and content-boundary gates when relevant.
- Make phases plan-first: each phase should require a written plan before edits and verification before completion.
- Make phases progressive: do not combine adjacent phases unless the user explicitly asks for a larger goal.
- Make phase docs durable: avoid prose that depends on chat context; write assumptions and decisions into the files.

## Scaffold Script

Use `scripts/scaffold_harness_prd.py` when a quick folder skeleton helps. It creates README, manifest, and phase files from a phase list, using templates under `assets/`.

Example:

```bash
python3 ~/.codex/skills/prd-phase-harness/scripts/scaffold_harness_prd.py \
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

After scaffolding, replace placeholders with project-specific content. Do not leave placeholder acceptance gates in final docs.

## Research Notes

Load `references/research-notes.md` only when you need the rationale behind the harness model or want to adapt this skill to a new domain. It summarizes local project patterns and external harness-engine research.

## Output Quality Bar

The finished folder should be usable by a fresh coding agent with minimal chat context. If a phase cannot be assigned as a standalone goal prompt with clear inputs, boundaries, tests, and completion evidence, tighten the phase before claiming the folder is ready.
