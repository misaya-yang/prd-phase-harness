# {{TITLE}}

**Date:** {{DATE}}

**Owner:** {{OWNER}}

**Purpose:** {{PURPOSE}}

---

## Harness Intent

{{PRODUCT_THESIS}}

## Coding Agent Loading Protocol

When assigned a phase goal:

1. Open this `README.md`.
2. Open `phase-manifest.md`.
3. Locate the target with:

```bash
rg -n "PHASE_ID: <ID>|GOAL_PROMPT|VALIDATION_COMMANDS|ACCEPTANCE_GATES" {{DOCS_PATH}}
```

4. Open only the target phase file and files listed in that phase's `PRIMARY_CONTEXT`.
5. Create a plan before editing.
6. Treat `LIKELY_EDIT_PATHS` as the intended write boundary.
7. Complete validation, browser/runtime checks, regression scope, compliance gates, rollback notes, evidence output, and acceptance gates before claiming completion.
8. Move to the next phase only after dependency gates are met or explicitly waived in a report.

## Source Packet

{{INPUT_SOURCES}}

## Current System Shape

{{CURRENT_SHAPE}}

## Assumptions and Decisions

{{ASSUMPTIONS_AND_DECISIONS}}

## Phase Order

| Phase | Name | Core Outcome | Report |
| --- | --- | --- | --- |
{{PHASE_ORDER_ROWS}}

## Roadmap Cohesion

{{ROADMAP_COHESION}}

## Shared Harness Rules

{{SHARED_HARNESS_RULES}}

## Global Non-Goals

{{GLOBAL_NON_GOALS}}

## Global Compliance Gates

{{GLOBAL_COMPLIANCE_GATES}}

## Standard Verification Commands

{{STANDARD_VERIFICATION_COMMANDS}}

## Required Browser or Runtime Checks

{{REQUIRED_BROWSER_CHECKS}}

## External Inputs and Approvals

{{EXTERNAL_INPUTS_AND_APPROVALS}}
