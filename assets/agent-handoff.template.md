# {{TITLE}} Agent Handoff

**Created:** {{DATE}}

**Harness Folder:** `{{DOCS_PATH}}`

---

## Planner Notes

- Source packet: `{{DOCS_PATH}}/source-packet.md`
- Feature oracle: `{{FEATURE_ORACLE_PATH}}`
- Continuity ledger: `{{CONTINUITY_LEDGER_PATH}}`
- First target phase: `{{FIRST_PHASE_ID}}`
- First target phase file: `{{FIRST_PHASE_FILE}}`
- First feature-oracle item: `{{FIRST_FEATURE_ID}}`

## Generator Notes

- Work on one phase and one feature-oracle item at a time.
- Stay inside the phase `LIKELY_EDIT_PATHS`.
- Summarize inspected code facts into `{{DOCS_PATH}}/source-packet.md`.
- Update `{{PROGRESS_LOG_PATH}}`, `{{CONTINUITY_LEDGER_PATH}}`, and the phase report before handoff.

## Evaluator Notes

- Read the phase report, changed files, validation output, and oracle evidence.
- Reject `passing` status when evidence is missing, superficial, or outside the target phase.
- Write findings as actionable file/line or command/check notes.

## Next Handoff

- Active role: planner
- Active phase: {{FIRST_PHASE_ID}}
- Active feature-oracle item: {{FIRST_FEATURE_ID}}
- Required evidence before unlock: phase report, validation output or documented blocker, oracle evidence, progress-log entry, continuity-ledger update, and code-summary writeback.
