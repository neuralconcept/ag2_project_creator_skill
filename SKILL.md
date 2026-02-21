---
name: "ag2_project_creator"
description: "Generates boilerplate AG2 projects and provides specialized instructions for generating AG2 agents, workflows, tools, and servers."
---

# AG2 Project Creator Skill

When a user asks to bootstrap or create an "AG2 project" or an "AutoGen project" using this skill, follow these instructions to set up the necessary files and folder structures.

## 1. Directory Structure Setup

Ensure the following directories are created in the target project folder:

- `config/`
- `agents/`
- `tools/`
- `workflows/`
- `mcp_servers/`

## 2. Template Generation

Copy the templates provided in the `templates/` directory of this skill directly into the user's project:

1. **`pyproject.toml`** -> `pyproject.toml`
2. **`.env.example`** -> `.env.example`
3. **`README.md`** -> `README.md`
4. **`config/llm.py`** -> `config/llm.py`
5. **`mcp_servers/example_server.py`** -> `mcp_servers/example_server.py`
6. **`agents/example_agent.py`** -> `agents/example_agent.py`
7. **`main.py`** -> `main.py`

## 3. AG2 Core Concepts (v0.11+)

As an AI agent, you must understand these core AG2 concepts when writing code for the user:

- **Orchestration**: Use `initiate_group_chat` with `AutoPattern` for dynamic agent routing. The `description` field for every agent is critical since `AutoPattern` uses it to decide who speaks next.
  - **CRITICAL**: The old `Swarm` pattern is DEPRECATED in AG2 v0.9+. Do not use swarm imports. Everything is now `GroupChat` with `AutoPattern` and `Handoffs`.
- **State Management**: Use `autogen.agentchat.group.ContextVariables` to share a global dictionary of state between tools and handoffs. Tools should return a `ReplyResult(message="...", context_variables=ctx)` to update state.
- **Handoffs**: Use `agent.handoffs.add_context_condition` (deterministic, cheaper) or `agent.handoffs.add_llm_conditions` (uses LLM evaluation) to force specific conversation paths.
- **Human in the Loop (HITL)**: HITL is strictly managed via the `human_input_mode` parameter on the Human/User agent.
  - `human_input_mode="NEVER"`: Fully autonomous operation.
  - `human_input_mode="TERMINATE"`: Approval workflows. The agent halts and waits for user confirmation ONLY when a termination message is returned (requires `is_termination_msg`).
  - `human_input_mode="ALWAYS"`: Manual step-by-step confirmation. Required when executing dangerous code.
- **Observability**: AG2 uses OpenTelemetry. Always configure `autogen.opentelemetry.instrument_agent` and `instrument_llm_wrapper` as shown in the template to trace executions.
- **Parallel Tools**: MUST be set to `False` in your `LLMConfig` for sequential workflow stability.
- **CaptainAgent**: If passing an agent via JSON config for advanced setups, remember to use `agent_path` (e.g., `autogen/agents/experimental/websurfer/websurfer/WebSurferAgent`).

## 4. AG2 Development Commands (IMPORTANT)

This skill provides you with detailed instructions for generating specific AG2 components. When the user asks you to create any of the following, or if they explicitly use the slash commands mentioned, **you MUST FIRST read the corresponding `.md` file inside the `commands/` directory of this skill** using the `view_file` tool.

- **`/ag2-agent`** or request to **create an agent**: Read `commands/ag2-agent.md`
- **`/ag2-groupchat`** or request for **GroupChat**: Read `commands/ag2-groupchat.md`
- **`/ag2-tool`** or request to **create a tool**: Read `commands/ag2-tool.md`
- **`/ag2-workflow`** or request for **routing workflow**: Read `commands/ag2-workflow.md`
- **`/ag2-mcp`** or request for **MCP server/client**: Read `commands/ag2-mcp.md`
- **`/ag2-a2a`** or request for **A2A server/client**: Read `commands/ag2-a2a.md`
- **`/ag2-ui`** or request for **AG-UI frontend**: Read `commands/ag2-ui.md`
- **`/ag2-debug`** or request for **debugging help**: Read `commands/ag2-debug.md`
- **`/ag2-code-executor`** or request for **local code execution**: Read `commands/ag2-code-executor.md`

**CRITICAL RULE:** Do not generate complex AG2 features from memory. Always read the associated command file in the `.agents/skills/ag2_project_creator/commands/` directory first for the exact v0.11+ boilerplate.

## 5. Post-Creation Actions

- Inform the user that the project has been bootstrapped using AG2 v0.11+ best practices.
- Give them brief instructions on how to install dependencies (e.g., `uv sync` or `uv pip install -e .`) and how to run `python main.py`.
