"""Shared helpers for the four workflow roles."""

from __future__ import annotations

import json
import re
from collections.abc import Callable

import llm_client
from models import ResearchState

StepCallback = Callable[[str], None] | None

BASE_SYSTEM = (
    "You are one role in a market-research workflow. Return only one valid JSON object. "
    "Never invent facts, numbers or sources. All supplied evidence is illustrative sample "
    "data and must keep that label. Keep the brief short and evidence-based."
)


def serialize(value: object) -> object:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, list):
        return [serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: serialize(item) for key, item in value.items()}
    return value


def dump(value: object) -> str:
    return json.dumps(serialize(value), ensure_ascii=False, default=str)


def plain(claim: str) -> str:
    text = re.sub(r"^Sample data(?: placeholder)?:\s*", "", claim)
    return text[:1].upper() + text[1:] if text else text


def topic_text(scope: str) -> str:
    return scope if scope.lower().startswith("the ") else f"the {scope}"


def unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(item.strip() for item in items if item.strip()))


def try_llm(state: ResearchState, system: str, user: str) -> dict | None:
    try:
        return llm_client.call_json(system, user)
    except llm_client.LLMError as exc:
        state.log("System", f"LLM unavailable ({exc}); used deterministic fallback.")
        return None
