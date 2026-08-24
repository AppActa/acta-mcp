"""OpenTelemetry helpers for ACTA MCP."""

from __future__ import annotations

import sys
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from functools import lru_cache
from typing import Any

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from acta_mcp.core.config import env_bool, env_str, set_default_env

_configured = False


def _is_enabled() -> bool:
    if "pytest" in sys.modules and not env_bool("ACTA_OBSERVABILITY_IN_TESTS", False):
        return False
    if not env_bool("ACTA_OBSERVABILITY_ENABLED", True):
        return False
    return any(
        env_str(name)
        for name in (
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
            "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT",
        )
    )


def configure_observability(default_service_name: str) -> bool:
    global _configured
    if _configured:
        return True
    if not _is_enabled():
        return False

    set_default_env("OTEL_SERVICE_NAME", default_service_name)
    set_default_env("OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf")

    resource = Resource.create(
        {
            "service.name": env_str("OTEL_SERVICE_NAME", default_service_name),
            "service.namespace": "acta",
            "deployment.environment": env_str("ACTA_ENV", "development"),
        }
    )

    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(tracer_provider)

    metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter())
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))

    _configured = True
    return True


def instrument_asgi_app(app: Any, *, service_name: str = "acta-mcp") -> Any:
    if not configure_observability(service_name):
        return app
    return OpenTelemetryMiddleware(app)


def _clean_attributes(attributes: Mapping[str, Any] | None) -> dict[str, Any]:
    if not attributes:
        return {}
    return {
        key: value
        for key, value in attributes.items()
        if value is not None and isinstance(value, str | int | float | bool)
    }


@contextmanager
def observed_span(name: str, attributes: Mapping[str, Any] | None = None) -> Iterator[Any]:
    if not _configured:
        yield None
        return

    with trace.get_tracer("acta.mcp").start_as_current_span(name) as span:
        for key, value in _clean_attributes(attributes).items():
            span.set_attribute(key, value)
        yield span


@lru_cache(maxsize=1)
def _meter():
    return metrics.get_meter("acta.mcp")


@lru_cache(maxsize=1)
def _tool_latency():
    return _meter().create_histogram(
        "acta_mcp_tool_latency_ms",
        unit="ms",
        description="Latencia de execucao das tools MCP do ACTA.",
    )


@lru_cache(maxsize=1)
def _tool_calls():
    return _meter().create_counter(
        "acta_mcp_tool_calls_total",
        description="Total de execucoes de tools MCP do ACTA.",
    )


def record_tool_call(tool_name: str, duration_ms: float, *, status: str) -> None:
    if not _configured:
        return
    attributes = {"tool": tool_name, "status": status}
    _tool_calls().add(1, attributes)
    _tool_latency().record(duration_ms, attributes)
