# Phase {{PHASE_NUMBER}} - {{PHASE_NAME}}

> For agentic workers: enter plan-first mode before editing. Execute this phase only, write the required evidence, and do not advance to the next phase until acceptance gates pass or blockers are documented.

**Goal:** {{GOAL}}

**Architecture:** {{ARCHITECTURE}}

**Tech Stack:** {{TECH_STACK}}

---

## Machine Contract

The JSON block below is the authoritative machine-readable contract for goal-mode agents and validators. Keep it synchronized with the human-readable sections.

```json
{{PHASE_CONTRACT_JSON}}
```

## Coding Agent Contract

- PHASE_ID: {{PHASE_ID}}
- GOAL_TARGET: {{GOAL_TARGET}}
- GOAL_PROMPT: Complete {{PHASE_ID}} {{PHASE_NAME}} for `{{REPO_PATH}}` by following `{{PHASE_FILE}}`; {{GOAL_PROMPT_CONSTRAINTS}}; stay inside the named edit boundaries; finish only after validation, regression, compliance, rollback, evidence, and acceptance gates pass or blockers are documented.
- DEPENDS_ON: {{DEPENDS_ON}}
- READ_FIRST: `{{DOCS_PATH}}/README.md`, `{{DOCS_PATH}}/phase-manifest.md`, this file
- PRIMARY_CONTEXT: {{PRIMARY_CONTEXT}}
- LIKELY_EDIT_PATHS: {{LIKELY_EDIT_PATHS}}
- DO_NOT_EDIT: {{DO_NOT_EDIT}}
- EXECUTION_MODE: plan-first; implement stepwise; verify before completion; write evidence before handoff
- VALIDATION_COMMANDS: {{VALIDATION_COMMANDS}}
- BROWSER_CHECKS: {{BROWSER_CHECKS}}
- REGRESSION_SCOPE: {{REGRESSION_SCOPE}}
- COMPLIANCE_GATES: {{COMPLIANCE_GATES}}
- ROLLBACK_PLAN: {{ROLLBACK_PLAN}}
- ACCEPTANCE_GATES: {{ACCEPTANCE_GATES}}
- EVIDENCE_OUTPUT: {{EVIDENCE_OUTPUT}}
- STOP_CONDITIONS: {{STOP_CONDITIONS}}

## Task Spec

{{TASK_SPEC}}

## Problem Boundary

In scope:

{{IN_SCOPE}}

Out of scope:

{{OUT_OF_SCOPE}}

## Context Policy

Before editing, inspect:

{{CONTEXT_POLICY}}

Do not load unrelated files unless a blocker requires expanding context.

## Requirements

### R1 {{R1_NAME}}

{{R1_BODY}}

## Test and Regression Requirements

{{TEST_AND_REGRESSION_REQUIREMENTS}}

## Compliance and Safety Requirements

{{COMPLIANCE_AND_SAFETY_REQUIREMENTS}}

## Rollback and Recovery

{{ROLLBACK_AND_RECOVERY}}

## Execution Capture

{{EXECUTION_CAPTURE}}

Use `{{REPORT_TEMPLATE}}` when writing the phase report.

## Evaluator Protocol

{{EVALUATOR_PROTOCOL}}

## Acceptance Criteria

{{ACCEPTANCE_CRITERIA}}

## Risks

{{RISKS}}
