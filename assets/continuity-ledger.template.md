# {{TITLE}} Continuity Ledger

**Created:** {{DATE}}

**Harness Folder:** `{{DOCS_PATH}}`

---

## Purpose

This file preserves cross-phase continuity for long-running agents. Treat it as the bridge between product intent, code facts, execution evidence, and the next agent's starting point.

## Phase Continuity Chain

| Phase | Feature | Depends On | Unlocks | Handoff Boundary | Required Writeback |
| --- | --- | --- | --- | --- | --- |
{{CONTINUITY_ROWS}}

## Interface Boundary Ledger

| Boundary | Current Fact | Source | Last Verified | Owner Phase |
| --- | --- | --- | --- | --- |
| Code entrypoints | Not inspected yet; baseline phase must record concrete files, routes, services, schemas, and tests before implementation. | `source-packet.md` | scaffold-created | {{FIRST_PHASE_ID}} |
| Edit boundary | Use only phase `LIKELY_EDIT_PATHS`; if paths are unresolved, inspect code and write back the resolved boundary before editing. | phase contract | scaffold-created | {{FIRST_PHASE_ID}} |
| Validation boundary | Use phase validation commands; if commands are absent in the repo, record the attempted discovery and blocker evidence. | phase contract | scaffold-created | {{FIRST_PHASE_ID}} |
| Handoff boundary | Do not unlock a dependent phase until report evidence, oracle evidence, progress log, and this ledger are updated. | phase report | scaffold-created | {{FIRST_PHASE_ID}} |

## Code Summary Writeback Rules

- After inspecting code, summarize discovered files, services, routes, schemas, tests, and runtime commands back into `source-packet.md`.
- Record cross-phase interface decisions here before handing off, especially API contracts, shared state, data shape, UI route assumptions, eval criteria, and rollback boundaries.
- If a phase changes a boundary another phase depends on, update that dependent phase's report handoff and the relevant oracle item notes.
- If a second agent cannot identify the next concrete action from this file, `progress-log.md`, and `agent-handoff.md`, stop and write a blocker instead of guessing.

## Current Continuity Status

- Active phase: {{FIRST_PHASE_ID}}
- Active feature-oracle item: {{FIRST_FEATURE_ID}}
- Current decision: Start from baseline/code-summary evidence, then unlock dependent phases in manifest order.
- Next action: Execute {{FIRST_PHASE_ID}}, update code facts, and write durable evidence before implementation phases proceed.
