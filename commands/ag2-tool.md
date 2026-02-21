Genera una herramienta (tool function) para registrar en agentes AG2.

Argumento opcional: nombre/descripción de la herramienta. Ejemplo: `/ag2-tool buscar_documentos`.

## Instrucciones

1. Pregunta al usuario:
   - ¿Qué hace la herramienta?
   - ¿Qué parámetros recibe?
   - ¿Necesita acceder/modificar `ContextVariables`?
   - ¿Debe hacer handoff a otro agente al terminar? (retornar `ReplyResult`)
   - ¿Qué agente la **llama** (caller con llm_config) y cuál la **ejecuta** (executor)?

2. Crea la función en `tools/<nombre>_tools.py`:

```python
from typing import Annotated
from autogen.agentchat.group import ContextVariables, ReplyResult, AgentTarget

def <nombre_tool>(
    param1: Annotated[str, "Descripción del parámetro 1 — el LLM la lee"],
    param2: Annotated[int, "Descripción del parámetro 2"],
    context_variables: ContextVariables,   # solo si necesita estado compartido
) -> ReplyResult:  # o -> str si no hace handoff
    """
    Descripción completa: qué hace, cuándo debe llamarse, qué produce.
    El LLM usa esta docstring para decidir si llamar la herramienta.
    Ser específico: cuándo usarla, qué retorna, efectos en el estado.
    """
    resultado = ...  # implementación

    # Actualizar contexto si aplica
    context_variables["ultimo_resultado"] = resultado
    context_variables["etapa_completada"] = True

    # Opción A: solo retornar el resultado (sin handoff)
    return str(resultado)

    # Opción B: retornar resultado + handoff explícito a otro agente
    return ReplyResult(
        message=f"Resultado: {resultado}",
        target=AgentTarget(siguiente_agente),   # instancia del agente destino
        # o: target=AgentNameTarget("nombre_agente")  # por nombre
        context_variables=context_variables,
    )
```

3. Registrar con `register_function`:

```python
from autogen import register_function
from tools.<nombre>_tools import <nombre_tool>

register_function(
    <nombre_tool>,
    caller=agente_llm,       # AssistantAgent o ConversableAgent con llm_config
    executor=agente_proxy,   # UserProxyAgent o el mismo agente caller
    name="<nombre_tool>",
    description="Descripción concisa de cuándo usar esta herramienta.",
)
```

## Notas críticas
- **Docstring** = lo que el LLM ve para decidir si usar la tool
- **`Annotated[tipo, "desc"]`** = descripción de cada parámetro para el LLM
- `context_variables` se inyecta automáticamente si aparece como parámetro
- `ReplyResult` permite hacer handoffs desde dentro de una tool (útil en Pipeline)
- El `caller` DEBE tener `llm_config`; el `executor` puede no tenerlo
- Retornar siempre `str` o `ReplyResult` — no objetos complejos no serializables
- Efectos secundarios: documentarlos en el docstring, loguearlos en ejecución
