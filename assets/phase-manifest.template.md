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
