"""Optional OpenAI-compatible LLM client (standard library only)."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request

from dotenv import load_dotenv

load_dotenv()


class LLMError(RuntimeError):
    pass


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def use_llm() -> bool:
    """auto: use the LLM only when a key exists; sample: never; llm: require a key."""

    mode = _env("RESEARCH_MODE", "auto").lower()
    key = _env("OPENAI_API_KEY")
    if mode == "sample":
        return False
    if not key:
        if mode == "llm":
            raise LLMError("RESEARCH_MODE=llm but OPENAI_API_KEY is empty. Add a key to .env or use sample mode.")
        return False
    return True


# (is_configured removed; use_llm covers runtime mode)


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise LLMError("Model response did not contain a JSON object.")
    try:
        result = json.loads(text[start : end + 1])
    except json.JSONDecodeError as exc:
        raise LLMError(f"Could not parse model JSON: {exc}") from exc
    if not isinstance(result, dict):
        raise LLMError("Model JSON was not an object.")
    return result


def _chat(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    base_url = _env("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    payload = {
        "model": _env("OPENAI_MODEL", "gpt-4o-mini"),
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {_env('OPENAI_API_KEY')}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise LLMError(f"LLM request failed (HTTP {exc.code}): {detail}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise LLMError(f"LLM request failed: {exc}") from exc

    try:
        content = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError("Unexpected response shape from the LLM endpoint.") from exc
    if isinstance(content, list):
        content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
    return str(content).strip()


def call_text(system_prompt: str, user_prompt: str) -> str:
    """Call the configured chat-completions endpoint and return plain text."""

    text = _chat(system_prompt, user_prompt, temperature=0.7)
    if not text:
        raise LLMError("Model returned an empty response.")
    return text


def call_json(system_prompt: str, user_prompt: str) -> dict:
    """Call the configured chat-completions endpoint and return a parsed JSON object."""

    return _extract_json(_chat(system_prompt, user_prompt, temperature=0.2))
