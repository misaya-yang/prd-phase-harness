# {{TITLE}} Agent Handoff

**Created:** {{DATE}}

**Harness Folder:** `{{DOCS_PATH}}`

---

## Planner Notes

- Source packet: `{{DOCS_PATH}}/source-packet.md`
- Feature oracle: `{{FEATURE_ORACLE_PATH}}`
- First target phase: `{{FIRST_PHASE_ID}}`
- First target phase file: `{{FIRST_PHASE_FILE}}`

## Generator Notes

- Work on one phase and one feature-oracle item at a time.
- Stay inside the phase `LIKELY_EDIT_PATHS`.
- Update `{{PROGRESS_LOG_PATH}}` and the phase report before handoff.

## Evaluator Notes

- Read the phase report, changed files, validation output, and oracle evidence.
- Reject `passing` status when evidence is missing, superficial, or outside the target phase.
- Write findings as actionable file/line or command/check notes.

## Next Handoff

- Active role: TODO
- Active phase: {{FIRST_PHASE_ID}}
- Active feature-oracle item: TODO
- Required evidence before unlock: TODO
