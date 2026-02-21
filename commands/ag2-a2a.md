Genera un servidor A2A para exponer un agente AG2 como microservicio y/o un cliente para consumir agentes remotos.

Argumento opcional: nombre del agente a exponer/consumir. Ejemplo: `/ag2-a2a coder` o `/ag2-a2a data_analyst`.

## Instrucciones

1. Pregunta al usuario:
   - ¿Quiere crear un **servidor** (exponer agente), un **cliente** (consumir agente remoto), o ambos?
   - Si servidor: ¿Qué agente AG2 exponer? ¿En qué puerto?
   - Si cliente: ¿URL del agente remoto? ¿Cómo integrarlo en el workflow?
   - ¿El agente remoto es AG2, Pydantic AI, LangGraph u otro framework con A2A?

2. Instalar dependencias:
```bash
uv add "ag2[openai]" uvicorn
```

3. Crear servidor A2A (`api/<nombre>_server.py`):

```python
import os
from dotenv import load_dotenv
from autogen import ConversableAgent, LLMConfig
from autogen.a2a import A2aAgentServer

load_dotenv()

llm_config = LLMConfig({
    "model": os.environ.get("DEFAULT_MODEL", "gpt-4o-mini"),
    "api_key": os.environ["OPENAI_API_KEY"],
})

agent = ConversableAgent(
    name="<nombre_agente>",
    system_message="""<rol detallado del agente>""",
    llm_config=llm_config,
)

server = A2aAgentServer(agent).build()

# Iniciar con: uvicorn api.<nombre>_server:server --port <puerto>
# Ejemplo:     uvicorn api.coder_server:server --port 8001
```

4. Crear cliente A2A (`agents/<nombre>_remote.py`):

```python
from autogen.a2a import A2aRemoteAgent

# Se comporta exactamente como un ConversableAgent local
# pero las llamadas van al servicio remoto via HTTP
<nombre>_remote = A2aRemoteAgent(
    url="http://localhost:<puerto>",
    name="<nombre_agente>",
)

# IMPORTANTE: A2aRemoteAgent solo soporta métodos asíncronos
# Usar a_initiate_chat() en lugar de initiate_chat()
# Usar a_run() en lugar de run()
```

5. Mostrar cómo usar el agente remoto en un workflow asíncrono:

```python
import asyncio
from autogen import ConversableAgent, LLMConfig
from agents.<nombre>_remote import <nombre>_remote

async def run_distributed_workflow(task: str):
    coordinator = ConversableAgent(
        name="coordinator",
        llm_config=llm_config,
        human_input_mode="NEVER",
        is_termination_msg=lambda m: "DONE" in m.get("content", ""),
    )

    # Usar el agente remoto igual que uno local
    await coordinator.a_initiate_chat(
        recipient=<nombre>_remote,
        message=task,
        max_turns=10,
    )

asyncio.run(run_distributed_workflow("tarea a delegar al agente remoto"))
```

6. Si hay múltiples agentes remotos, mostrar cómo combinarlos en un GroupChat asíncrono.

7. Crear un `docker-compose.yml` básico si el usuario quiere desplegar múltiples agentes A2A.

## Cuándo usar A2A vs import directo

| Situación | Usar |
|---|---|
| Mismo repo, mismo proceso | Import directo |
| Otro equipo / otro repo | **A2A** |
| Distintos lenguajes/frameworks | **A2A** |
| Escalar agentes independientemente | **A2A** |
| Contrato formal entre componentes | **A2A** |

## Notas
- A2A implementa el protocolo oficial: https://github.com/google/a2a
- `A2aRemoteAgent` es compatible con agentes de otros frameworks (Pydantic AI, LangGraph, etc.)
- **Solo métodos async**: `a_initiate_chat()`, `a_run()` — no hay versión síncrona
- Verificar que el servidor A2A esté corriendo antes de instanciar `A2aRemoteAgent`
- Para producción: añadir autenticación, health checks y retry logic
