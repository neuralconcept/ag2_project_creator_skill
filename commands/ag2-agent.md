Genera un nuevo agente AG2 en `agents/`.

Argumento opcional: nombre y rol. Ejemplo: `/ag2-agent researcher` o `/ag2-agent "validador de facturas"`.

## Instrucciones

1. Si el usuario no especificó, preguntar:
   - Nombre del agente (snake_case para el archivo)
   - Rol/propósito en 1-2 frases
   - Tipo: `AssistantAgent` (razona con LLM), `UserProxyAgent` (ejecuta código/tools), o Reference Agent
   - ¿Necesita herramientas? ¿Cuáles?
   - ¿En qué patrón participará? (Pipeline, GroupChat, Hierarchical...)
   - ¿Necesita `UpdateSystemMessage` para prompt dinámico?

2. Para **agente custom**, crear `agents/<nombre>.py`:

```python
import os
from autogen import ConversableAgent, LLMConfig, UpdateSystemMessage
from autogen.agentchat.group import (
    ContextVariables, ReplyResult, AgentTarget, RevertToUserTarget,
    OnCondition, StringLLMCondition,
    OnContextCondition, ExpressionContextCondition, ContextExpression,
)
from config.llm import llm_config

<nombre> = ConversableAgent(
    name="<nombre>",
    description="<1 línea precisa: cuándo y para qué invocar este agente>",
    llm_config=llm_config,
    system_message="<rol, restricciones, formato de respuesta esperado>",

    # Opcional: prompt que se actualiza con ContextVariables antes de cada respuesta
    # update_agent_state_before_reply=[
    #     UpdateSystemMessage("Usuario: {user_name}. Iteración: {iteration_count}.")
    # ],
)

# Opcional: handoffs
# <nombre>.handoffs.add_llm_conditions([
#     OnCondition(
#         target=AgentTarget(otro_agente),
#         condition=StringLLMCondition(prompt="Cuándo transferir a otro_agente"),
#     )
# ])
# <nombre>.handoffs.set_after_work(RevertToUserTarget())
```

3. Para **Reference Agent**, usar el agente preexistente apropiado:

```python
# WebSurferAgent — información web en tiempo real
from autogen.agents.experimental import WebSurferAgent
agent = WebSurferAgent(name="web_researcher", web_tool="browser_use",
                       web_tool_kwargs={"browser_config": {"headless": True}},
                       llm_config=llm_config,
                       description="Navega la web para información actualizada.")

# DocAgent — RAG sobre documentos
from autogen.agents.experimental import DocAgent
agent = DocAgent(name="doc_analyst", llm_config=llm_config,
                 description="Responde preguntas sobre documentos (PDF, DOCX, HTML, CSV...)")

# ReasoningAgent — razonamiento estructurado
from autogen import ReasoningAgent
agent = ReasoningAgent(name="deep_thinker", llm_config=llm_config,
                       reason_config={"method": "beam_search", "beam_size": 3, "max_depth": 4},
                       description="Resolución sistemática de problemas complejos.")

# DeepResearchAgent — investigación profunda
from autogen.agents.experimental import DeepResearchAgent
agent = DeepResearchAgent(name="researcher", llm_config=llm_config,
                           description="Investiga temas en profundidad consultando múltiples fuentes.")

# CaptainAgent — orquestador autónomo (requiere ag2[captainagent])
from autogen.agentchat.contrib.captainagent import CaptainAgent
agent = CaptainAgent(name="captain", llm_config=llm_config,
                     agent_config_save_path="./captain_agents/")

# WikipediaAgent — conocimiento general
from autogen.agents.experimental import WikipediaAgent
agent = WikipediaAgent(name="wiki", llm_config=llm_config,
                       description="Consulta Wikipedia para definiciones y conocimiento verificado.")
```

4. Actualizar `agents/__init__.py` para exportar el agente.

5. Crear `config/llm.py` si no existe:
```python
import os
from autogen import LLMConfig
llm_config = LLMConfig(
    api_type="openai",
    model=os.environ.get("DEFAULT_MODEL", "gpt-4o"),
    api_key=os.environ["OPENAI_API_KEY"],
    temperature=0.0,
    parallel_tool_calls=False,
)
```

## Notas clave
- `description` responde: "¿cuándo tiene sentido pedirle algo a este agente?"
- En GroupChat v0.9 (`AutoPattern`): description es el único criterio de selección si no hay handoffs
- Si participa en un workflow con handoffs: configurar `handoffs.set_after_work()` siempre
- `UpdateSystemMessage` es útil para agentes que necesitan saber el estado actual del workflow
