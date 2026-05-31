# Phase Folder Spec

Use this reference when creating or reviewing a harness-style PRD folder.

## Folder Layout

```text
docs/<topic>/
├── README.md
├── phase-manifest.md
├── phase-00-<baseline-slug>.md
├── phase-01-<slug>.md
├── phase-02-<slug>.md
└── reports/
```

Create `reports/` only when implementation reports or screenshots are expected soon. Do not create empty report files.

## README.md

Purpose: orient both humans and agents without requiring them to load every phase.

Recommended sections:

- Title
- Date
- Owner
- Purpose
- Coding Agent Loading Protocol
- Product Thesis
- Input Sources and Assumptions
- Current Product or System Shape
- Highest-Impact Findings, if a baseline/review exists
- Phase Order
- Roadmap Cohesion
- Shared Harness Contract
- Global Non-Goals
- Standard Verification Commands
- Required Browser/View/Runtime Checks, if applicable

Include a loading protocol similar to:

```markdown
## Coding Agent Loading Protocol

When assigned a phase goal:

1. Open this `README.md`.
2. Open `phase-manifest.md`.
3. Locate the target with `rg -n "PHASE_ID: <ID>|GOAL_PROMPT|VALIDATION_COMMANDS|ACCEPTANCE_GATES" docs/<topic>`.
4. Open only the target phase file and files listed in `PRIMARY_CONTEXT`.
5. Set the execution goal from `GOAL_PROMPT`.
6. Treat `LIKELY_EDIT_PATHS` as the intended write boundary.
7. Complete `VALIDATION_COMMANDS`, `BROWSER_CHECKS`, `REGRESSION_SCOPE`, and `ACCEPTANCE_GATES` before claiming completion.
```

## phase-manifest.md

Purpose: compact machine index. Prefer tables and grep anchors over prose.

Required sections:

- Grep Usage
- Phase Index
- Dependency Flow
- Validation Matrix
- Goal Setup Templates
- Shared Agent Rules

Phase index columns:

- `PHASE_ID`
- File
- Depends On
- Goal Target
- Main Validation
- Evidence Output

Validation matrix columns:

- `PHASE_ID`
- Mutates Data
- Needs Browser/UI
- Needs Agent/LLM Eval
- Needs Migration
- Release Blocking

## Phase File

Every phase file should be assignable as a standalone agent goal.

Use this section order:

```markdown
# Phase XX - <Name>

> For agentic workers: enter plan-first mode before editing. Create or update a plan, execute in bounded steps, run verification, and record blockers before moving on.

**Goal:** <one clear outcome>

**Architecture:** <how the phase should fit the existing system>

**Tech Stack:** <specific frameworks, files, services, tools>

---

## Coding Agent Contract

- PHASE_ID: <PREFIX-XX>
- GOAL_TARGET: <single sentence target>
- GOAL_PROMPT: Complete <PREFIX-XX> <Name> for `<repo>` by following `docs/<topic>/phase-XX-<slug>.md`; <key constraints>; finish only after validation, regression, compliance, evidence, and acceptance gates pass or blockers are documented.
- DEPENDS_ON: <none or IDs>
- READ_FIRST: `docs/<topic>/README.md`, `docs/<topic>/phase-manifest.md`, this file
- PRIMARY_CONTEXT: <files, routes, schemas, APIs, design artifacts>
- LIKELY_EDIT_PATHS: <bounded paths>
- DO_NOT_EDIT: <non-goals and protected files>
- EXECUTION_MODE: plan-first; implement stepwise; verify before completion
- VALIDATION_COMMANDS: <commands>
- BROWSER_CHECKS: <routes and viewports, or none>
- REGRESSION_SCOPE: <existing behavior that must still work>
- COMPLIANCE_GATES: <privacy, security, a11y, data retention, legal, brand, content boundaries>
- ACCEPTANCE_GATES: <deterministic gates>
- EVIDENCE_OUTPUT: <report path, screenshots, logs, tables>
- STOP_CONDITIONS: <when to stop and ask/document instead of guessing>

## Task Spec

## Problem Boundary

## Context Policy

## Product Requirements

### R1 <Requirement Name>

## Test and Regression Requirements

## Compliance and Safety Requirements

## Execution Capture

## Evaluator Protocol

## Acceptance Criteria

## Risks
```

## Phase Sizing

Use phases, not tiny implementation tasks. A good phase has:

- One coherent product or engineering outcome.
- Clear dependency boundaries.
- Enough scope for a coding agent to make meaningful changes.
- Enough constraints to prevent unrelated rewrites.
- Verification that can complete in the current repo.

Split a phase when:

- It mixes schema/backend/UI/release work with independent risk profiles.
- It needs different validation environments.
- It would require broad edits outside `LIKELY_EDIT_PATHS`.
- It depends on feedback from a prior phase.

Merge phases when:

- They cannot produce value or evidence separately.
- The second phase is only cleanup required by the first.

## Metadata Rules

Use stable, grep-friendly labels. Keep values concrete:

- Use IDs like `PO-05`, `HE-00`, `NF-02`.
- Put commands in backticks and separate multiple commands with semicolons.
- Name exact files, routes, endpoints, data tables, and artifacts.
- Put "none" explicitly when a field has no values.
- Do not use vague gates like "works well" without a measurable check.

`GOAL_PROMPT` should include:

- Phase ID and name.
- Absolute or repo-relative phase path.
- Main implementation constraints.
- Required validation classes.
- Completion rule.

## Requirement Writing

Write requirements as observable behavior:

- "When owner publishes a draft, status becomes `published`, visibility becomes `public`, and `publishedAt` is set if missing."
- "Public source cards must never include hidden/admin/draft content."
- "Mobile viewport `390x844` must have no horizontal overflow."

Avoid:

- "Improve UX."
- "Make it robust."
- "Add AI magic."

## Test and Regression Requirements

Include the smallest credible command set for each phase:

- Static/type checks.
- Unit/integration tests.
- Route/API tests.
- Browser checks for UI.
- Migration checks for schema work.
- Golden questions/evals for agent behavior.
- Build or bundle checks for release-sensitive work.

For rough early phases, allow explicit blocker documentation, but do not let "blocked" silently become "passed."

## Compliance and Safety Requirements

Include this section even if it says "none beyond standard repo policies." Consider:

- Privacy and PII.
- Auth and permissions.
- Hidden/admin/draft content boundaries.
- Data retention and deletion.
- External API keys/secrets.
- Accessibility.
- Security and rate limiting.
- Copyright/licensing.
- Brand/design constraints.
- Migration and rollback safety.

## Evidence Output

Require artifacts that survive the chat:

- Markdown report under `docs/<topic>/reports/`.
- JSON route/audit output.
- Browser screenshots.
- Console/network error summaries.
- Golden question table.
- Migration notes.
- Test command summaries.
- Known blockers list.

## Review Checklist

Before finalizing a folder, verify:

- README explains how agents should load the folder.
- Manifest indexes every phase and dependencies are acyclic.
- Every phase has the complete `Coding Agent Contract`.
- Every phase has bounded `PRIMARY_CONTEXT`, `LIKELY_EDIT_PATHS`, and `DO_NOT_EDIT`.
- Every phase has explicit tests, regression scope, compliance gates, acceptance gates, and evidence output.
- Baseline/audit exists or is explicitly waived.
- Non-goals prevent scope creep.
- No phase depends on unstated chat context.
- No placeholder text remains.
