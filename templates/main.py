import os
from dotenv import load_dotenv

from autogen import UserProxyAgent
from autogen.agentchat import initiate_group_chat
from autogen.agentchat.group.patterns import AutoPattern
from autogen.agentchat.group import ContextVariables

from config.llm import llm_config
from agents.example_agent import assistant

# Configuración de observabilidad OpenTelemetry
from config.instrumentation import setup_tracing, apply_tracing_to_agent

load_dotenv()

def main():
    print("Iniciando sistema multi-agente AG2 (v0.11+)...")
    
    # 1. Habilitamos tracing
    tracer_provider = setup_tracing("ag2-mi-proyecto")
    
    # Contexto compartido entre agentes (estado global)
    context = ContextVariables(data={
        "task_completed": False
    })
    
    # Agente interactivo / ejecutor
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",  # Cambiar a "TERMINATE" si quieres confirmación humana antes de ejecutar tools
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: "TERMINATE" in x.get("content", "").upper(),
        code_execution_config={"use_docker": False},
        description="Representa al usuario. Ejecuta herramientas locales y termina el proceso cuando lee TERMINATE."
    )
    
    # 2. Aplicamos tracing a los agentes participantes
    apply_tracing_to_agent(assistant, tracer_provider)
    apply_tracing_to_agent(user_proxy, tracer_provider)

    # Patrón: Routing dinámico dictado por el LLM basado en las `description`
    pattern = AutoPattern(
        initial_agent=user_proxy,
        agents=[user_proxy, assistant], 
        user_agent=user_proxy,
        context_variables=context,
        group_manager_args={"llm_config": llm_config},
    )

    print("\\n--- Ejecutando GroupChat con AutoPattern ---")
    result, final_context, last_agent = initiate_group_chat(
        pattern=pattern,
        messages="Hola, por favor usa la herramienta para obtener el clima de Madrid y luego di TERMINATE.",
        max_rounds=15
    )

    print("\\n--- Contexto Final ---")
    print(final_context.to_dict())

if __name__ == "__main__":
    main()
