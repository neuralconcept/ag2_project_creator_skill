Genera un workflow AG2 completo en `workflows/` mapeando la topología lógica elegida por el usuario a uno de los 5 patrones oficiales de `GroupChat`.

Argumento opcional: nombre del workflow. Ejemplo: `/ag2-workflow procesamiento_pedidos`.

## Cookbook de Patrones (Instrucciones al agente)

1. Muestra al usuario este Cookbook detallado y espera su elección de arquitectura:

### A) Context-Aware Routing (`AutoPattern`)

* **Caso de Uso**: Enrutar quejas o solicitudes dinámicamente a especialistas basándose en análisis de contenido (ej. asistentes multi-dominio, atención al cliente).
* **Información**: Hub-and-spoke. Un "Router" invisible (el LLM del GroupChat manager) extrae la intención y enruta al experto apropiado.
* **Implementación AG2**: Utiliza `AutoPattern` puro. El ruteo ocurre mágicamente si cada agente tiene un `description` extremadamente claro sobre "cuándo intervenir".

### B) Pipeline / Secuencial (`RoundRobinPattern`)

* **Caso de Uso**: Cadenas de procesamiento lineal (ej. Investigación → Borrador → Edición → Publicación; o Validación → Inventario → Pago → Envío).
* **Información**: Cada agente transforma la salida del anterior en un ciclo cerrado.
* **Implementación AG2**: Utiliza `RoundRobinPattern`. El orden en la lista `agents=[...]` dicta la secuencia estricta.

### C) Escalation (`DefaultPattern` + `ContextVariables`)

* **Caso de Uso**: Tiradas de atención (Chatbot barato → Humano/Médico → Especialista Senior). Tareas con complejidad variable que requieren escalar solo si la confianza es baja.
* **Información**: Agente básico intenta resolver. Si falla, pasa a intermedio, etc.
* **Implementación AG2**: Utiliza `DefaultPattern`. Usa respuestas estructuradas (Pydantic) donde el agente evalúa su `confianza` (1-10 escalar si < 8). Mapear las transiciones estrictamente mediante `OnContextCondition` analizando el contexto compartido.

### D) Hierarchical / Tree (`DefaultPattern`)

* **Caso de Uso**: Reportes complejos, desarrollo de productos con múltiples equipos, tomas de decisión enterprise.
* **Información**: Un Ejecutivo delega a Managers → Managers delegan a Especialistas. La información fluye hacia abajo en peticiones y hacia arriba en síntesis.
* **Implementación AG2**: Utiliza `DefaultPattern`. Crucial obligar a que los Especialistas reporten *siempre* al Manager configurando explícitamente `handoffs.set_after_work(AgentTarget(manager))`.

### E) Feedback Loop / Iterative (`DefaultPattern` o `AutoPattern`)

* **Caso de Uso**: Diseño iterativo, procesos de QA donde un evaluador manda al creador a corregir hasta que se apruebe.
* **Información**: Progreso en ciclos repetidos de evaluación y mejora.
* **Implementación AG2**: Requiere guardar "número de intentos" en `ContextVariables` y usar un `OnContextCondition` si se llega al máximo para forzar un fallback (ej. `RevertToUserTarget()`) y evitar un bucle de consumo de LLM infinito.

1. Preguntar también:
   * ¿Qué agentes participan? (nombres, roles)
   * ¿Qué estado global (estado predeterminado para ContextVariables) necesita inicializarse?
   * **Asistencia Humana (HITL)**: ¿`NEVER` (Autónomo), `TERMINATE` (Aprobación final) o `ALWAYS` (Manual)?

2. Generar `workflows/<nombre>.py` usando siempre la **API `initiate_group_chat`**:

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

from config.llm import llm_config

def run(task: str, verbose: bool = False) -> dict:
    """Ejecuta el workflow <nombre> para la tarea dada."""

    # 1. ESTADO COMPARTIDO (CRÍTICO)
    context = ContextVariables(data={
        # Define aquí métricas si es un loop (ej. "intentos": 0) o banderas ("aprobado": False)
    })

    # 2. DEFINIR AGENTES
    # Recuerda: Si usas AutoPattern, la `description` define quién habla.
    agent_1 = ConversableAgent(
        name="...",
        description="...",
        system_message="...",
        llm_config=llm_config
    )
    # ...

    # El agente que representa al humano
    # IMPORTANTE: Configurar HITL aquí (NEVER, TERMINATE o ALWAYS)
    user_proxy = ConversableAgent(
        name="user_proxy",
        human_input_mode="TERMINATE",  # Cambia esto según lo que pida el usuario
        is_termination_msg=lambda m: "TERMINATE" in m.get("content", "")
    )

    # 3. DEFINIR HANDOFFS (OPCIONAL, SOLO SI ES DefaultPattern)
    # agent_1.handoffs.add_llm_conditions(...)

    # 4. INSTANCIAR EL PATRÓN ELEGIDO (El recomendado en la tabla)
    pattern = AutoPattern(    # o DefaultPattern / RoundRobinPattern
        initial_agent=agent_1,
        agents=[agent_1, ...],
        user_agent=user_proxy,
        context_variables=context,
        group_manager_args={"llm_config": llm_config}, # Solo para AutoPattern
    )

    # 5. INICIAR EL CHAT
    result, final_context, last_agent = initiate_group_chat(
        pattern=pattern,
        messages=task,
        max_rounds=20,
    )

    return {
        "summary": result.summary,
        "context": final_context.to_dict(),
    }

if __name__ == "__main__":
    r = run("tarea de ejemplo")
    print(r["summary"])
```

## Checklist Crítico para Entregar

* [ ] No usaste Swarm (está deprecado). Usaste `DefaultPattern` + `Handoffs` si había rutas rígidas.
* [ ] Has mapeado la topología lógica elegida a su *Patrón AG2 Oficial* real.
* [ ] `parallel_tool_calls=False` en el `LLMConfig` si el workflow debe ser estricto secuencialmente.
* [ ] En un *Feedback Loop*, definiste al menos un `ContextVariable` para evitar bucles infinitos (límite de iteraciones).
