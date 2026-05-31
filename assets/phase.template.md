# Phase {{PHASE_NUMBER}} - {{PHASE_NAME}}

> For agentic workers: enter plan-first mode before editing. Create or update a plan, execute in bounded steps, run verification, and record blockers before moving on.

**Goal:** {{GOAL}}

**Architecture:** {{ARCHITECTURE}}

**Tech Stack:** {{TECH_STACK}}

---

## Coding Agent Contract

- PHASE_ID: {{PHASE_ID}}
- GOAL_TARGET: {{GOAL_TARGET}}
- GOAL_PROMPT: Complete {{PHASE_ID}} {{PHASE_NAME}} for `{{REPO_PATH}}` by following `{{PHASE_FILE}}`; {{GOAL_PROMPT_CONSTRAINTS}}; finish only after validation, regression, compliance, evidence, and acceptance gates pass or blockers are documented.
- DEPENDS_ON: {{DEPENDS_ON}}
- READ_FIRST: `{{DOCS_PATH}}/README.md`, `{{DOCS_PATH}}/phase-manifest.md`, this file
- PRIMARY_CONTEXT: {{PRIMARY_CONTEXT}}
- LIKELY_EDIT_PATHS: {{LIKELY_EDIT_PATHS}}
- DO_NOT_EDIT: {{DO_NOT_EDIT}}
- EXECUTION_MODE: plan-first; implement stepwise; verify before completion
- VALIDATION_COMMANDS: {{VALIDATION_COMMANDS}}
- BROWSER_CHECKS: {{BROWSER_CHECKS}}
- REGRESSION_SCOPE: {{REGRESSION_SCOPE}}
- COMPLIANCE_GATES: {{COMPLIANCE_GATES}}
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

## Product Requirements

### R1 {{R1_NAME}}

{{R1_BODY}}

## Test and Regression Requirements

{{TEST_AND_REGRESSION_REQUIREMENTS}}

## Compliance and Safety Requirements

{{COMPLIANCE_AND_SAFETY_REQUIREMENTS}}

## Execution Capture

{{EXECUTION_CAPTURE}}

## Evaluator Protocol

{{EVALUATOR_PROTOCOL}}

## Acceptance Criteria

{{ACCEPTANCE_CRITERIA}}

## Risks

{{RISKS}}
