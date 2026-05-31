# {{TITLE}}

**Date:** {{DATE}}

**Owner:** {{OWNER}}

**Purpose:** {{PURPOSE}}

---

## Coding Agent Loading Protocol

When assigned a phase goal:

1. Open this `README.md`.
2. Open `phase-manifest.md`.
3. Locate the target with:

```bash
rg -n "PHASE_ID: <ID>|GOAL_PROMPT|VALIDATION_COMMANDS|ACCEPTANCE_GATES" {{DOCS_PATH}}
```

4. Open only the target phase file and the files listed in that phase's `PRIMARY_CONTEXT`.
5. Set the execution goal from the phase's `GOAL_PROMPT`.
6. Treat `LIKELY_EDIT_PATHS` as the intended write boundary.
7. Complete `VALIDATION_COMMANDS`, `BROWSER_CHECKS`, `REGRESSION_SCOPE`, `COMPLIANCE_GATES`, and `ACCEPTANCE_GATES` before claiming completion.

## Product Thesis

{{PRODUCT_THESIS}}

## Input Sources and Assumptions

{{INPUT_SOURCES}}

## Current Product or System Shape

{{CURRENT_SHAPE}}

## Phase Order

| Phase | Name | Core Outcome |
| --- | --- | --- |
{{PHASE_ORDER_ROWS}}

## Roadmap Cohesion

{{ROADMAP_COHESION}}

## Shared Harness Contract

Each phase is a bounded harness module. It defines task spec, problem boundary, context policy, requirements, test/regression gates, compliance/safety gates, execution capture, evaluator protocol, acceptance criteria, and risks.

## Global Non-Goals

{{GLOBAL_NON_GOALS}}

## Standard Verification Commands

{{STANDARD_VERIFICATION_COMMANDS}}

## Required Browser or Runtime Checks

{{REQUIRED_BROWSER_CHECKS}}
