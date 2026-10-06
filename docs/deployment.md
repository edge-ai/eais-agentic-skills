# Deployment Guide

How to use this skills repository in different agentic coding environments.

## Authorization

This repository and its bundled API materials are proprietary to Edgematrix Inc.
Only users authorized in writing by Edgematrix Inc. may clone, install, use, or
redistribute the contents. Public GitHub visibility or installation by a skills
manager does not grant those rights. See the repository's [LICENSE](../LICENSE).

## Option 1: Skills CLI (recommended)

The [skills.sh](https://www.skills.sh/) CLI installs skills from this repo directly into each agent's native skills directory. It auto-detects installed agents (Claude Code, GitHub Copilot, Codex, Cursor, Windsurf, and more) — for GitHub Copilot, for example, skills land in `~/.agents/skills/`, which it reads natively.

```bash
# install all skills, auto-detect agents
npx skills add edge-ai/eais-agentic-skills

# only specific skills
npx skills add edge-ai/eais-agentic-skills --skill aip-builder

# target a specific agent, globally
npx skills add edge-ai/eais-agentic-skills -g -a github-copilot

# update later
npx skills update
```

Useful flags: `-g/--global` (user-level install), `--skill <name>` to select specific skills, `-a/--agent <agents>` to target specific agents, `-y` for non-interactive mode.

> The CLI is third-party tooling. Review its current privacy and telemetry policies before using it
> in an environment with confidentiality requirements. Use it only if authorized under the
> proprietary terms above.

## Option 2: Git Submodule (for teams)

Add to any project as a submodule:

```bash
git submodule add https://github.com/edge-ai/eais-agentic-skills.git .ai-skills
```

Then copy or symlink each required `skills/<skill-name>/` directory into the
target agent's project-level skills directory. Directory names differ by agent;
consult that agent's skills documentation. The consumable unit is the
self-contained skill directory, not the repository root.

The repository publishes three developer-facing skills. They form the AIP → Flow →
Dashboard authoring pipeline.

## Option 3: Direct Clone

Clone directly as your workspace when doing pure skill development:

```bash
git clone https://github.com/edge-ai/eais-agentic-skills.git
```

## Platform Compatibility

The skills CLI (Option 1) auto-detects installed agents and handles per-agent
bindings. For manual installs, copy or symlink each self-contained skill into
the target agent's native skills directory; do not rely on repository-level
instruction files.

Installation is not evidence of activation. Explicitly ask the agent to use `aip-builder`,
`node-red-flow-architect`, or `node-red-dashboard-architect`, and inspect its skill-loading trace
when supported. Do not assume that slash-command syntax or automatic selection is identical across
agents. The README provides example prompts and prerequisites for station development.

## Updating

Skills CLI installs:

```bash
npx skills update
```

Submodule installs:

```bash
cd .ai-skills && git pull origin main && cd ..
git add .ai-skills && git commit -m "Update agentic skills"
```
