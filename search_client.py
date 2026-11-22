"""Optional web-search adapter. Returns labelled web findings or raises SearchError."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from dotenv import load_dotenv

from models import Finding, ResearcherOutput, Source

load_dotenv()


class SearchError(RuntimeError):
    pass


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def is_configured() -> bool:
    provider = _env("SEARCH_PROVIDER", "auto").lower()
    if provider in {"", "auto", "tavily"}:
        return bool(_env("TAVILY_API_KEY"))
    if provider == "none":
        return False
    return bool(_env("SEARCH_API_KEY") or _env("TAVILY_API_KEY"))


def search(query: str, max_results: int = 5) -> ResearcherOutput:
    provider = _env("SEARCH_PROVIDER", "auto").lower()
    if provider == "none":
        raise SearchError("Web search disabled by SEARCH_PROVIDER=none.")
    if provider in {"", "auto", "tavily"}:
        return _search_tavily(query, max_results=max_results)
    raise SearchError(f"Unsupported SEARCH_PROVIDER={provider!r}. Use auto, tavily, or none.")


def _search_tavily(query: str, max_results: int = 5) -> ResearcherOutput:
    api_key = _env("TAVILY_API_KEY")
    if not api_key:
        raise SearchError("TAVILY_API_KEY is empty.")

    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "max_results": max(1, min(max_results, 8)),
        "include_answer": False,
        "include_raw_content": False,
    }
    request = urllib.request.Request(
        "https://api.tavily.com/search",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise SearchError(f"Web search failed (HTTP {exc.code}): {detail}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise SearchError(f"Web search failed: {exc}") from exc

    results = body.get("results", [])
    if not isinstance(results, list) or not results:
        raise SearchError("Web search returned no results.")

    findings: list[Finding] = []
    for item in results[:max_results]:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "Web result").strip()
        url = str(item.get("url") or "").strip()
        content = str(item.get("content") or "").strip()
        if not content:
            continue
        claim = content.replace("\n", " ").strip()
        if len(claim) > 320:
            claim = claim[:317].rstrip() + "..."
        findings.append(
            Finding(
                category=_guess_category(claim),
                claim=f"Web search: {claim}",
                source=Source(
                    title=title,
                    kind="Web search",
                    url=url,
                    note="Retrieved via Tavily web search; verify before decisions.",
                ),
            )
        )

    if not findings:
        raise SearchError("Web search results could not be parsed.")

    return ResearcherOutput(
        findings=findings,
        missing_information=[
            "Web results may be incomplete, outdated, or biased; verify key facts",
            "No primary market-size or financial validation was performed",
            "Competitor and market-share claims should be cross-checked with primary sources",
        ],
        data_origin="Live web search via Tavily (external sources; verify before use)",
    )


def _guess_category(text: str) -> str:
    lowered = text.lower()
    if any(word in lowered for word in ("competitor", "company", "inc", "ltd", "corp", "startup", "platform", "app")):
        return "competitor" if any(word in lowered for word in ("vs", "competitor", "rival", "alternative", "competes")) else "market"
    if any(word in lowered for word in ("customer", "user", "consumer", "client", "buyer")):
        return "customer"
    return "market"
