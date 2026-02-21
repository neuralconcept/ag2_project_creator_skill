import os
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from autogen.opentelemetry import instrument_agent, instrument_llm_wrapper

def setup_tracing(service_name: str = "ag2-multi-agent-system"):
    """
    Configura OpenTelemetry para trazar la ejecución de agentes y llamadas a LLMs.
    En un entorno de producción, puedes cambiar ConsoleSpanExporter por un exporter OTLP.
    """
    resource = Resource.create({"service.name": service_name})
    tracer_provider = TracerProvider(resource=resource)
    
    # Exportar trazas a consola si está habilitado en el .env
    if os.environ.get("TRACING_ENABLED", "").lower() == "true":
        tracer_provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    
    trace.set_tracer_provider(tracer_provider)
    instrument_llm_wrapper(tracer_provider=tracer_provider)
    
    return tracer_provider

def apply_tracing_to_agent(agent, tracer_provider):
    """
    Aplica instrumentación a un agente individual para extraer token usage, 
    coste y duración de llamadas.
    """
    instrument_agent(agent, tracer_provider=tracer_provider)
