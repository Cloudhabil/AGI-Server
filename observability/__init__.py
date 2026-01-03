import json
import logging
import os
from typing import Optional, Any, cast

from fastapi import FastAPI
try:
    from opentelemetry import trace
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.logging import LoggingInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
except ImportError:  # pragma: no cover - optional dependency
    trace = None
    FastAPIInstrumentor = cast(Any, None)
    LoggingInstrumentor = cast(Any, None)
    TracerProvider = cast(Any, None)
    BatchSpanProcessor = cast(Any, None)
    OTLPSpanExporter = cast(Any, None)
    Resource = cast(Any, None)


def setup(service_name: str, app: Optional[FastAPI] = None) -> None:
    """Configure OpenTelemetry tracing and JSON logging.

    Parameters
    ----------
    service_name:
        Name reported to observability backends.
    app:
        Optional FastAPI application to instrument.
    """
    if trace is None:
        logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
        return
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT")
    if endpoint:
        provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(endpoint=endpoint, insecure=True)
            )
        )
    trace.set_tracer_provider(provider)

    if app is not None:
        FastAPIInstrumentor.instrument_app(app)

    LoggingInstrumentor().instrument(set_logging_format=False)

    class JSONFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            span = trace.get_current_span()
            ctx = span.get_span_context()
            payload = {
                "level": record.levelname,
                "message": record.getMessage(),
                "trace_id": f"{ctx.trace_id:032x}",
                "span_id": f"{ctx.span_id:016x}",
                "service": service_name,
            }
            if record.exc_info:
                payload["exc_info"] = self.formatException(record.exc_info)
            return json.dumps(payload)

    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), handlers=[handler], force=True)
