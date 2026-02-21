Genera un workflow GroupChat AG2 basado en los 5 patrones oficiales (API v0.9+).

Argumento opcional: nombre del workflow. Ejemplo: `/ag2-groupchat analisis_documentos`.

## Instrucciones al agente

1. Pregunta al usuario (si no lo especificó antes):
    * Objetivo del GroupChat
    * Agentes participantes (nombres y roles)
    * **Método de orquestación deseado**:
        * `AutoPattern` — (Recomendado) El LLM lee las descripciones para decidir el turno.
        * `DefaultPattern` — Rutas rígidas y condiciones predefinidas (Sin LLM).
        * `RoundRobinPattern` — Turnos secuenciales estrictos.
        * `RandomPattern` — Turnos aleatorios.
        * `ManualPattern` — Un humano decide quién habla.
    * **Asistencia Humana (HITL)**:
        * `NEVER` — Autonomía total (por defecto).
        * `TERMINATE` — Aprobación humana final (el script se pausa al acabar y espera confirmación).
        * `ALWAYS` — Control total manual o para ejecutar código peligroso.

2. Genera `workflows/<nombre>.py` utilizando siempre la API `initiate_group_chat`.

### Ejemplo base (Plantilla)

```python
import os
from dotenv import load_dotenv
from autogen import ConversableAgent, LLMConfig
from autogen.agentchat import initiate_group_chat
from autogen.agentchat.group import (
    ContextVariables, ReplyResult, RevertToUserTarget, 
    AgentTarget, OnCondition, StringLLMCondition,
    OnContextCondition, ExpressionContextCondition, ContextExpression
)
from autogen.agentchat.group.patterns import (
    AutoPattern, DefaultPattern, RoundRobinPattern,
    RandomPattern, ManualPattern
)

load_dotenv()

# Inicialización obligatoria de LLMConfig
llm_config = LLMConfig(
    api_type="openai",
    model=os.environ.get("DEFAULT_MODEL", "gpt-4o"),
    api_key=os.environ["OPENAI_API_KEY"],
    temperature=0.0,
    parallel_tool_calls=False,
)

def run_groupchat(task: str) -> dict:
    context = ContextVariables(data={"task_completed": False})

    # IMPORTANTE: Definir el "description" es CRÍTICO para AutoPattern
    agent_a = ConversableAgent(
        name="agent_a",
        description="Experto en X. Interviene cuando el usuario pregunta sobre X.",
        system_message="...",
        llm_config=llm_config
    )
    
    agent_b = ConversableAgent(
        name="agent_b",
        description="Especialista en Y.",
        system_message="...",
        llm_config=llm_config
    )

    # El agente representante del humano
    # IMPORTANTE: Configurar HITL aquí (NEVER, TERMINATE o ALWAYS)
    user = ConversableAgent(
        name="user", 
        human_input_mode="TERMINATE",  # Cambia esto según lo que pida el usuario
        is_termination_msg=lambda m: "TERMINATE" in m.get("content", "")
    )
```

### Inyección de Patrones

Elige el patrón según la topología que se necesite e insértalo en la plantilla anterior:

#### A) `AutoPattern` (Ruteo Inteligente)

Úsalo cuando quieras que un "Manager" invisible (LLM) analice la conversación y rote el turno al agente cuyo `description` mejor encaje.

```python
    pattern = AutoPattern(
        initial_agent=user,
        agents=[user, agent_a, agent_b],
        user_agent=user,
        context_variables=context,
        group_manager_args={"llm_config": llm_config} # LLM requerido
    )
```

#### B) `DefaultPattern` (Ruteo Rígido / Máquina de Estados)

Úsalo cuando conozcas **exactamente** la ruta de la conversación y no quieras malgastar tokens de LLM en ruteo. Requiere `Handoffs` explícitos.

```python
    # Definimos las rutas estáticas
    agent_a.handoffs.add_llm_conditions([
        OnCondition(
            target=AgentTarget(agent_b),
            condition=StringLLMCondition(prompt="Si la tarea X terminó, transfiere a B.")
        )
    ])
    agent_b.handoffs.set_after_work(RevertToUserTarget())

    pattern = DefaultPattern(
        initial_agent=agent_a,
        agents=[agent_a, agent_b],
        user_agent=user,
        context_variables=context
    )
```

#### C) `RoundRobinPattern` (Secuencial estricto)

Úsalo para flujos de procesamiento en cadena (Pipeline). A habla, luego B, luego C.

```python
    pattern = RoundRobinPattern(
        initial_agent=agent_a,
        agents=[agent_a, agent_b, user], # El orden de esta lista dicta los turnos
        user_agent=user,
        context_variables=context
    )
```

#### D) Ejecución Final (Para todos los patrones)

```python
    result, final_context, last_agent = initiate_group_chat(
        pattern=pattern,
        messages=task,
        max_rounds=20,
    )
    return {"summary": result.summary, "context": final_context.to_dict()}
```

## Reglas Críticas

* **NUNCA usar Swarm.** Está deprecado en v0.9+. Usa `DefaultPattern` con Handoffs para simular el comportamiento antiguo de Swarm.

* **NUNCA usar `GroupChatManager` instanciado a mano** para comportamientos "Organic" como en versiones anteriores. En su lugar, usa `AutoPattern`.
