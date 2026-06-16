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
3. Open `loop-contract.json`, `loop-state.json`, `feature-oracle.json`, `progress-log.md`, `agent-handoff.md`, and `next-window-prompt.md`.
4. Locate the target with:

```bash
rg -n "PHASE_ID: <ID>|GOAL_PROMPT|VALIDATION_COMMANDS|ACCEPTANCE_GATES" {{DOCS_PATH}}
```

5. Open only the target phase file and files listed in that phase's `PRIMARY_CONTEXT`.
6. Create a plan before editing.
7. Treat `LIKELY_EDIT_PATHS` as the intended write boundary.
8. Complete validation, browser/runtime checks, regression scope, compliance gates, rollback notes, evidence output, and acceptance gates before claiming completion.
9. Update `progress-log.md`, `agent-handoff.md`, the phase report, and only the relevant feature `status`/`evidence` fields in `feature-oracle.json`.
10. Move to the next phase only after dependency gates are met or explicitly waived in a report.

## Long-Running Runtime Protocol

Each fresh session must start from durable files instead of hidden chat context:

- Read `{{PROGRESS_LOG_PATH}}` and recent git history before choosing work.
- Follow `{{LOOP_CONTRACT_PATH}}`: observe, select, execute, verify, record, then decide whether to continue or stop.
- Update `{{LOOP_STATE_PATH}}` when the active phase, feature, iteration, decision, or blocker changes.
- Run the baseline or smoke check named by the target phase before adding new changes.
- Work on one phase and one feature-oracle item at a time.
- Mark oracle items `passing` only when evidence points to a command, report, screenshot, trace, or log.
- Leave the repo in a clean, restartable state or document the blocker in the phase report.

## Runtime Artifacts

| Artifact | Purpose |
| --- | --- |
| `{{LOOP_CONTRACT_PATH}}` | The control loop: observe, select, execute, verify, record, decide. |
| `{{LOOP_STATE_PATH}}` | Current phase, feature, iteration, status, last decision, and next action. |
| `{{FEATURE_ORACLE_PATH}}` | End-to-end feature/test oracle. Agents may update status and evidence, not delete cases. |
| `{{PROGRESS_LOG_PATH}}` | Chronological progress, current blocker, and clean-state notes for the next session. |
| `{{AGENT_HANDOFF_PATH}}` | File-based planner/generator/evaluator handoff packet. |
| `{{NEXT_WINDOW_PROMPT_PATH}}` | Copy-ready prompt for starting the next agent window. |

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

## New Window Prompt

Use `{{NEXT_WINDOW_PROMPT_PATH}}` when starting a new Codex, Claude Code, or compatible agent window. Prefer the exact target phase `GOAL_PROMPT` from the phase file when assigning implementation work.

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
