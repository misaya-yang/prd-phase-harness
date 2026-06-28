# Phase {{PHASE_NUMBER}} - {{PHASE_NAME}}

> Agentic worker: open `{{CONTEXT_PROFILE_PATH}}`, `{{LOOP_STATE_PATH}}`, and this file only. Execute just this phase, make the smallest requirement-satisfying change, write evidence, then stop at the gates. Shared session-boot, loop-cycle, feature-oracle, and code-writeback rules live once in `README.md` and `phase-manifest.md`; this file does not restate them.

- PHASE_ID: {{PHASE_ID}}
- DEPENDS_ON: {{DEPENDS_ON}}
- UNLOCKS: {{UNLOCKS}}
- FEATURE: {{FEATURE_ID}}

**Goal:** {{GOAL}}

## Machine Contract

Single authoritative contract for this phase. The goal prompt, context budget, edit boundaries, validation commands, evidence outputs, and stop conditions all live in this JSON; the four header lines above are only a grep aid. Update `status`, evidence paths, and gates here as the phase progresses.

```json
{{PHASE_CONTRACT_JSON}}
```

## Requirements

### R1 {{R1_NAME}}

{{R1_BODY}}

## Critic Protocol

{{CRITIC_PROTOCOL}}
