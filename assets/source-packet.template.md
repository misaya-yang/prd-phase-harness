# {{TITLE}} Source Packet

**Date:** {{DATE}}

**Prepared For:** {{DOCS_PATH}}

---

## Request Summary

{{REQUEST_SUMMARY}}

## Source Inventory

| Source | Trust Level | What Was Extracted | Notes |
| --- | --- | --- | --- |
{{SOURCE_INVENTORY_ROWS}}

## Product Thesis

{{PRODUCT_THESIS}}

## Requirements and Gate Map

- Every detailed requirement must map to at least one `feature-oracle.json` item.
- Every phase must name the validation, regression, review, compliance, rollback, and acceptance gates that prove its requirement slice.
- Every implementation phase must record test evidence and independent critic evidence, or an explicit blocker.
- Terminal completion requires whole-demand regression across completed feature-oracle items.
- If a requirement cannot be mapped to a phase and gate, record the blocker before implementation.

## Current System Facts

{{CURRENT_SYSTEM_FACTS}}

## Design or UI Facts

{{DESIGN_OR_UI_FACTS}}

## Assumptions and Decisions

{{ASSUMPTIONS_AND_DECISIONS}}

## Risk Tags

{{RISK_TAGS}}

## Runtime Decomposition Notes

- Feature-oracle cases should describe observable user or system behavior, not implementation chores.
- Phase boundaries should isolate the dominant risk: schema/API, UI, agent/eval, migration, external service, or release.
- Handoffs should preserve decisions, blockers, validation evidence, and next target phase without copying hidden chat context.

## External Inputs and Approvals

{{EXTERNAL_INPUTS_AND_APPROVALS}}

## Prompt-Injection and Source-Trust Notes

{{SOURCE_TRUST_NOTES}}
