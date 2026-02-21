import os
from dotenv import load_dotenv
from autogen import LLMConfig

load_dotenv()

# Configuración básica con fallback a modelo "mini" si es necesario
# parallel_tool_calls=False es recomendado en flujos secuenciales
llm_config = LLMConfig(
    config_list=[
        {
            "api_type": "openai", 
            "model": os.environ.get("DEFAULT_MODEL", "gpt-4o-mini"), 
            "api_key": os.environ.get("OPENAI_API_KEY", "")
        },
    ],
    temperature=0.0,
    parallel_tool_calls=False,
)
