# {{TOPIC}} Phase Manifest

This is the compact index for coding agents. Prefer this file plus the target phase file over loading the whole folder.

## Grep Usage

Find a phase:

```bash
rg -n "PHASE_ID: {{PREFIX}}-XX" {{DOCS_PATH}}
```

Find all goal prompts:

```bash
rg -n "GOAL_PROMPT:" {{DOCS_PATH}}
```

Find validation commands:

```bash
rg -n "VALIDATION_COMMANDS:" {{DOCS_PATH}}
```

Find acceptance gates:

```bash
rg -n "ACCEPTANCE_GATES:" {{DOCS_PATH}}
```

Validate a completion claim:

```bash
python3 <skill-dir>/scripts/validate_harness_prd.py {{DOCS_PATH}} --strict --completion-gate --phase <PHASE_ID> --quality-score
```

## Phase Index

| PHASE_ID | File | Depends On | Goal Target | Main Validation | Evidence Output |
| --- | --- | --- | --- | --- | --- |
{{PHASE_INDEX_ROWS}}

## Phase Report Index

| PHASE_ID | Required Report |
| --- | --- |
{{PHASE_REPORT_ROWS}}

## Dependency Flow

```text
{{DEPENDENCY_FLOW}}
```

## Validation Matrix

| PHASE_ID | Mutates Data | Needs Browser/UI | Needs Agent/LLM Eval | Needs Migration | Needs External Service | Release Blocking |
| --- | --- | --- | --- | --- | --- | --- |
{{VALIDATION_MATRIX_ROWS}}

## Risk Matrix

| PHASE_ID | Primary Risk | Stop Condition |
| --- | --- | --- |
{{RISK_MATRIX_ROWS}}

## Runtime Artifacts

| Artifact | Path | Agent Rule |
| --- | --- | --- |
| Context Profile | `{{CONTEXT_PROFILE_PATH}}` | Load first; it defines hot path, role budgets, and deferred triggers. |
| Loop State | `{{LOOP_STATE_PATH}}` | Load first; keep active phase, feature, iteration, status, and next action current. |
| Loop Contract | `{{LOOP_CONTRACT_PATH}}` | Deferred; open only when loop semantics are unclear. |
| Feature Oracle | `{{FEATURE_ORACLE_PATH}}` | Deferred; inspect only the selected feature item unless repairing oracle coverage. |
| Progress Log | `{{PROGRESS_LOG_PATH}}` | Deferred; inspect recent entries only when blocker or status history is unclear. |
| Agent Handoff | `{{AGENT_HANDOFF_PATH}}` | Deferred; open only when next action or role handoff is unclear. |
| Continuity Ledger | `{{CONTINUITY_LEDGER_PATH}}` | Deferred; open only dependency rows needed for target phase or writeback. |
| Next Window Prompt | `{{NEXT_WINDOW_PROMPT_PATH}}` | Deferred; open only when preparing a fresh context window. |

## Agent Role Handoffs

- Planner role: expand intent into phase contracts and feature-oracle cases without over-specifying implementation details.
- Generator role: execute one phase/feature item, update evidence, and hand off to evaluation.
- Critic role: run in an independent subagent or fresh context, review actor output from files and runtime checks, reject superficial completion, and write actionable findings.
- No phase or PRD completion claim is valid until independent critic evidence is recorded.

## Delivery Quality Gates

- Each phase is independently executable and verifiable.
- Each phase records inherited evidence, dependency status, and what it unlocks next.
- Each phase uses the smallest requirement-satisfying change; scope expansion must be justified in the report.
- Each phase records test evidence and independent critic evidence, or a blocker.
- The terminal phase or release gate runs whole-demand regression across completed feature-oracle items.
- Runtime files must be sufficient for a fresh agent to resume after context compaction.
- Cold start must use `context-profile.json`; do not load the full docs folder or every runtime file by default.
- `--strict` is structure readiness only; phase and full-demand completion require `--completion-gate`.

## Goal Setup Templates

Use the exact phase file `GOAL_PROMPT` when creating an agent goal. If a phase has dependencies, do not execute it until dependency acceptance gates are met or explicitly waived in the previous phase report.

Example:

```text
{{GOAL_PROMPT_EXAMPLE}}
```

## Shared Agent Rules

{{SHARED_AGENT_RULES}}

## External Inputs Checklist

{{EXTERNAL_INPUTS_CHECKLIST}}
