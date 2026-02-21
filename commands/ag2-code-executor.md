Genera un agente o configuración capaz de ejecutar código Python localmente de forma segura usando `LocalCommandLineCodeExecutor` (AG2 v0.9+).

Argumento opcional: nombre del archivo. Ejemplo: `/ag2-code-executor data_analyzer`.

## Instrucciones al agente

1. Pregunta al usuario:
   - ¿Qué tipo de código se va a ejecutar? (ej. scripts de Python de análisis de datos)
   - ¿Qué agente generará el código y quién lo ejecutará? (Normalmente hay un agente `coder` que escribe código y un `executor` que lo corre).
   - ¿Se necesita instalar alguna librería (ej. pandas, matplotlib)?

2. Genera el código siguiendo estríctamente estas **REGLAS DE SEGURIDAD CRÍTICAS**:
   - ¡NUNCA ejectues código en el directorio de trabajo principal del usuario! Debes aislar la ejecución en un directorio temporal usando `tempfile.TemporaryDirectory()`.
   - El agente ejecutor **NO DEBE** tener LLM activado. `llm_config=False`.
   - Se debe mantener activado el modo de aprobación humana `human_input_mode="ALWAYS"` a menos que el usuario explícitamente apruebe una automatización total con gran confianza.

3. Genera el archivo (ej. `agents/executor.py` o `workflows/code_flow.py`) con la siguiente plantilla base:

```python
import tempfile
import os
from autogen import ConversableAgent, LLMConfig
from autogen.coding import LocalCommandLineCodeExecutor

# 1. Crear un directorio temporal para aislar la ejecución
temp_dir = tempfile.TemporaryDirectory()

# 2. Configurar el LocalCommandLineCodeExecutor
executor = LocalCommandLineCodeExecutor(
    timeout=10,                      # Timeout de seguridad (segundos)
    work_dir=temp_dir.name,          # AISLAMIENTO: NUNCA usar './' directamente
)

# 3. Crear el agente ejecutor (SIN LLM)
code_executor_agent = ConversableAgent(
    "code_executor_agent",
    llm_config=False,  # CRÍTICO: Turn off LLM for execution
    code_execution_config={"executor": executor}, 
    human_input_mode="ALWAYS", # CRÍTICO: Safety first
)

# 4. Crear el agente desarrollador (CON LLM)
llm_config = LLMConfig(
    api_type="openai",
    model=os.environ.get("DEFAULT_MODEL", "gpt-4o"),
    api_key=os.environ["OPENAI_API_KEY"],
)

code_writer_agent = ConversableAgent(
    "code_writer_agent",
    system_message="""Eres un desarrollador experto en Python. 
    Resuelve la tarea escribiendo bloques de código Python empezando con ```python y terminando con ```.
    En el mismo bloque, asegúrate de hacer un `print()` de los resultados para que podamos verlos.
    Si la tarea requiere leer archivos, asume que están en el directorio actual.""",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

# 5. Ejemplo de cómo iniciar el flujo
def run_code_task(task: str):
    print(f"Directorio temporal configurado en: {temp_dir.name}")
    
    # El ejecutor es el proxy que "chatea" con el coder
    result = code_executor_agent.initiate_chat(
        code_writer_agent,
        message=task
    )
    
    # Imprimir archivos generados antes de limpiar
    print("Archivos generados:", os.listdir(temp_dir.name))
    
    # Limpiar el entorno temporal al final
    temp_dir.cleanup()
    return result

if __name__ == "__main__":
    run_code_task("Escribe un script de python que genere un scatter plot de matplotlib y lo guarde como scatter.png")
```

## Checklist antes de entregar

- [ ] ¿Usaste `tempfile.TemporaryDirectory()` para el `work_dir`?
- [ ] ¿`llm_config=False` en el ejecutor?
- [ ] ¿Usaste `LocalCommandLineCodeExecutor` (la API moderna) en lugar de la sintaxis deprecada antigua?
