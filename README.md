# AG2 Project Creator (Antigravity Skill)

This repository contains an open-source **AG2 Project Creator Skill** designed for the Antigravity AI agent framework. When installed, it empowers your local AI assistant to automatically bootstrap production-ready, multi-agent AI applications powered by [AG2](https://ag2.ai) (formerly AutoGen 2.0).

Unlike generic templates, this skill acts as an "AG2 Brain" for your AI. It contains a comprehensive **Pattern Cookbook** and strict engineering guidelines to ensure the code your AI writes is secure, modern, and aligned with AG2 v0.11+ best practices.

## Features

- **Modern AG2 Architecture**: Uses `GroupChat` instead of the deprecated `Swarm` API.
- **Topological Pattern Cookbook**: The AI is instructed on how to generate the 5 official GroupChat patterns:
  - `AutoPattern` (Context-Aware Routing)
  - `DefaultPattern` (State Machines, Escalation, Hierarchical)
  - `RoundRobinPattern` (Sequential Pipelines)
  - `RandomPattern` & `ManualPattern`
- **Human-in-the-Loop (HITL)**: Built-in support for approval workflows using `human_input_mode="TERMINATE"`.
- **Local Code Execution**: Configured to run generated Python code securely inside sandboxed temporary directories (`LocalCommandLineCodeExecutor`).
- **Observability Integrated**: Generates OpenTelemetry-ready projects (Jaeger/Console tracing) out of the box.
- **FastMCP Support**: Includes boilerplate for building Model Context Protocol (MCP) servers and clients.

## Installation (For Antigravity Agents)

To install this skill so your AI assistant can use it:

1. Copy the contents of this repository into your Antigravity skills folder:

   ```bash
   mkdir -p .agents/skills/ag2_project_creator
   cp -r * .agents/skills/ag2_project_creator/
   ```

2. The AI will automatically discover `SKILL.md` and learn its new capabilities.

## Usage

Once installed, simply ask your Antigravity assistant to spawn a project or use a specific slash command.

### Bootstrapping a New Project
>
> "Create a new AG2 project in this folder."

The AI will generate the `pyproject.toml`, `.env`, `main.py` entrypoint with tracing, and `config/llm.py`.

### Using Specific Slash Commands

You can directly command the AI to generate specific components using these triggers:
- `/ag2-groupchat` - Generates a multi-agent logic flow using one of the 5 official patterns.
- `/ag2-workflow` - Maps a complex architecture (Escalation, Feedback Loop, Hub-and-Spoke) to AG2 code.
- `/ag2-agent` - Generates specialized sub-agents with proper contexts.
- `/ag2-tool` - Explica cómo crear decoradores `@agent.register_for_execution()`.
- `/ag2-code-executor` - Generates a secure sandboxed environment for the AI to run code.
- `/ag2-mcp` - Generates FastMCP Server/Client configurations.

## Contributing

Contributions to expand the Cookbook with new AG2 architectures are welcome! Please open an issue or submit a Pull Request.
