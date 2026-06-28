# {{TITLE}}

**Date:** {{DATE}}

**Owner:** {{OWNER}}

**Purpose:** {{PURPOSE}}

---

## Harness Intent

{{PRODUCT_THESIS}}

## Coding Agent Loading Protocol

When assigned a phase goal:

1. Open `{{CONTEXT_PROFILE_PATH}}`.
2. Open `{{LOOP_STATE_PATH}}`.
3. Open the assigned target phase file. If the target is unknown, locate it with:

```bash
rg -n "PHASE_ID: <ID>" {{DOCS_PATH}}
```

4. Open only the target phase file and hot-path items allowed by `context-profile.json`. The goal prompt, edit boundaries, validation, and gates all live in that phase's single `## Machine Contract` JSON block.
5. Do not load the full docs folder, full `source-packet.md`, full `feature-oracle.json`, or prior reports unless the context profile trigger says to.
6. Create a plan before editing.
7. Treat the contract's `boundaries.likely_edit_paths` as the intended write boundary.
8. Complete validation, browser/runtime checks, regression scope, review, compliance gates, rollback notes, evidence output, and acceptance gates before claiming completion.
9. Summarize code facts and boundary decisions back into `source-packet.md` and `continuity-ledger.md` using targeted sections only.
10. Update `progress-log.md`, `agent-handoff.md`, the phase report, and only the relevant feature `status`/`evidence` fields in `feature-oracle.json`.
11. Run `--strict --completion-gate --phase <PHASE_ID>` before declaring a phase complete or unlocked.
12. Move to the next phase only after dependency gates are met or explicitly waived in a report.

## Long-Running Runtime Protocol

Each fresh session must start from the smallest durable context packet instead of hidden chat context or pre-compaction memory:

- Read `{{CONTEXT_PROFILE_PATH}}` first and follow its role-specific load budget.
- Read recent `{{PROGRESS_LOG_PATH}}` entries only when the active blocker or status is unclear.
- Follow `{{LOOP_CONTRACT_PATH}}`: observe, select, execute, verify, record, then decide whether to continue or stop.
- Update `{{LOOP_STATE_PATH}}` when the active phase, feature, iteration, decision, or blocker changes.
- Update `{{CONTINUITY_LEDGER_PATH}}` when code facts, interfaces, contracts, or handoff boundaries change.
- Run the baseline or smoke check named by the target phase before adding new changes.
- Work on one phase and one feature-oracle item at a time.
- Make the smallest requirement-satisfying change and record any scope expansion in the phase report.
- Mark oracle items `passing` only when evidence points to an actor report with `Status: passed` and an independent critic artifact with `Critic Verdict: approved` or `waived`.
- Leave the repo in a clean, restartable state or document the blocker in the phase report.

## Runtime Artifacts

| Artifact | Purpose |
| --- | --- |
| `{{CONTEXT_PROFILE_PATH}}` | Progressive disclosure budget, hot-path files, role load profiles, and deferred triggers. |
| `{{LOOP_CONTRACT_PATH}}` | The control loop: observe, select, execute, verify, record, decide. |
| `{{LOOP_STATE_PATH}}` | Current phase, feature, iteration, status, last decision, and next action. |
| `{{FEATURE_ORACLE_PATH}}` | End-to-end feature/test oracle. Agents may update status and evidence, not delete cases. |
| `{{PROGRESS_LOG_PATH}}` | Chronological progress, current blocker, and clean-state notes for the next session. |
| `{{AGENT_HANDOFF_PATH}}` | File-based planner/generator/critic handoff packet. |
| `{{CONTINUITY_LEDGER_PATH}}` | Cross-phase continuity, code summary writeback, and interface boundary ledger. |
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

## Delivery Quality Gates

- Every phase must be executable and verifiable on its own.
- Every phase must inherit prior evidence and record what it unlocks next.
- Every implementation must include test evidence and independent critic evidence or an explicit blocker.
- The terminal phase or release gate must run whole-demand regression across completed feature-oracle items.
- Runtime files must be current enough for a fresh agent to resume after context compaction.
- `--strict` is structure readiness, not completion proof; phase or full-demand completion requires `--completion-gate`.

## New Window Prompt

Use `{{NEXT_WINDOW_PROMPT_PATH}}` when starting a new Codex, Claude Code, or compatible agent window. Prefer the exact `goal.prompt` from the target phase's `## Machine Contract` JSON when assigning implementation work.

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
