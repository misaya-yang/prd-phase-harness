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
| Loop Contract | `{{LOOP_CONTRACT_PATH}}` | Follow observe, select, execute, verify, record, decide before claiming progress. |
| Loop State | `{{LOOP_STATE_PATH}}` | Keep active phase, feature, iteration, status, and next action current. |
| Feature Oracle | `{{FEATURE_ORACLE_PATH}}` | Update only status, evidence, and notes for the feature being worked. |
| Progress Log | `{{PROGRESS_LOG_PATH}}` | Append session start/end, validation, and blocker notes. |
| Agent Handoff | `{{AGENT_HANDOFF_PATH}}` | Keep planner, generator, and evaluator notes file-based and brief. |
| Continuity Ledger | `{{CONTINUITY_LEDGER_PATH}}` | Preserve phase relatedness, code-summary writeback, and interface boundary decisions. |
| Next Window Prompt | `{{NEXT_WINDOW_PROMPT_PATH}}` | Use this to restart work in a fresh context window. |

## Agent Role Handoffs

- Planner role: expand intent into phase contracts and feature-oracle cases without over-specifying implementation details.
- Generator role: execute one phase/feature item, update evidence, and hand off to evaluation.
- Evaluator role: review from files and runtime checks, reject superficial completion, and write actionable findings.
- For small low-risk phases, one agent may play generator and evaluator only after running objective validation commands.

## Delivery Quality Gates

- Each phase is independently executable and verifiable.
- Each phase records inherited evidence, dependency status, and what it unlocks next.
- Each phase uses the smallest requirement-satisfying change; scope expansion must be justified in the report.
- Each phase records test evidence and review evidence, or a blocker.
- The terminal phase or release gate runs whole-demand regression across completed feature-oracle items.
- Runtime files must be sufficient for a fresh agent to resume after context compaction.

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
