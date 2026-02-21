Analiza y depura una conversación AG2 fallida o que no se comporta como se espera.

El usuario puede pegar el error, el historial de chat, o describir el comportamiento incorrecto.

## Instrucciones

Leer el código afectado y aplicar este checklist de diagnóstico:

---

### 1. Errores de API / imports

La única API soportada es v0.9+ (`initiate_group_chat`). Verificar:

```python
# ✅ CORRECTO — API v0.9+
from autogen.agentchat.group import (
    ContextVariables, ReplyResult,
    AgentTarget, AgentNameTarget, RevertToUserTarget, TerminateTarget, StayTarget,
    OnCondition, StringLLMCondition,
    OnContextCondition, ExpressionContextCondition, ContextExpression,
)
from autogen.agentchat.group.patterns import (
    DefaultPattern, AutoPattern, RoundRobinPattern, RandomPattern, ManualPattern
)
from autogen.agentchat import initiate_group_chat

# ✅ Registrar handoffs
agent.handoffs.add_llm_conditions([OnCondition(...)])
agent.handoffs.add_context_conditions([OnContextCondition(...)])
agent.handoffs.set_after_work(RevertToUserTarget())

# ❌ NO USAR — API antigua incompatible
# register_hand_off, initiate_swarm_chat, AfterWorkOption, SwarmAgent, SwarmResult
# Estos imports ya no deben existir en el proyecto (Swarm está deprecado)
```

---

### 2. Selección de agente incorrecta (GroupChat / AutoPattern)

- ¿Todos los agentes tienen `description` clara y diferenciada?
- ¿La `description` responde "cuándo invocar este agente"?
- ¿El `group_manager_args={"llm_config": ...}` está configurado en `AutoPattern`?
- ¿Los nombres de agentes son únicos?

---

### 3. Handoffs no se activan

**Para `OnContextCondition`:**

- ¿La variable existe en `ContextVariables` con el tipo correcto?
- La `ContextExpression` usa sintaxis `${variable}` — sin espacios extra
- Imprimir el estado del contexto justo antes del handoff para verificar
- `available=` es opcional pero puede bloquear el handoff si la condición es `False`

**Para `OnCondition` (LLM):**

- El `prompt=` de `StringLLMCondition` debe ser claro y específico
- ¿El agente LLM tiene acceso al contexto necesario para evaluar la condición?

---

### 4. Bucles infinitos / conversación que no termina

- ¿`set_after_work()` está configurado para todos los agentes?
- ¿`is_termination_msg` está definido y se activa?
- ¿`max_rounds` en `initiate_group_chat` está configurado?
- En Feedback Loop: ¿`iteration_count` se incrementa? ¿`max_iterations` está en `ContextVariables`?
- En Escalation: ¿`StayTarget()` puede causar un bucle infinito si la confianza nunca cambia?

---

### 5. Tools no se llaman o producen resultados incorrectos

- ¿La docstring de la tool es descriptiva y específica?
- ¿Los parámetros usan `Annotated[tipo, "descripción"]`?
- ¿El `caller` tiene `llm_config`? ¿El `executor` es el correcto?
- ¿`register_function` fue llamado con los agentes correctos?
- ¿`parallel_tool_calls=False` en `llm_config` si el orden importa?
- Si la tool retorna `ReplyResult`: ¿el agente destino en `target=` existe en el workflow?

---

### 6. `ContextVariables` no se actualiza

- ¿La función de tool recibe `context_variables: ContextVariables` como parámetro?
- ¿Se está mutando directamente `context_variables["clave"] = valor`?
- Si retorna `ReplyResult`: ¿se pasa `context_variables=context_variables` en él?
- ¿Es la misma instancia de `ContextVariables` que se pasó a `AutoPattern`?

---

### 7. Errores de LLM / credenciales

- ¿`load_dotenv()` se llama al inicio del script?
- ¿El modelo especificado existe y está disponible en la cuenta?
- `parallel_tool_calls=False` — requerido para algunos modelos en workflows secuenciales
- ¿`api_type` está especificado? (openai, anthropic, gemini...)

---

### 8. A2A / MCP

- `A2aRemoteAgent` solo soporta métodos **async** (`a_initiate_chat`, `a_run`)
- MCP: `nest_asyncio.apply()` es necesario en Jupyter o donde hay event loop activo
- MCP: verificar que el servidor MCP está corriendo antes de conectar el cliente
- `ClientSession(read, write, read_timeout_seconds=timedelta(seconds=30))` — timeout adecuado

---

## Salida esperada del diagnóstico

1. **Causa raíz**: qué está fallando exactamente
2. **Fix concreto**: el cambio de código para resolverlo
3. **Verificación**: qué loguear o qué output esperar para confirmar que funciona
