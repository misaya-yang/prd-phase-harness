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
- Make the smallest requirement-satisfying change and justify any scope expansion.
- Summarize inspected code facts into `{{DOCS_PATH}}/source-packet.md`.
- Update `{{PROGRESS_LOG_PATH}}`, `{{CONTINUITY_LEDGER_PATH}}`, and the phase report before handoff.
- Record test evidence and review evidence before marking a phase passed.

## Evaluator Notes

- Read the phase report, changed files, validation output, and oracle evidence.
- Reject `passing` status when evidence is missing, superficial, outside the target phase, unreviewed, or broader than the minimal required change.
- Confirm terminal whole-demand regression before the full requirement is considered complete.
- Write findings as actionable file/line or command/check notes.

## Next Handoff

- Active role: planner
- Active phase: {{FIRST_PHASE_ID}}
- Active feature-oracle item: {{FIRST_FEATURE_ID}}
- Required evidence before unlock: phase report, validation output or documented blocker, oracle evidence, review evidence, minimal-change scope note, progress-log entry, continuity-ledger update, and code-summary writeback.
