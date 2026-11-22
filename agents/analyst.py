"""Analyst role: writes the brief and applies one round of critic feedback."""

from __future__ import annotations

from pydantic import ValidationError

import sample_data
from agents.common import BASE_SYSTEM, dump, plain, topic_text, try_llm, unique
from models import Brief, ResearchState


def run(state: ResearchState, use_llm: bool, revision: bool = False) -> ResearchState:
    fallback = _deterministic_brief(state)
    brief = fallback
    feedback = state.critique.feedback if revision and state.critique else ""

    if use_llm:
        instruction = (
            "Role: Analyst. Write a short brief using ONLY the findings below. "
            "Include at most 2 competitors. Every observation must end with '(Source: <source title>)'. "
            "Copy the source titles exactly and list the missing information provided. "
            "Return JSON: {\"summary\": string, \"competitors\": [strings], "
            "\"key_observations\": [strings], \"sources\": [strings], \"missing_information\": [strings]}."
        )
        if revision:
            instruction += f" Revise this brief using the critic feedback: {feedback!r}."
        user_prompt = f"{instruction} Scope: {state.orchestrator.scope!r}. Research: {dump(state.research)}."
        if revision:
            user_prompt += f" Previous brief: {dump(state.draft)}"
        data = try_llm(state, BASE_SYSTEM, user_prompt)
        if data:
            try:
                allowed_sources = unique([f.source.title for f in state.research.findings])
                data["topic"] = state.orchestrator.scope
                data["sources"] = [s for s in data.get("sources", []) if s in allowed_sources] or fallback.sources
                data["missing_information"] = data.get("missing_information") or fallback.missing_information
                brief = Brief(**data)
            except (TypeError, ValidationError):
                state.log("Analyst", "LLM draft was invalid; used the template-based draft.")

    if revision:
        brief = brief.model_copy(deep=True)
        brief.competitors = brief.competitors[:2]
        brief.key_observations = brief.key_observations[:6] or fallback.key_observations
        brief.sources = brief.sources or fallback.sources
        brief.missing_information = brief.missing_information or fallback.missing_information
        brief.revision_note = feedback or "Applied critic feedback: tightened the brief."
        issues = state.critique.issues if state.critique else []
        if any("summary repeats" in issue for issue in issues):
            origin = state.research.data_origin.lower()
            evidence_label = "web search" if "web search" in origin else "labelled sample"
            brief.summary = (
                f"Revised brief: {topic_text(state.orchestrator.scope)} — the {evidence_label} evidence provides "
                f"{len(state.research.findings)} findings covering market context, customer priorities "
                "and named competitors. These points should be verified before decisions are made."
            )
        elif not brief.summary.startswith("Revised brief:"):
            brief.summary = f"Revised brief: {brief.summary}"
        state.log("Analyst", "revised the brief once using critic feedback; passed it back to Critic.")
    else:
        state.log("Analyst", f"drafted a brief with {len(brief.key_observations)} observations; passed it to Critic.")

    state.draft = brief
    return state


def _deterministic_brief(state: ResearchState) -> Brief:
    evidence = state.research
    findings = evidence.findings
    claims = [plain(f.claim) for f in findings]
    context = [c for f, c in zip(findings, claims) if f.category in ("market", "customer")] or claims
    summary = (
        f"This brief covers {topic_text(state.orchestrator.scope)}. It uses {len(findings)} "
        f"{'finding' if len(findings) == 1 else 'findings'} from {evidence.data_origin}. "
    )
    if context:
        summary += " ".join(context[:2]) + " "
    summary += "All points are illustrative and should be verified before decisions are made."

    return Brief(
        topic=state.orchestrator.scope,
        summary=summary,
        competitors=sample_data.competitor_names(findings),
        key_observations=[f"{f.claim} (Source: {f.source.title})" for f in findings],
        sources=unique(
            [
                f"{f.source.title} — {f.source.kind}; {f.source.note}" + (f" URL: {f.source.url}" if f.source.url else "")
                for f in findings
            ]
        ),
        missing_information=list(evidence.missing_information),
    )
