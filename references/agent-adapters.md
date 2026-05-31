# Agent Adapters

Use this to keep harnesses portable across Codex, Claude Code, and Agent Skills-compatible tools.

## Portable Paths

In skill instructions, refer to scripts as:

```text
<skill-dir>/scripts/<script>.py
```

The active agent should resolve `<skill-dir>` from the directory containing this `SKILL.md`. Avoid hardcoding user-specific paths such as `/Users/<name>` or assuming only `~/.codex/skills`.

In generated harness docs, prefer repo-relative paths unless the user's workflow requires absolute paths for goal prompts.

## Codex Notes

Codex workflows often have:

- Goal mode for durable long-running objectives.
- Plan tools for visible step tracking.
- Browser/Chrome/computer-use tools for UI verification.
- Plugins/connectors for GitHub, Figma, Vercel, Gmail, and others.
- Skills stored in user or project skill directories.

Generated phases should make browser checks and evidence outputs explicit so Codex can verify before completion.

## Claude Code Notes

Claude Code workflows often have:

- Plan mode before editing.
- Project/user `CLAUDE.md` memory.
- Skills under `.claude/skills` or user skill directories.
- Custom subagents with separate context windows.
- Permission modes, hooks, and worktrees.

Generated phases should keep context bounded so a subagent can execute a phase without polluting the main session.

## Subagent Guidance

Suggest subagents only when the work is genuinely parallel or high-noise:

- Research explorer for large source packets.
- UI verifier for screenshots and browser paths.
- Security reviewer for auth/payment/data phases.
- Test runner for independent test surfaces.

Do not make subagents mandatory for every phase. A simple phase with one edit boundary should stay simple.

## Plan and Report Portability

Use neutral language:

- "Create a plan before editing" instead of tool-specific commands.
- "Use the available plan tool or write `goal.plan_output`" when durable plan output is required.
- "Write the phase report" instead of assuming a particular task-management integration.

## Tool Policy

Phase contracts should name required tools by capability:

- repo search
- shell validation
- browser verification
- Figma/design inspection
- GitHub read/write
- deployment provider
- database migration runner

The active agent maps capabilities to available tools in its environment.
