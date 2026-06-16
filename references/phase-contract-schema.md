# Phase Contract Schema

This is the semantic schema for the `Machine Contract` JSON block in each phase.

## Required Top-Level Fields

```text
schema_version: string, currently "prd-phase-harness/v3"
harness_role: "execution" | "evaluation" | "hybrid"
phase: object
goal: object
runtime: object
context: object
boundaries: object
tool_policy: object
risk: object
validation: object
evidence: object
stop_conditions: array
```

## `phase`

```text
id: stable phase ID, for example PO-05
number: two digit string
title: human-readable name
status: draft | ready | planned | in_progress | blocked | passed | waived
type: baseline | implementation | release | eval | repair
repo_path: repo-relative or absolute path
docs_path: path to harness folder
phase_file: path to this file
depends_on: array of PHASE_ID values
unlocks: array of PHASE_ID values
```

## `goal`

```text
target: one sentence target
prompt: runnable goal prompt
plan_required: boolean
plan_output: optional durable plan path
completion_report: required report path
```

`prompt` must include the phase ID and phase file path.

## `runtime`

```text
feature_oracle: path to feature-oracle.json
loop_contract: path to loop-contract.json
loop_state: path to loop-state.json
progress_log: path to progress-log.md
handoff: path to agent-handoff.md
next_window_prompt: path to next-window-prompt.md
session_boot: object with read_progress, run_baseline_check, update_progress_before_exit booleans
agent_roles: array containing planner, generator, evaluator when the harness supports independent review
```

The runtime files are the restart surface for fresh context windows. They should be concrete paths in final harnesses.

## `context`

```text
read_first: array of files to read before planning
primary_context: bounded files/routes/design artifacts
context_budget: focused | broad | exploratory
do_not_load_unless: contexts that require a blocker or explicit reason
```

## `boundaries`

```text
likely_edit_paths: paths/globs expected to change
do_not_edit: protected paths and non-goals
external_inputs: dashboards, credentials, Figma, providers, deploys, DNS, test accounts
secrets_required: secret names only, never values
```

## `tool_policy`

```text
allowed_tools: capabilities allowed or expected
approval_required: operations requiring user approval
dangerous_commands: command classes the agent must avoid or gate
```

## `risk`

```text
tags: array, e.g. ui, auth, payment, database, migration, ai, agent, eval, external-service, release
data_mutation: boolean | "unknown"
migration_required: boolean | "unknown"
browser_required: boolean | "unknown"
ai_eval_required: boolean | "unknown"
external_service_required: boolean | "unknown"
release_blocking: boolean | "unknown"
```

## `validation`

```text
commands: array of { id, cwd, command, expected, required }
browser_checks: array
regression_scope: array
compliance_gates: array
acceptance_gates: array
rollback_plan: array
```

Commands should be deterministic and scoped. Avoid `run tests` without a concrete command.

## `evidence`

```text
outputs: report, screenshot, log, trace, eval table, or audit paths
required_artifacts: artifact classes that must exist before completion
waiver_policy: how skipped gates are documented
next_phase_handoff: what unlocks or blocks dependent phases
```

## Risk-Triggered Requirements

| Risk Tag | Additional Required Fields |
| --- | --- |
| `ui`, `frontend`, `figma`, `browser` | `browser_checks` with route and viewport details. |
| `auth`, `security` | `compliance_gates` covering permissions, session, abuse, secret, and failure behavior. |
| `payment` | `compliance_gates` covering idempotency, test mode, webhooks, no-real-charge, and audit. |
| `database`, `schema`, `migration` | `rollback_plan` and migration/idempotency validation. |
| `ai`, `agent`, `llm`, `eval` | acceptance/eval gates with golden questions, trace capture, tool/source boundaries, privacy behavior, and evaluator handoff. |
| `external-service` | external input and approval gates plus mock/offline fallback. |
| `release` | build/smoke/deploy/rollback/monitoring evidence. |

## Vague Language Ban

Final harnesses should not use these as gates:

- as needed
- etc.
- relevant files
- related files
- run tests
- verify manually
- make sure it works
- improve UX
- make it robust
