# {{TITLE}} Next Window Prompt

Use this prompt to start a fresh Codex, Claude Code, or Agent Skills-compatible window.

```text
Use $prd-phase-harness to continue the harness at `{{DOCS_PATH}}`.

Target phase: {{FIRST_PHASE_ID}}
Target phase file: `{{FIRST_PHASE_FILE}}`
Target feature-oracle item: {{FIRST_FEATURE_ID}}

Cold-start protocol:
1. Open `{{CONTEXT_PROFILE_PATH}}`.
2. Open `{{DOCS_PATH}}/loop-state.json`.
3. Open only the target phase file: `{{FIRST_PHASE_FILE}}`.
4. Do not open README, manifest, full source packet, full oracle, progress log, handoff, continuity ledger, or prior reports unless `context-profile.json` says the trigger applies.
5. Open only the target phase's hot-path `PRIMARY_CONTEXT` before planning.

Execution rule:
- Work on exactly one phase and one feature-oracle item.
- Follow the loop cycle: observe, select, execute, verify, record, decide.
- Stay inside the phase edit boundaries.
- Run the required validation and runtime checks.
- Summarize code facts back into targeted source-packet and continuity-ledger sections before handoff.
- Update the phase report, progress log, handoff file, continuity ledger, and oracle evidence before claiming completion.
- Request an independent critic/subagent or fresh-context reviewer to write a separate critic artifact; actor self-review is not completion evidence.
- Treat `--strict` as structure readiness only; run `--strict --completion-gate --phase {{FIRST_PHASE_ID}}` before claiming this phase is complete.
- Preserve progressive disclosure: load additional files only when the context profile trigger is met.
- Stop and document blockers instead of guessing when credentials, production systems, destructive commands, or out-of-scope edits are required.
```
