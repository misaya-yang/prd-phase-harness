# Phase {{PHASE_NUMBER}} - {{PHASE_NAME}}

> For agentic workers: enter plan-first mode before editing. Execute this phase only, make the smallest requirement-satisfying change, write the required evidence, and do not advance to the next phase until acceptance gates pass or blockers are documented.

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
- GOAL_PROMPT: Complete {{PHASE_ID}} {{PHASE_NAME}} for `{{REPO_PATH}}` by following `{{PHASE_FILE}}`; {{GOAL_PROMPT_CONSTRAINTS}}; stay inside the named edit boundaries; make the smallest requirement-satisfying change; finish only after validation, regression, review, compliance, rollback, evidence, acceptance gates, and `--completion-gate --phase {{PHASE_ID}}` pass or blockers are documented.
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

## Harness Runtime

- FEATURE_ORACLE: `{{FEATURE_ORACLE_PATH}}`
- LOOP_CONTRACT: `{{LOOP_CONTRACT_PATH}}`
- LOOP_STATE: `{{LOOP_STATE_PATH}}`
- PROGRESS_LOG: `{{PROGRESS_LOG_PATH}}`
- AGENT_HANDOFF: `{{AGENT_HANDOFF_PATH}}`
- NEXT_WINDOW_PROMPT: `{{NEXT_WINDOW_PROMPT_PATH}}`
- CONTINUITY_LEDGER: `{{CONTINUITY_LEDGER_PATH}}`

Session boot:

1. Read the runtime artifacts above.
2. Follow the loop contract: observe, select, execute, verify, record, decide.
3. Run the target phase's baseline or smoke validation before implementation when available.
4. Select one matching feature-oracle item and keep work scoped to that item and this phase.
5. Summarize inspected code facts and interface decisions back into the source packet and continuity ledger.
6. Record minimal-change scope and test evidence.
7. Update loop state, progress, continuity, and handoff files before exiting.
8. Hand off to an independent critic/subagent for completion review.
9. Run `--strict --completion-gate --phase {{PHASE_ID}}` before claiming this phase is passed or unlocked.

## Feature Oracle Policy

The feature oracle is the durable test list for long-running agents. Do not delete oracle cases to make completion easier. Update only `status`, `evidence`, and `notes` unless the user explicitly changes scope.

Status rules:

- `failing`: not implemented or not verified.
- `passing`: end-to-end actor evidence exists, cites a phase report with `Status: passed`, and cites an independent critic artifact with `Critic Verdict: approved`.
- `blocked`: a named dependency, credential, environment, or scope issue prevents completion.
- `waived`: the user explicitly waived the case and remaining risk is documented.

## Task Spec

{{TASK_SPEC}}

## Cross-Phase Continuity

- Depends on: {{DEPENDS_ON}}
- Unlocks: {{UNLOCKS}}
- Feature-oracle item: {{FEATURE_ID}}
- Continuity ledger: `{{CONTINUITY_LEDGER_PATH}}`
- Prior-phase evidence to inherit: {{PRIOR_PHASE_EVIDENCE}}
- Boundary this phase must preserve for later phases: {{BOUNDARY_TO_PRESERVE}}
- Handoff this phase must produce: {{PHASE_HANDOFF_OUTPUT}}

## Code Summary Writeback

Before claiming completion, inspect the code paths allowed by this phase and write back:

- `source-packet.md`: summarize discovered files, services, routes, schemas, tests, commands, and runtime constraints.
- `continuity-ledger.md`: record interface boundaries, dependency assumptions, changed contracts, and any downstream phase impact.
- `agent-handoff.md`: state the next concrete action, active feature-oracle item, validation evidence, and blocker status.
- Phase report: link validation output, independent critic evidence, minimal-change scope notes, the exact code-summary update, and completion-gate result.

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
