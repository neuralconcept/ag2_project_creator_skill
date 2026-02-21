from autogen import AssistantAgent
from typing import Annotated

# Exportamos la configuración creada centralmente
from config.llm import llm_config

# Agente asistente configurado con directivas precisas
assistant = AssistantAgent(
    name="agente_experto",
    description="Útil para responder preguntas complejas y redactar código. Invocado automáticamente cuando se necesite expertice general.",
    system_message="""Eres un experto asistente. 
Instrucciones:
1. Responde de manera concisa y clara.
2. Si tienes que generar código, asegúrate de que esté bien documentado y siga las mejores prácticas.
""",
    llm_config=llm_config,
)

# Ejemplo de una herramienta que el agente puede usar
def obtener_clima(
    ciudad: Annotated[str, "El nombre de la ciudad donde consultar el clima"],
) -> str:
    """Obtiene el clima actual de una ciudad. 
    (Docstring leída por el LLM para saber qué hace la tool)"""
    return f"El clima en {ciudad} es soleado y 22°C."

# Registramos la herramienta en el agente
# 'caller' decide cuándo se usa, 'executor' es quien finalmente la ejecuta
from autogen import register_function
# NOTA: En un script real, 'executor' sería típicamente el UserProxyAgent.
# register_function(
#    obtener_clima, 
#    caller=assistant, 
#    executor=user_proxy, 
#    name="obtener_clima", 
#    description="Consigue el clima actual."
# )
