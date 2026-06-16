# {{TITLE}} Next Window Prompt

Use this prompt to start a fresh Codex, Claude Code, or Agent Skills-compatible window.

```text
Use $prd-phase-harness to continue the harness at `{{DOCS_PATH}}`.

Target phase: {{FIRST_PHASE_ID}}
Target phase file: `{{FIRST_PHASE_FILE}}`

Cold-start protocol:
1. Open `{{DOCS_PATH}}/README.md`.
2. Open `{{DOCS_PATH}}/phase-manifest.md`.
3. Open `{{DOCS_PATH}}/loop-contract.json`.
4. Open `{{DOCS_PATH}}/loop-state.json`.
5. Open `{{DOCS_PATH}}/feature-oracle.json`.
6. Open `{{DOCS_PATH}}/progress-log.md`.
7. Open `{{DOCS_PATH}}/agent-handoff.md`.
8. Open only the target phase file and its `PRIMARY_CONTEXT` before planning.

Execution rule:
- Work on exactly one phase and one feature-oracle item.
- Follow the loop cycle: observe, select, execute, verify, record, decide.
- Stay inside the phase edit boundaries.
- Run the required validation and runtime checks.
- Update the phase report, progress log, handoff file, and oracle evidence before claiming completion.
- Stop and document blockers instead of guessing when credentials, production systems, destructive commands, or out-of-scope edits are required.
```
