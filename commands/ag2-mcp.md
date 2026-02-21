Genera un servidor MCP y su cliente AG2 para integrar un sistema externo en el workflow multiagente.

Argumento opcional: nombre del sistema a integrar. Ejemplo: `/ag2-mcp base_de_datos` o `/ag2-mcp github_api`.

## Instrucciones

1. Pregunta al usuario:
   - ¿Qué sistema externo se quiere integrar? (base de datos, API REST, sistema de archivos, etc.)
   - ¿Qué operaciones/herramientas necesita exponer? (listar, consultar, crear, actualizar...)
   - ¿Qué modo de transporte usar? `stdio` (local), `sse` o `streamable-http` (remoto)
   - ¿Qué agente(s) AG2 van a usar estas herramientas?

2. Instalar dependencias si no están:
```bash
uv add "ag2[mcp]" mcp
```

3. Crea el servidor MCP (`mcp_servers/<nombre>.py`):

```python
import argparse
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("<NombreServidor>")

@mcp.tool()
def <nombre_operacion>(param: str) -> str:
    """
    Descripción detallada de la operación.
    El LLM leerá esta docstring para decidir cuándo llamar esta herramienta.
    """
    # implementación
    return resultado

# Añadir más @mcp.tool() según las operaciones necesarias
# Añadir @mcp.resource("esquema://{id}") para recursos accesibles

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("transport", choices=["stdio", "sse", "streamable-http"])
    mcp.run(transport=parser.parse_args().transport)
```

4. Crea el cliente AG2 (`workflows/<nombre>_mcp_client.py`):

```python
import asyncio
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from autogen import AssistantAgent, LLMConfig
from autogen.mcp import create_toolkit

load_dotenv()

async def run(task: str) -> None:
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_servers/<nombre>.py", "stdio"],
    )
    async with stdio_client(server_params) as (read, write), \
               ClientSession(read, write) as session:
        await session.initialize()

        toolkit = await create_toolkit(session=session)

        agent = AssistantAgent(
            name="agente_con_mcp",
            llm_config=LLMConfig(
                model=os.environ.get("DEFAULT_MODEL", "gpt-4o"),
                api_key=os.environ["OPENAI_API_KEY"],
            ),
        )
        toolkit.register_for_llm(agent)

        result = await agent.a_run(
            message=task,
            tools=toolkit.tools,
            max_turns=10,
            user_input=False,
        )
        await result.process()

if __name__ == "__main__":
    asyncio.run(run("tarea de ejemplo usando el sistema externo"))
```

5. Si el modo es SSE o streamable-http, generar también el script de inicio del servidor.

6. Muestra cómo integrar el toolkit MCP en un workflow GroupChat existente (DefaultPattern/AutoPattern).

## Notas
- Toda la API MCP en AG2 es **asíncrona** — el punto de entrada debe ser `asyncio.run()`
- `create_toolkit()` descubre automáticamente todas las tools del servidor
- Las docstrings de `@mcp.tool()` son lo que el LLM ve — escribirlas bien
- Un servidor MCP puede estar escrito en cualquier lenguaje (Node.js, Go, etc.)
- Recursos (`@mcp.resource`) son para datos que el agente puede leer, no ejecutar
- Buscar servidores MCP públicos en: https://github.com/modelcontextprotocol/servers
