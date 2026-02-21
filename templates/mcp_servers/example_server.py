import argparse
import random
from mcp.server.fastmcp import FastMCP

# Creamos un servidor MCP (Model Context Protocol) utilizando FastMCP.
# Este script se ejecuta como un proceso aislado y se expone por stdio u HTTP/SSE.
mcp = FastMCP("ExampleServer")

@mcp.tool()
def generar_numero_aleatorio(rango_min: int, rango_max: int) -> str:
    """
    IMPORTANTE: Esta docstring es leída por el LLM.
    Genera un número aleatorio entre rango_min y rango_max. Útil para demostraciones.
    """
    resultado = random.randint(rango_min, rango_max)
    return f"El número generado en este servidor MCP es: {resultado}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Permitimos elegir correrlo en consola local (stdio) o mediante streaming web (sse)
    parser.add_argument("transport", choices=["stdio", "sse", "streamable-http"], default="stdio", nargs="?")
    args = parser.parse_args()
    
    print(f"Iniciando MCP ExampleServer via {args.transport}...")
    mcp.run(transport=args.transport)
