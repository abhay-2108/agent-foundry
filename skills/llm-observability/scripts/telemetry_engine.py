"""telemetry_engine.py
Production-grade, vendor-neutral LLM observability engine using OpenTelemetry
and OpenInference semantic conventions.

Supports exporting via standard OTLP (gRPC/HTTP) to:
- Arize Phoenix
- Langfuse
- Weights & Biases Weave
- Datadog / Honeycomb / Grafana Tempo
- Self-hosted OpenTelemetry Collectors
"""
from __future__ import annotations
import os
import time
import json
import logging
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode, Tracer
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource

# Standard pricing table ($ per 1K tokens: prompt, completion)
MODEL_PRICING_PER_1K = {
    "gpt-4o": (0.0025, 0.0100),
    "gpt-4o-mini": (0.00015, 0.0006),
    "claude-3-5-sonnet": (0.0030, 0.0150),
    "gemini-1.5-pro": (0.00125, 0.0050),
}

logger = logging.getLogger("llm_observability")


class LLMObservabilityManager:
    """Manages vendor-neutral tracing and metrics for AI agents and LLM calls."""

    def __init__(self, service_name: str = "ai-agent-service", environment: str = "production"):
        self.resource = Resource.create({
            "service.name": service_name,
            "deployment.environment": environment,
            "telemetry.sdk.name": "opentelemetry",
        })

        provider = TracerProvider(resource=self.resource)

        # Configure OTLP Exporter if endpoint is set; otherwise fallback to console/memory
        otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        if otlp_endpoint:
            try:
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
                exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
                provider.add_span_processor(BatchSpanProcessor(exporter))
                logger.info(f"Connected to OTLP collector at {otlp_endpoint}")
            except Exception as e:
                logger.warning(f"Failed to initialize OTLP exporter ({e}). Falling back to console.")
                provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        else:
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

        trace.set_tracer_provider(provider)
        self.tracer: Tracer = trace.get_tracer("llm-observability", "1.0.0")

    @staticmethod
    def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculates USD cost based on token counts and model pricing."""
        prompt_rate, completion_rate = MODEL_PRICING_PER_1K.get(model, (0.0, 0.0))
        cost = (prompt_tokens / 1000.0 * prompt_rate) + (completion_tokens / 1000.0 * completion_rate)
        return round(cost, 6)

    @staticmethod
    def sanitize_pii(text: str) -> str:
        """Redacts common sensitive data (SSN, credit cards, emails) before logging."""
        import re
        text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL_REDACTED]", text)
        text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[SSN_REDACTED]", text)
        text = re.sub(r"\b(?:\d{4}-){3}\d{4}\b", "[CARD_REDACTED]", text)
        return text

    @contextmanager
    def trace_agent_workflow(
        self,
        workflow_name: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Generator[trace.Span, None, None]:
        """Context manager tracing a high-level agent workflow or conversation turn."""
        attributes = {
            "openinference.span.kind": "AGENT",
            "agent.workflow.name": workflow_name,
        }
        if user_id:
            attributes["user.id"] = user_id
        if session_id:
            attributes["session.id"] = session_id
        if metadata:
            for k, v in metadata.items():
                attributes[f"metadata.{k}"] = str(v)

        with self.tracer.start_as_current_span(workflow_name, attributes=attributes) as span:
            start_time = time.perf_counter()
            try:
                yield span
                span.set_status(Status(StatusCode.OK))
            except Exception as exc:
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                raise
            finally:
                duration = time.perf_counter() - start_time
                span.set_attribute("agent.duration_seconds", round(duration, 4))

    @contextmanager
    def trace_llm_generation(
        self,
        span_name: str,
        model: str,
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Generator[Dict[str, Any], None, None]:
        """Context manager capturing model generation, token economics, and latency."""
        attributes = {
            "openinference.span.kind": "LLM",
            "gen_ai.system": model.split("-")[0] if "-" in model else "custom",
            "gen_ai.request.model": model,
            "gen_ai.request.temperature": temperature,
        }
        if system_prompt:
            attributes["gen_ai.prompt.system"] = self.sanitize_pii(system_prompt)
        if user_prompt:
            attributes["gen_ai.prompt.user"] = self.sanitize_pii(user_prompt)

        result_recorder: Dict[str, Any] = {
            "completion": "",
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "ttft_seconds": 0.0,
        }

        with self.tracer.start_as_current_span(span_name, attributes=attributes) as span:
            start_time = time.perf_counter()
            try:
                yield result_recorder
                span.set_status(Status(StatusCode.OK))
            except Exception as exc:
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                raise
            finally:
                duration = time.perf_counter() - start_time
                prompt_toks = result_recorder.get("prompt_tokens", 0)
                comp_toks = result_recorder.get("completion_tokens", 0)
                total_toks = prompt_toks + comp_toks
                cost = self.calculate_cost(model, prompt_toks, comp_toks)

                span.set_attribute("gen_ai.usage.prompt_tokens", prompt_toks)
                span.set_attribute("gen_ai.usage.completion_tokens", comp_toks)
                span.set_attribute("gen_ai.usage.total_tokens", total_toks)
                span.set_attribute("gen_ai.usage.cost_usd", cost)
                span.set_attribute("gen_ai.latency.total_seconds", round(duration, 4))

                if result_recorder.get("ttft_seconds"):
                    span.set_attribute("gen_ai.latency.ttft_seconds", result_recorder["ttft_seconds"])
                if result_recorder.get("completion"):
                    span.set_attribute("gen_ai.completion", self.sanitize_pii(result_recorder["completion"][:2000]))

    @contextmanager
    def trace_tool_execution(
        self,
        tool_name: str,
        tool_parameters: Optional[Dict[str, Any]] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """Context manager tracing deterministic tool invocations (APIs, DBs, search)."""
        attributes = {
            "openinference.span.kind": "TOOL",
            "tool.name": tool_name,
        }
        if tool_parameters:
            attributes["tool.parameters"] = json.dumps(tool_parameters)

        recorder: Dict[str, Any] = {"output": None}
        with self.tracer.start_as_current_span(f"tool:{tool_name}", attributes=attributes) as span:
            try:
                yield recorder
                span.set_status(Status(StatusCode.OK))
                if recorder.get("output") is not None:
                    span.set_attribute("tool.output", str(recorder["output"])[:1000])
            except Exception as exc:
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                raise


def log_evaluation_score(span: trace.Span, metric_name: str, score: float, rationale: str = "") -> None:
    """Logs an evaluation score onto an active span for regression tracking."""
    span.add_event(
        name="evaluation_result",
        attributes={
            "eval.metric_name": metric_name,
            "eval.score": score,
            "eval.rationale": rationale,
            "eval.timestamp": time.time(),
        }
    )


# Self-test demo execution
if __name__ == "__main__":
    telemetry = LLMObservabilityManager(service_name="multi-agent-system", environment="development")

    with telemetry.trace_agent_workflow("financial_research_agent", user_id="user_441", session_id="sess_abc123"):
        with telemetry.trace_tool_execution("query_stock_price", {"ticker": "NVDA"}) as tool_rec:
            tool_rec["output"] = {"price": 128.50, "currency": "USD"}

        with telemetry.trace_llm_generation(
            span_name="synthesize_market_summary",
            model="gpt-4o",
            system_prompt="You are a financial advisor assistant.",
            user_prompt="Summarize NVDA stock performance based on recent price of 128.50.",
        ) as llm_rec:
            llm_rec["completion"] = "NVIDIA (NVDA) is trading at $128.50 with strong quarterly growth."
            llm_rec["prompt_tokens"] = 320
            llm_rec["completion_tokens"] = 85
            llm_rec["ttft_seconds"] = 0.42

    print("Trace executed and recorded successfully.")
