# Research Notes

Load this file when explaining the PRD phase harness paradigm, adapting it to a new domain, or writing public-facing rationale.

## Local Pattern Summary

The `ai-tech-blog` repository contains three useful examples:

- `docs/harness_engine/`: early bounded phase modules with task spec, problem boundary, context policy, execution capture, evaluator protocol, acceptance criteria, and risks.
- `docs/product_optimization/`: mature agent-ready docs with README loading protocol, `phase-manifest.md`, stable `Coding Agent Contract` anchors, dependency flow, validation matrix, shared agent rules, and precise goal prompts.
- `docs/email_rabc/`: stronger release-style pattern with external inputs checklist, phase report index, provider readiness, RBAC/security gates, and explicit blocked-state handling.

The strongest local conventions are:

- README acts as the folder-level operating manual.
- Manifest acts as the compact machine index.
- Every phase has grep-friendly contract anchors.
- `GOAL_PROMPT` is the runnable handoff text for a fresh agent.
- `PRIMARY_CONTEXT`, `LIKELY_EDIT_PATHS`, and `DO_NOT_EDIT` bound the agent.
- Tests, browser/runtime checks, compliance gates, and acceptance gates are required before completion.
- Reports and evidence live under predictable paths.
- External service actions, credentials, migrations, deploys, and DNS changes are explicit approval boundaries.

## External Research Synthesis

Current harness-engine research frames agent performance as a model-harness-environment system, not a model alone. A strong phase folder should therefore encode the harness responsibilities that the runtime may not provide natively.

Map the research concepts into docs like this:

| Harness Concept | Phase Folder Translation |
| --- | --- |
| Task specification | `GOAL_TARGET`, `GOAL_PROMPT`, `Task Spec`, observable requirements |
| Context selection | `READ_FIRST`, `PRIMARY_CONTEXT`, manifest grep usage |
| Tool access | `VALIDATION_COMMANDS`, `BROWSER_CHECKS`, Figma/design inputs, migration commands |
| Project memory | README assumptions, decisions, phase reports |
| Task state | phase IDs, dependency flow, report status |
| Fresh-window recovery | feature oracle, progress log, continuity ledger, handoff packet, next-window prompt |
| Cross-phase relatedness | continuity ledger, source-packet code-summary writeback, phase report handoff |
| Control loop | loop contract, loop state, observe/select/execute/verify/record/decide cycle |
| Observability | screenshots, traces, logs, eval tables, command summaries |
| Failure attribution | blocker notes, stop conditions, failed gate explanations |
| Verification | tests, regression scope, acceptance gates |
| Permissions | edit boundaries, do-not-edit paths, approval requirements |
| Entropy auditing | release gates, drift checks, freshness checks, repeated validation |
| Intervention recording | user waivers, scope changes, external approvals in reports |

## Source Notes

- OpenAI Codex: https://openai.com/index/introducing-codex/
- OpenAI Codex Skills: https://developers.openai.com/codex/skills
- OpenAI Codex Subagents: https://developers.openai.com/codex/subagents
- OpenAI Codex MCP: https://developers.openai.com/codex/mcp
- OpenAI Codex Rules: https://developers.openai.com/codex/rules
- Claude Code Skills: https://code.claude.com/docs/en/skills
- Claude Code Subagents: https://code.claude.com/docs/en/sub-agents
- Claude Code Memory: https://code.claude.com/docs/en/memory
- Claude Code Best Practices: https://code.claude.com/docs/en/best-practices
- Anthropic, Effective harnesses for long-running agents: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- Anthropic, Harness design for long-running applications: https://www.anthropic.com/engineering/harness-design-long-running-apps
- Anthropic, Effective context engineering for AI agents: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Anthropic, Demystifying evals for AI agents: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- Agent Skills specification: https://agentskills.io/specification
- Agent Skills evaluation guidance: https://agentskills.io/skill-creation/evaluating-skills
- AI Harness Engineering, arXiv 2605.13357: identifies task specification, context selection, tool access, project memory, task state, observability, failure attribution, verification, permissions, entropy auditing, and intervention recording as harness responsibilities.
- Agentic Harness Engineering, arXiv 2604.25850: emphasizes component observability, experience observability, and decision observability for evolving coding-agent harnesses.

## Practical Heuristics

For long-running coding work:

- Start every generated harness with a feature oracle and progress log.
- Write a loop contract and loop state so agents execute a workflow rather than merely following a prompt.
- Keep one phase and one oracle item as the atomic execution unit.
- Ask the runner to run baseline/smoke checks before new work.
- Use a separate evaluator when UI behavior, agent behavior, migration safety, release readiness, or subjective quality is part of completion.
- Make the next-window prompt concrete enough that the next agent does not need the current chat.
- Require agents to summarize inspected code facts back into durable files before handoff; otherwise phases drift into isolated PRDs instead of a connected execution chain.

For a full PRD:

- Preserve product thesis, user journeys, constraints, and non-goals.
- Convert capabilities into phases only when each phase can produce evidence.
- Put speculative ideas into non-goals or future phases.

For Figma/UI:

- Extract screen inventory, states, components, responsive breakpoints, empty/error/loading states, and accessibility expectations.
- Translate visual requirements into browser checks and screenshot evidence.

For rough oral requirements:

- Write assumptions.
- Create baseline/discovery first.
- Prefer fewer, safer phases with explicit stop conditions.

For AI/agent features:

- Include source boundaries, prompt contracts, golden questions, eval tables, trace capture, quota/cost checks, refusal behavior, and privacy gates.

For data/schema features:

- Include migration, rollback, seed/idempotency, privacy, permission, retention, and production-approval gates.

For frontend features:

- Include route inventory, viewport checks, keyboard/focus behavior, accessibility, loading/error/empty states, and screenshots.

## Anti-Patterns

- Treating a phase folder as prose documentation instead of an executable contract.
- Writing `GOAL_PROMPT` as a vague summary.
- Letting a phase edit the whole repo.
- Omitting reports because tests passed in chat.
- Hiding external service actions inside implementation phases.
- Mixing discovery, schema, UI, eval, and release work in one phase.
- Using "works well" or "improve UX" as an acceptance gate.
- Leaving future ideas in executable scope.
- Marking oracle items `passing` without evidence.
