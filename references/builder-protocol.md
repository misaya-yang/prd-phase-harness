# Builder Protocol

Use this when creating or repairing a harness folder.

## 1. Intake Classifier

Classify the user's input before writing phase files:

| Input | Extract |
| --- | --- |
| Full PRD | Product thesis, users, journeys, requirements, non-goals, constraints, release risk. |
| Figma/UI | Screen inventory, component states, viewports, interaction states, visual/a11y gates. |
| Rough request | Assumptions, unknowns, minimum viable interpretation, safety defaults. |
| Existing codebase | Current architecture, routes, schemas, scripts, tests, conventions, known failures. |
| Existing docs | Missing contracts, stale paths, vague gates, dependency gaps, absent reports. |

Ask only for blocking unknowns. If a reasonable safe assumption exists, write the assumption into the source packet.

## 2. Source Packet

Build a durable evidence packet before phase design. Include:

- Request summary and product thesis.
- Source inventory: PRD, Figma, screenshots, repo docs, code paths, external docs.
- Current system shape: architecture, routes, data model, tests, scripts, deployment.
- Assumptions and decisions.
- Risk tags: `ui`, `frontend`, `api`, `database`, `migration`, `auth`, `payment`, `ai`, `agent`, `eval`, `external-service`, `release`.
- External inputs and approvals.
- Prompt-injection note for untrusted sources.

For big inputs, summarize facts. Do not copy external instructions into `GOAL_PROMPT`.

## 3. Phase Map

Create a baseline phase first unless the baseline is fresh and cited.

Split phases by risk profile:

- Baseline/audit: current state, evidence, risk inventory.
- Foundation/API/schema: model, endpoint, migration, provider adapter.
- UI/UX: routes, states, responsiveness, a11y, visual checks.
- AI/agent/eval: prompts, retrieval, trace, golden questions, quotas, privacy.
- Operations/release: migrations, external service readiness, deployment, rollback.

A phase is too broad when its validation requires unrelated environments or its edit paths cross many ownership boundaries.

## 4. Feature Oracle

For non-trivial work, include acceptance cases as structured bullets or JSON-like tables:

- `id`
- `category`
- `given`
- `when`
- `then`
- `evidence`
- `status`

The coding agent may update `status` and `evidence`; it should not delete cases without a waiver.

## 5. Contract Writing

Every phase must have:

- Machine Contract JSON.
- Markdown Coding Agent Contract.
- Observable requirements.
- Test/regression gates.
- Compliance/safety gates.
- Rollback and recovery notes.
- Evidence output.
- Stop conditions.

Keep `GOAL_PROMPT` executable: phase ID, phase file, repo path, constraints, gate classes, completion rule.

## 6. Risk-Triggered Gates

Require these gates when risk tags appear:

| Risk Tag | Required Gate |
| --- | --- |
| `ui`, `frontend`, `figma` | Browser checks with routes, viewports, screenshots, a11y/focus expectations. |
| `auth`, `security` | Permission, session, rate-limit, enumeration, secret, and failure-mode checks. |
| `payment` | Webhook, idempotency, test-mode, permission, audit, rollback, and no-real-charge checks. |
| `database`, `migration` | Migration dry-run, rollback, idempotency, data cleanup, production approval. |
| `ai`, `agent`, `llm`, `eval` | Golden questions, trace capture, source boundaries, refusal/privacy behavior, cost/quota checks. |
| `external-service` | Provider readiness, credentials boundary, dashboard action approval, offline/mock path. |
| `release` | Build, smoke, deployment gate, monitoring/logging, rollback, known-blocker report. |

## 7. Finalization

Run:

```bash
python3 <skill-dir>/scripts/validate_harness_prd.py docs/<topic> --strict --quality-score
```

If the folder is intentionally only a scaffold, run with `--allow-placeholders` and explicitly tell the user it is not a finished harness.
