"""Researcher role: fetches labelled evidence from the repository."""

from __future__ import annotations

from pydantic import ValidationError

import repository
from agents.common import BASE_SYSTEM, dump, try_llm
from models import Finding, ResearcherOutput, ResearchState


def run(state: ResearchState, use_llm: bool) -> ResearchState:
    evidence = repository.get_evidence(state.query, allow_web=use_llm)
    state.research = evidence

    if use_llm:
        data = try_llm(
            state,
            BASE_SYSTEM,
            "Role: Researcher. Organize ONLY the supplied evidence, without adding facts. "
            f"Questions: {dump(state.orchestrator.research_questions)}. "
            f"Evidence: {dump(evidence.findings)}. Gaps: {dump(evidence.missing_information)}. "
            "Return JSON: {\"findings\": [{\"claim\": string, \"category\": market|competitor|customer|other, "
            "\"source_index\": integer}], \"missing_information\": [strings]}. Use at most 5 findings.",
        )
        if data and evidence.findings:
            try:
                findings: list[Finding] = []
                for entry in data.get("findings", []):
                    if not isinstance(entry, dict):
                        continue
                    index = int(entry.get("source_index", 0))
                    index = index if 0 <= index < len(evidence.findings) else 0
                    findings.append(
                        Finding(
                            claim=str(entry.get("claim", "")),
                            category=entry.get("category", "other"),
                            source=evidence.findings[index].source,
                        )
                    )
                gaps = [str(item) for item in data.get("missing_information", []) if str(item).strip()]
                if findings:
                    state.research = ResearcherOutput(
                        findings=findings,
                        missing_information=gaps or evidence.missing_information,
                        data_origin=evidence.data_origin + " (organised by LLM)",
                    )
            except (AttributeError, KeyError, TypeError, ValueError, ValidationError):
                state.log("Researcher", "LLM research output was invalid; kept the labelled sample findings.")

    state.log(
        "Researcher",
        f"collected {len(state.research.findings)} findings and {len(state.research.missing_information)} information gaps; passed them to Analyst.",
    )
    return state
