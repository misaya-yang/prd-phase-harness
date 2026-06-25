# Long-Running Agent Protocol

Use this when a harness must support multiple sessions, subagents, or independent evaluation.

## Core Pattern

A long-running coding harness should preserve state in files, not in chat memory or pre-compaction context:

```text
source packet -> loop contract -> loop state -> feature oracle -> continuity ledger -> phase contract -> session boot -> one-feature execution -> actor report -> independent critic verdict -> handoff
```

This follows two practical findings from modern agent harness work:

- A fresh agent needs a compact way to recover state after context compaction, choose the next unit of work, and restart the environment.
- The agent doing the work should not be the only judge of whether the work is complete when the task is broad or high-risk.

## Required Runtime Files

| File | Purpose | Update Rule |
| --- | --- | --- |
| `context-profile.json` | Progressive disclosure budget: hot path, role-specific load profiles, deferred triggers, and files not loaded by default. | Builder owns; runners obey it before opening more context. |
| `source-packet.md` | Durable facts, trust boundaries, assumptions, and risk inventory. | Builder updates; runners cite, not rewrite broadly. |
| `loop-contract.json` | The control loop: observe, select, execute, verify, record, decide. | Builder owns; runners follow it and do not remove verification/record steps. |
| `loop-state.json` | Active phase, feature, iteration, status, last decision, and next action. | Runners update after each decision and before exit. |
| `feature-oracle.json` | End-to-end feature and test cases. | Runners update only `status`, `evidence`, and `notes`. |
| `progress-log.md` | Session history, current blocker, clean-state note. | Append at start/end of work. |
| `agent-handoff.md` | Planner/generator/critic file-based messages. | Keep brief and actionable. |
| `continuity-ledger.md` | Cross-phase relatedness, code-summary writeback, and interface boundary decisions. | Update when code facts, contracts, phase dependencies, or downstream assumptions change. |
| `next-window-prompt.md` | Copy-ready fresh-window prompt. | Update when the active target phase changes. |

## Session Boot

Every fresh agent should:

1. Run `pwd` and confirm the repo root.
2. Read `context-profile.json`, `loop-state.json`, and the target phase file.
3. Read only the role-specific hot-path `PRIMARY_CONTEXT` before planning.
4. Check recent git history when available.
5. Run the baseline/smoke command named in the target phase before adding new work.
6. Pick one phase and one feature-oracle item.
7. Execute the loop cycle: observe, select, execute, verify, record, decide.
8. Make the smallest requirement-satisfying change, then write inspected code facts and interface decisions back into `source-packet.md` and `continuity-ledger.md` before handoff.
9. Record test evidence and minimal-change scope, then request an independent critic/subagent review before marking the phase passed.

If baseline checks fail, fix or document that state before starting new feature work.
Do not load README, manifest, full source packet, full feature oracle, progress log, handoff, continuity ledger, prior reports, or next-window prompt until the context profile trigger applies.

## Feature Oracle

Write oracle cases as observable behavior:

```json
{
  "id": "PAY-F001",
  "phase_id": "PAY-02",
  "category": "api",
  "description": "A paid invoice webhook updates ledger state exactly once.",
  "steps": [
    "Send a signed test-mode webhook payload.",
    "Verify ledger state and idempotency record.",
    "Replay the same payload and verify no duplicate ledger entry."
  ],
  "status": "failing",
  "evidence": "",
  "notes": ""
}
```

Status policy:

- `failing`: default for unverified work.
- `passing`: requires actor evidence plus an independent critic artifact with `Critic Verdict: approved`.
- `blocked`: requires a named blocker and next action.
- `waived`: requires user waiver, reason, and residual risk.

## Loop Contract

Use the loop contract to make the workflow executable instead of prompt-only:

```json
{
  "schema_version": "prd-phase-harness/loop-contract/v1",
  "goal": "Run one bounded phase and one feature-oracle item until evidence proves pass, block, or fail.",
  "cycle": ["observe", "select", "execute", "verify", "record", "decide"],
  "max_iterations": 3,
  "state_file": "docs/topic/loop-state.json",
  "oracle_file": "docs/topic/feature-oracle.json",
  "done_when": ["phase report exists", "required evidence is recorded"],
  "continue_when": ["validator is clean", "work remains in the selected phase"],
  "stop_when": ["credentials are missing", "edits outside boundary are required"]
}
```

Never remove `verify`, `record`, or `decide` from the cycle. Without those steps the harness becomes a prompt again.

## Planner/Generator/Critic Loop

Use this loop when work is complex enough to justify more than one role:

1. Planner writes the source packet, feature oracle, phase map, and target phase contract.
2. Generator proposes a phase contract or plan before editing.
3. Evaluator reviews the proposed contract before implementation when the source is ambiguous or the risk is high.
4. Generator implements one target item and writes evidence.
5. Critic independently checks the runtime, changed files, report, and oracle status from a separate context or subagent.
6. Critic checks minimal-change scope, test coverage, and regression impact, then writes `Critic Verdict: approved`, `changes_requested`, `blocked`, or `waived`.
7. Generator fixes critic findings or records a blocker.

Keep role communication in `agent-handoff.md` or reports. Do not rely on hidden chat history.

## Continuity Ledger

Use `continuity-ledger.md` to keep all generated phase PRDs related instead of isolated:

- Map each phase to its feature-oracle item, dependency, unlock target, handoff boundary, and required writeback.
- Record code/interface facts that downstream phases inherit, including API contracts, state shape, routes, schemas, eval criteria, and rollback boundaries.
- When code inspection changes a prior assumption, update the ledger and dependent phase handoff notes before continuing.
- If a fresh agent cannot identify the next concrete action from the continuity ledger, progress log, and handoff, stop and write a blocker.

## Next-Window Prompt Requirements

The prompt must name:

- skill to use
- repo or docs path
- context profile path
- target phase ID and phase file
- target feature-oracle item
- loading order
- one-phase and one-feature rule
- loop cycle
- edit boundaries
- code-summary writeback and continuity-ledger update
- validation and evidence requirements
- test evidence, independent critic verdict, and minimal-change scope
- terminal whole-demand regression when the final phase or release gate is assigned
- stop conditions for credentials, production systems, destructive commands, and out-of-scope edits
- progressive disclosure rule: open deferred files only when their trigger applies

Avoid vague prompts like "continue from here." A good prompt lets a new window start without this conversation.

## Complexity Control

Harness components are assumptions about what the model cannot do reliably alone. Keep them only when they protect real risk:

- Keep planner when raw prompts under-specify scope.
- Keep critic review mandatory for completion claims; increase critic depth when completion quality is subjective, UI-heavy, AI/eval-heavy, release-sensitive, or hard to verify from code.
- Keep phase decomposition when validation or edit boundaries differ.
- Simplify when a task has one clear file boundary and deterministic validation.
