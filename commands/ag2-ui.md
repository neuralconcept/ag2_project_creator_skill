Genera un endpoint FastAPI con AG-UI para conectar un agente AG2 a un frontend web.

Argumento opcional: nombre del agente/servicio. Ejemplo: `/ag2-ui soporte_cliente`.

## Instrucciones

1. Pregunta al usuario:
   - ¿Qué agente AG2 exponer al frontend? (nuevo o existente)
   - ¿Necesita autenticación en el endpoint?
   - ¿Necesita pasar contexto de usuario (user_id, session_id) al agente?
   - ¿Necesita herramientas de frontend (Human-in-the-Loop, Generative UI)?
   - ¿Puerto y ruta del endpoint?

2. Instalar dependencias:
```bash
uv add "ag2[ag-ui]" fastapi uvicorn python-dotenv
```

3. Crear el servidor AG-UI (`api/<nombre>_ui.py`):

```python
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from autogen import ConversableAgent, LLMConfig
from autogen.ag_ui import AGUIStream, RunAgentInput

load_dotenv()

# --- Agente AG2 ---
agent = ConversableAgent(
    name="<nombre_agente>",
    system_message="""<rol e instrucciones del agente>""",
    llm_config=LLMConfig(
        model=os.environ.get("DEFAULT_MODEL", "gpt-4o-mini"),
        api_key=os.environ["OPENAI_API_KEY"],
    ),
)

# Registrar tools Python normales si el agente las necesita:
# register_function(mi_tool, caller=agent, executor=agent, ...)

# --- Stream AG-UI ---
stream = AGUIStream(agent)

# --- FastAPI app ---
app = FastAPI(title="<Nombre> AG-UI Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ajustar en producción
    allow_methods=["*"],
    allow_headers=["*"],
)

# Opción A: montaje directo (sin autenticación)
app.mount("/chat", stream.build_asgi())

# Opción B: con autenticación y contexto de usuario
@app.post("/chat/secure")
async def run_agent(
    message: RunAgentInput,
    authorization: str = Header(...),
) -> StreamingResponse:
    token = authorization.removeprefix("Bearer ").strip()
    if token != os.environ.get("API_TOKEN", ""):
        raise HTTPException(status_code=401, detail="Token inválido")

    event_stream = stream.dispatch(
        message,
        context={
            "user_id": message.thread_id,
            # Añadir cualquier metadata de usuario que el agente deba conocer
        },
    )
    return StreamingResponse(event_stream, media_type="text/event-stream")

@app.get("/health")
def health():
    return {"status": "ok"}

# Iniciar: uvicorn api.<nombre>_ui:app --port 8000 --reload
```

4. Si hay un workflow multiagente (GroupChat, Pipeline, etc.) en lugar de un agente simple:

```python
# Usar el agente orquestador como punto de entrada AG-UI
# El agente inicial del patrón (DefaultPattern/AutoPattern) es el que se expone
from workflows.mi_workflow import coordinator_agent

stream = AGUIStream(coordinator_agent)
```

5. Mostrar cómo ejecutar:
```bash
uvicorn api.<nombre>_ui:app --port 8000 --reload
# El frontend AG-UI compatible conecta a: http://localhost:8000/chat
```

6. Sugerir un frontend compatible con AG-UI:
- CopilotKit (React): https://docs.copilotkit.ai
- ag-ui-protocol playground: para testing local

## Notas clave
- AG-UI usa **Server-Sent Events (SSE)** para streaming en tiempo real
- `stream.dispatch()` acepta `context={}` que llega al agente como `ContextVariables`
- Las **backend tools** (funciones Python) se ejecutan en el servidor — el frontend las ve como acciones
- Las **frontend tools** (HITL, Generative UI) requieren soporte explícito en el cliente frontend
- En producción: usar HTTPS, autenticación JWT, y rate limiting
- Para múltiples agentes/workflows: crear múltiples endpoints montados en rutas diferentes
