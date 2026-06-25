# Phase Folder Spec

Use this reference when writing or reviewing an agent-executable PRD phase folder.

## Contents

- [Design Principle](#design-principle)
- [Folder Layout](#folder-layout)
- [README.md Contract](#readmemd-contract)
- [phase-manifest.md Contract](#phase-manifestmd-contract)
- [Phase File Contract](#phase-file-contract)
- [Status Model](#status-model)
- [Phase Sizing](#phase-sizing)
- [Requirement Rules](#requirement-rules)
- [Verification Rules](#verification-rules)
- [Minimal Change and Review Rules](#minimal-change-and-review-rules)
- [Terminal Regression Rules](#terminal-regression-rules)
- [Compliance and Safety Rules](#compliance-and-safety-rules)
- [Evidence Rules](#evidence-rules)
- [Review Checklist](#review-checklist)

## Design Principle

A phase folder is a runtime harness for coding agents. It should answer:

1. What is the product or engineering intent?
2. What evidence supports the phase map?
3. Which phase should be executed now?
4. What files should the agent read first?
5. What files may the agent likely edit?
6. What must the agent avoid?
7. How does the agent prove completion?
8. What artifact survives after the chat ends?

## Folder Layout

```text
docs/<topic>/
├── README.md
├── source-packet.md
├── loop-contract.json
├── loop-state.json
├── feature-oracle.json
├── progress-log.md
├── agent-handoff.md
├── continuity-ledger.md
├── next-window-prompt.md
├── phase-manifest.md
├── phase-00-<baseline-slug>.md
├── phase-01-<slug>.md
├── phase-02-<slug>.md
└── reports/
    └── phase-report-template.md
```

Create concrete phase reports during execution, not during planning. The report template should exist so every worker uses the same evidence shape.

## README.md Contract

The README is the folder-level operating manual. It should be readable by humans and machines.

Required sections:

- Harness Intent
- Coding Agent Loading Protocol
- Long-Running Runtime Protocol
- Source Packet
- Runtime Artifacts
- Current System Shape
- Assumptions and Decisions
- Phase Order
- Roadmap Cohesion
- Shared Harness Rules
- Global Non-Goals
- Global Compliance Gates
- Standard Verification Commands
- Required Browser or Runtime Checks
- External Inputs and Approvals
- New Window Prompt

The loading protocol must tell an agent to:

1. Open README.
2. Open manifest.
3. Open loop contract, loop state, feature oracle, progress log, handoff, continuity ledger, and next-window prompt.
4. Locate the target phase by `PHASE_ID`.
5. Open only the target phase and `PRIMARY_CONTEXT`.
6. Plan before editing.
7. Stay inside `LIKELY_EDIT_PATHS`.
8. Verify and write evidence before completion.
9. Update progress, handoff, report, oracle evidence, source packet code facts, and continuity ledger before exit.
10. Advance only after dependencies pass or are explicitly waived.

## phase-manifest.md Contract

The manifest is the compact machine index. Prefer tables and grep anchors over prose.

Required sections:

- Grep Usage
- Phase Index
- Phase Report Index
- Dependency Flow
- Validation Matrix
- Risk Matrix
- Runtime Artifacts
- Agent Role Handoffs
- Goal Setup Templates
- Shared Agent Rules
- External Inputs Checklist

The phase index must include:

- `PHASE_ID`
- File
- Depends On
- Goal Target
- Main Validation
- Evidence Output

The validation matrix must include:

- Mutates Data
- Needs Browser/UI
- Needs Agent/LLM Eval
- Needs Migration
- Needs External Service
- Release Blocking

## Phase File Contract

Every phase file should be assignable as one standalone goal. Use this section order:

```markdown
# Phase XX - <Name>

> For agentic workers: enter plan-first mode before editing...

**Goal:** <one clear outcome>

**Architecture:** <how the phase fits the existing system>

**Tech Stack:** <specific frameworks, files, services, tools>

---

## Machine Contract

```json
{
  "schema_version": "prd-phase-harness/v3",
  "harness_role": "execution",
  "phase": {
    "id": "<PREFIX-XX>",
    "number": "XX",
    "title": "<Name>",
    "status": "ready",
    "type": "baseline|implementation|release|eval",
    "repo_path": ".",
    "docs_path": "docs/<topic>",
    "phase_file": "docs/<topic>/phase-XX-<slug>.md",
    "depends_on": [],
    "unlocks": []
  },
  "goal": {
    "target": "<single sentence target>",
    "prompt": "Complete <PREFIX-XX>...",
    "plan_required": true,
    "plan_output": "docs/<topic>/reports/<phase-id>-plan.md",
    "completion_report": "docs/<topic>/reports/<phase-id>-report.md"
  },
  "runtime": {
    "feature_oracle": "docs/<topic>/feature-oracle.json",
    "loop_contract": "docs/<topic>/loop-contract.json",
    "loop_state": "docs/<topic>/loop-state.json",
    "progress_log": "docs/<topic>/progress-log.md",
    "handoff": "docs/<topic>/agent-handoff.md",
    "continuity_ledger": "docs/<topic>/continuity-ledger.md",
    "next_window_prompt": "docs/<topic>/next-window-prompt.md",
    "session_boot": {
      "read_progress": true,
      "run_baseline_check": true,
      "update_progress_before_exit": true
    },
    "agent_roles": ["planner", "generator", "critic"]
  },
  "context": {
    "read_first": [],
    "primary_context": [],
    "context_budget": "focused",
    "do_not_load_unless": []
  },
  "boundaries": {
    "likely_edit_paths": [],
    "do_not_edit": [],
    "external_inputs": [],
    "secrets_required": []
  },
  "tool_policy": {
    "allowed_tools": [],
    "approval_required": [],
    "dangerous_commands": []
  },
  "risk": {
    "tags": [],
    "data_mutation": false,
    "migration_required": false,
    "browser_required": false,
    "ai_eval_required": false,
    "external_service_required": false,
    "release_blocking": false
  },
  "validation": {
    "commands": [],
    "browser_checks": [],
    "regression_scope": [],
    "compliance_gates": [],
    "acceptance_gates": [],
    "rollback_plan": []
  },
  "evidence": {
    "outputs": [],
    "required_artifacts": [],
    "waiver_policy": "",
    "next_phase_handoff": ""
  },
  "stop_conditions": []
}
```

## Coding Agent Contract

- PHASE_ID: <PREFIX-XX>
- GOAL_TARGET: <single sentence target>
- GOAL_PROMPT: Complete <PREFIX-XX> <Name> for `<repo>` by following `docs/<topic>/phase-XX-<slug>.md`; <constraints>; stay inside the named edit boundaries; finish only after validation, regression, compliance, rollback, evidence, and acceptance gates pass or blockers are documented.
- DEPENDS_ON: <none or IDs>
- READ_FIRST: `docs/<topic>/README.md`, `docs/<topic>/phase-manifest.md`, this file
- PRIMARY_CONTEXT: <files, routes, schemas, APIs, design artifacts>
- LIKELY_EDIT_PATHS: <bounded paths>
- DO_NOT_EDIT: <protected files, non-goals, external systems>
- EXECUTION_MODE: plan-first; implement stepwise; verify before completion; write evidence before handoff
- VALIDATION_COMMANDS: <commands>
- BROWSER_CHECKS: <routes and viewports, or none>
- REGRESSION_SCOPE: <existing behavior that must still work>
- COMPLIANCE_GATES: <privacy, security, a11y, permissions, data retention, brand, content boundaries>
- ROLLBACK_PLAN: <migration reversal, feature flag, revert path, or none>
- ACCEPTANCE_GATES: <deterministic gates>
- EVIDENCE_OUTPUT: `docs/<topic>/reports/<phase-id>-<slug>-report.md`
- STOP_CONDITIONS: <when to stop and document instead of guessing>

## Task Spec

## Problem Boundary

## Context Policy

## Requirements

### R1 <Requirement Name>

## Test and Regression Requirements

## Compliance and Safety Requirements

## Rollback and Recovery

## Execution Capture

## Evaluator Protocol

## Acceptance Criteria

## Risks
```

The JSON contract is authoritative. The Markdown contract mirrors the most important fields for grep and human scanning.

## Status Model

Use these status values in the machine contract and reports:

- `draft`: scaffold exists but still contains placeholders or unresolved assumptions.
- `ready`: phase is executable by a fresh agent.
- `planned`: phase runner has produced a plan but not completed implementation.
- `in_progress`: implementation has started.
- `blocked`: phase cannot complete; report names blocker and remaining evidence.
- `passed`: all required gates passed and evidence exists.
- `waived`: user explicitly waived a gate; report names who/what/why.

Do not unlock dependent phases from `draft`, `planned`, `in_progress`, or `blocked` unless the user explicitly waives the dependency in a report.

## Phase Sizing

A good phase has:

- One coherent product or engineering outcome.
- One dominant risk profile.
- A small named context set.
- Concrete edit boundaries.
- Verification that can run in the repo or a clear blocker path.
- Durable evidence output.

Split a phase when:

- Backend, schema, UI, migration, eval, or release work need different validation.
- It would require broad edits outside a narrow boundary.
- It depends on real feedback from an earlier phase.
- It mixes exploratory baseline work with implementation.

Merge phases when:

- One phase cannot create value or evidence without the other.
- The second phase is only mandatory cleanup of the first.

## Requirement Rules

Write requirements as observable behavior:

- Good: "When owner publishes a draft, status becomes `published`, visibility becomes `public`, and `publishedAt` is set if missing."
- Good: "Mobile viewport `390x844` has no horizontal overflow and focus remains visible."
- Bad: "Improve UX."
- Bad: "Make it robust."
- Bad: "Add AI magic."

Use stable requirement IDs (`R1`, `R2`) and connect them to tests or acceptance gates where possible.

## Verification Rules

Every phase should name the smallest credible verification set:

- Static checks, type checks, lint.
- Unit/integration/API tests.
- Browser checks for UI.
- Migration dry-runs or rollback checks for schema work.
- Golden questions, eval tables, traces, or refusal checks for AI behavior.
- Build checks for release-sensitive work.

If a command cannot run locally, the phase must require a blocker note explaining why and what evidence was still collected.

## Minimal Change and Review Rules

Every phase should name the smallest expected edit boundary and require independent critic evidence before `passed`.

The phase report should record:

- Files changed and why those files were the smallest sufficient change.
- Any scope expansion and the reason it was required.
- Independent critic findings tied to requirements, tests, and regression impact.

## Terminal Regression Rules

The terminal phase or release gate must run whole-demand regression across completed feature-oracle items before the overall requirement is marked complete.

If whole-demand regression cannot run, the terminal report must name:

- The blocked command, browser path, eval, or runtime dependency.
- Evidence already collected.
- Residual risk.
- Whether dependent release or handoff may proceed.

## Compliance and Safety Rules

Include compliance gates even for small features. Consider:

- Privacy and PII.
- Auth and permissions.
- Hidden/admin/draft content boundaries.
- Data retention and deletion.
- External API keys and secrets.
- Accessibility.
- Security and rate limiting.
- Copyright and licensing.
- Brand/design constraints.
- Migration and rollback safety.

## Evidence Rules

Evidence must survive chat context. Prefer:

- Markdown phase reports.
- Command summaries.
- Browser screenshots.
- Console/network error summaries.
- JSON audit output.
- Golden-question tables.
- Migration notes.
- Known blockers and user waivers.

## Review Checklist

Before finalizing a folder:

- README explains how an agent should load the folder.
- Manifest indexes every phase, dependency, report, risk, and validation class.
- Dependencies are acyclic.
- Every phase has the full `Coding Agent Contract`.
- Every phase has concrete context, edit paths, protected paths, validation, regression, compliance, rollback, acceptance, evidence, and stop conditions.
- Baseline/audit exists or is explicitly waived.
- Non-goals prevent scope creep.
- No phase depends on unstated chat context.
- No unresolved placeholder remains unless the user requested a scaffold.
