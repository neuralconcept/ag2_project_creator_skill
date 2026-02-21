# AG2 Multi-Agent Project

Este proyecto ha sido generado utilizando las mejores prácticas de **AG2 (AutoGen)** (API v0.11+).

## Estructura del Proyecto

* `main.py`: Punto de entrada del sistema. Inicia un `GroupChat` usando el patrón `AutoPattern` o orquestaciones basadas en reglas.
* `config/`: Contiene `llm.py` con la configuración centralizada de los modelos LLM (temperatura, API keys).
* `agents/`: Definición de cada agente (`ConversableAgent`, `AssistantAgent`, etc.). Cada agente debe exportarse desde aquí.
* `tools/`: Funciones regulares que se pueden conectar a los agentes mediante `autogen.register_function`.
* `workflows/`: Orquestaciones modulares que interconectan múltiples agentes para resolver flujos específicos (ej: pipeline complejo, escalamiento).
* `mcp_servers/`: Servidores locales utilizando el **Model Context Protocol (MCP)** mediante `FastMCP`. Se utilizan para proveer a los agentes acceso directo a tu entorno, bases de datos o APIs externas.

## Primeros Pasos

1. Asegúrate de tener `uv` instalado, y ejecuta `uv sync` para instalar las dependencias (`ag2`, `mcp`, `pydantic`, etc.).
2. Copia el archivo `.env.example` a un nuevo archivo llamado `.env`.
3. Completa tus claves de API dentro de `.env`.
4. Ejecuta el archivo principal para iniciar el sistema:

```bash
uv run python main.py
```
