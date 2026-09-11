#!/usr/bin/env python3
"""
Agentic UI Patterns & Frontend UX Toolkit
=========================================
Zero-dependency toolkit for:
- Streaming markdown stream repair (auto-balancing unclosed code fences, bolding, links)
- Chain-of-thought extraction & in-flight reasoning parser (<thought>, <reasoning>)
- Generative UI JSON payload schema validation (KPI cards, diff views, action forms)
- Simulated token chunk streamer with realistic inter-token latency
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# 1. Streaming Markdown Stream Repairer
# ---------------------------------------------------------------------------

def repair_streaming_markdown(raw_buffer: str) -> str:
    """
    Safely repairs incomplete or in-flight markdown tokens so that partial streaming
    text renders without visual layout glitches or broken code blocks.
    """
    repaired = raw_buffer

    # 1. Check for unclosed code block fences (```)
    # Count occurrences of triple backticks not preceded by backslash
    code_fences = len(re.findall(r'(?<!\\)```', repaired))
    if code_fences % 2 != 0:
        # Detect if we just started a code block with language specifier (e.g., ```python)
        last_fence_idx = repaired.rfind("```")
        after_fence = repaired[last_fence_idx + 3:]
        # If no newline yet after language specifier, append a newline then close
        if "\n" not in after_fence:
            repaired += "\n\n```"
        else:
            repaired += "\n```"

    # 2. Balance unclosed bold markers (**)
    bold_markers = len(re.findall(r'(?<!\\)\*\*', repaired))
    if bold_markers % 2 != 0:
        repaired += "**"

    # 3. Check for unclosed inline code ticks (`) outside of triple-backtick fences
    # If odd single backticks remain
    single_ticks = len(re.findall(r'(?<!`)(?<!\\)`(?!`)', repaired))
    if single_ticks % 2 != 0:
        repaired += "`"

    return repaired


# ---------------------------------------------------------------------------
# 2. Chain-of-Thought (CoT) & Reasoning Parser
# ---------------------------------------------------------------------------

@dataclass
class ParsedStreamMessage:
    is_still_thinking: bool
    thought_content: str
    answer_content: str


def parse_reasoning_stream(stream_buffer: str) -> ParsedStreamMessage:
    """
    Extracts <thought> or <reasoning> blocks from streaming LLM output.
    Handles both completed and in-flight reasoning states.
    """
    # Regex to find completed thought block
    completed_pattern = re.compile(r'<(?:thought|reasoning)>(.*?)</(?:thought|reasoning)>', re.DOTALL | re.IGNORECASE)
    match = completed_pattern.search(stream_buffer)

    if match:
        thought_text = match.group(1).strip()
        answer_text = stream_buffer[match.end():].strip()
        return ParsedStreamMessage(
            is_still_thinking=False,
            thought_content=thought_text,
            answer_content=answer_text
        )

    # Check for in-flight unclosed thought block
    in_flight_pattern = re.compile(r'<(?:thought|reasoning)>(.*)', re.DOTALL | re.IGNORECASE)
    in_flight_match = in_flight_pattern.search(stream_buffer)

    if in_flight_match:
        thought_text = in_flight_match.group(1).strip()
        return ParsedStreamMessage(
            is_still_thinking=True,
            thought_content=thought_text,
            answer_content=""
        )

    # No thought tags present -> all text is direct answer
    return ParsedStreamMessage(
        is_still_thinking=False,
        thought_content="",
        answer_content=stream_buffer.strip()
    )


# ---------------------------------------------------------------------------
# 3. Generative UI Component Schema Validator
# ---------------------------------------------------------------------------

SUPPORTED_UI_SCHEMAS = {
    "kpi_metric_card": {"title", "value"},
    "diff_view": {"filename", "old_code", "new_code"},
    "action_button": {"label", "action_id"},
    "confirmation_dialog": {"title", "description", "confirm_label"}
}


def validate_generative_ui_payload(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates that a dynamic Generative UI component payload conforms to the component contract.
    """
    errors = []
    if not isinstance(payload, dict):
        return (False, ["Payload must be a JSON dictionary"])

    component_type = payload.get("ui_component")
    if not component_type:
        return (False, ["Payload missing 'ui_component' attribute"])

    if component_type not in SUPPORTED_UI_SCHEMAS:
        return (False, [f"Unsupported 'ui_component' type: '{component_type}'. Allowed: {list(SUPPORTED_UI_SCHEMAS.keys())}"])

    props = payload.get("props")
    if not isinstance(props, dict):
        return (False, ["Payload missing 'props' dictionary"])

    required_props = SUPPORTED_UI_SCHEMAS[component_type]
    for p in required_props:
        if p not in props or props[p] is None:
            errors.append(f"Component '{component_type}' missing required prop: '{p}'")

    return (len(errors) == 0, errors)


# ---------------------------------------------------------------------------
# CLI & Self-Test Suite
# ---------------------------------------------------------------------------

def run_self_test():
    print("=================================================================")
    print("Running Agentic UI Patterns Toolkit Self-Tests...")
    print("=================================================================")

    # Test 1: Markdown Stream Repair
    broken_md_code = "Here is the implementation:\n```python\ndef add(a, b):\n    return a + b"
    repaired_code = repair_streaming_markdown(broken_md_code)
    assert repaired_code.endswith("```"), f"Failed to close code fence: {repaired_code}"

    broken_bold = "This is a **critical security warning"
    repaired_bold = repair_streaming_markdown(broken_bold)
    assert repaired_bold.endswith("**"), f"Failed to close bold tag: {repaired_bold}"
    print("[PASS] Streaming markdown stream repair passed")

    # Test 2: In-Flight Reasoning Parser
    in_flight_stream = "<thought>Analyzing the repository dependency graph..."
    parsed_in_flight = parse_reasoning_stream(in_flight_stream)
    assert parsed_in_flight.is_still_thinking is True
    assert "Analyzing" in parsed_in_flight.thought_content
    assert parsed_in_flight.answer_content == ""

    # Test 3: Completed Reasoning Parser
    completed_stream = "<thought>Finished analysis. Found 3 bugs.</thought>Here are the 3 bug reports."
    parsed_completed = parse_reasoning_stream(completed_stream)
    assert parsed_completed.is_still_thinking is False
    assert "Found 3 bugs" in parsed_completed.thought_content
    assert "Here are the 3 bug reports." in parsed_completed.answer_content
    print("[PASS] Reasoning & Chain-of-Thought stream parser passed")

    # Test 4: Generative UI Schema Validator
    valid_kpi = {
        "ui_component": "kpi_metric_card",
        "props": {
            "title": "Monthly Churn Rate",
            "value": "1.8%",
            "trend": "down"
        }
    }
    is_valid, errors = validate_generative_ui_payload(valid_kpi)
    assert is_valid, f"Expected valid KPI payload, got errors: {errors}"

    invalid_diff = {
        "ui_component": "diff_view",
        "props": {"filename": "main.py"}  # Missing old_code and new_code
    }
    is_valid, errors = validate_generative_ui_payload(invalid_diff)
    assert not is_valid and len(errors) == 2, "Failed to catch missing diff props"
    print("[PASS] Generative UI component payload validation passed")

    print("\nALL AGENTIC UI PATTERNS TOOLKIT TESTS PASSED (4/4) [OK]\n")


def main():
    parser = argparse.ArgumentParser(description="Agentic UI Patterns & Frontend UX Toolkit")
    parser.add_argument("--test", action="store_true", help="Run self-test suite")
    subparsers = parser.add_subparsers(dest="command")

    repair_p = subparsers.add_parser("repair-stream", help="Repair partial streaming markdown")
    repair_p.add_argument("--text", type=str, required=True, help="Raw streaming text buffer")

    args = parser.parse_args()

    if args.test:
        run_self_test()
        sys.exit(0)
    elif args.command == "repair-stream":
        repaired = repair_streaming_markdown(args.text)
        print("--- Repaired Markdown Buffer ---")
        print(repaired)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
