# Research Notes

Load this file only when you need the rationale behind the PRD phase harness pattern or when adapting it to a new domain.

## Local Pattern Summary

The `ai-tech-blog` docs show two useful generations of the pattern:

- `docs/harness_engine/`: a harness roadmap where each phase is a bounded module with task spec, problem boundary, context policy, execution capture, evaluator protocol, acceptance criteria, and risks.
- `docs/product_optimization/`: a more mature agent-ready folder with README loading protocol, `phase-manifest.md`, stable `Coding Agent Contract` anchors, dependency flow, validation matrix, shared agent rules, and precise goal prompts.

The strongest local conventions are:

- Use README as the folder-level operating manual.
- Use phase-manifest as a compact index to avoid loading every markdown file.
- Put stable grep anchors in every phase.
- Treat `GOAL_PROMPT` as the text an agent can use to start a goal.
- Bound the agent with `PRIMARY_CONTEXT`, `LIKELY_EDIT_PATHS`, and `DO_NOT_EDIT`.
- Require command validation, browser checks, and acceptance gates before completion.
- Keep reports and evidence under predictable paths.

## External Harness Concepts

Recent harness-engine writing frames agent performance as a model-harness-environment system, not a model alone. Useful concepts to reflect in phase docs:

- Task specification: define the work as executable behavior, not a loose wish.
- Context selection: name exactly what the agent should read first.
- Tool access: identify commands, browser checks, Figma/design tools, eval scripts, and migrations.
- Project memory: persist assumptions, decisions, and reports in files.
- Task state: force plan-first execution and phase status.
- Observability: require traces, screenshots, command output summaries, run logs, or tables.
- Failure attribution: require blockers and root-cause notes when validation fails.
- Verification: make tests, gates, and regression scope explicit.
- Permissions: distinguish allowed edits, protected files, data mutation, credentials, and approval needs.
- Intervention recording: document when a user waiver or decision changes scope.

Relevant sources:

- AI Harness Engineering, arXiv 2605.13357: identifies responsibilities including task specification, context selection, tool access, memory, observability, failure attribution, verification, permissions, entropy auditing, and intervention recording.
- Agentic Harness Engineering, arXiv 2604.25850: emphasizes file-level harness components, experience observability, and decision observability.
- From Model Scaling to System Scaling, arXiv 2605.26112: argues that agent outcomes depend on memory, context construction, skill routing, orchestration, and verification/governance layers.
- Harness Worker Agents documentation: worker agents combine instructions, model connectors, MCP-connected sources, inputs, environment variables, pipeline triggers, outputs, and approval/review loops.
- Atlassian Rovo agent manifest documentation: useful product analogy for named agent profiles with prompt, conversation starters, actions, and follow-up prompts.

## Adaptation Heuristics

For a full PRD:

- Preserve product thesis and user journeys.
- Convert every major capability into a phase or requirement.
- Put speculative ideas into non-goals or future phases.

For Figma UI:

- Extract screen inventory, states, components, responsive breakpoints, empty/error/loading states, and accessibility expectations.
- Translate visual requirements into browser checks and screenshot evidence.

For rough oral requirements:

- Write an assumptions section.
- Create a discovery/baseline phase first.
- Prefer fewer, safer phases with explicit stop conditions.

For AI/agent features:

- Include source boundaries, prompt contracts, eval/golden questions, trace capture, quota/cost checks, and refusal/privacy behavior.

For data/schema features:

- Include migration, rollback, seed/idempotency, privacy, permissions, and data-retention gates.

For frontend features:

- Include route inventory, viewport checks, keyboard/focus behavior, a11y, loading/error/empty states, and screenshot evidence.
