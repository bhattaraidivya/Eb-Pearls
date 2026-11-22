"""Critic role: checks the brief and requests at most one revision."""

from __future__ import annotations

import re

from pydantic import ValidationError

from agents.common import BASE_SYSTEM, dump, try_llm, unique
from models import Brief, CriticOutput, ResearchState


def run(state: ResearchState, use_llm: bool, final_check: bool = False) -> ResearchState:
    brief = state.draft
    issues = rule_issues(state, brief)
    llm_feedback = ""

    if use_llm:
        data = try_llm(
            state,
            BASE_SYSTEM,
            "Role: Critic. Review the brief against the research findings. Flag missing sections, "
            "more than 2 competitors, unsupported superlatives or unsourced observations. "
            f"Research: {dump(state.research)}. Brief: {dump(brief)}. "
            "Return JSON: {\"verdict\": approve|revise, \"feedback\": string, \"issues\": [strings]}.",
        )
        if data:
            try:
                candidate = CriticOutput(**data)
                issues = unique(issues + [str(i) for i in candidate.issues])
                if not final_check and candidate.verdict == "revise" and not issues:
                    issues = ["critic requested revision"]
                if candidate.feedback:
                    llm_feedback = candidate.feedback
            except (TypeError, ValidationError):
                state.log("Critic", "LLM critique was invalid; used rule-based checks.")

    if final_check:
        verdict = "approve" if not issues else "revise"
        feedback = "Final check passed." if not issues else "Remaining issues after one revision: " + "; ".join(issues)
    else:
        verdict = "revise" if issues else "approve"
        if issues:
            feedback = llm_feedback if llm_feedback else "Requesting one revision: " + "; ".join(issues)
        else:
            feedback = llm_feedback or "Brief is complete and evidence-based."

    state.critique = CriticOutput(verdict=verdict, feedback=feedback, issues=issues)
    state.log(
        "Critic",
        f"verdict={verdict}; issues={len(issues)}"
        + ("; one revision already used, no further revision requested." if final_check and issues else ""),
    )
    return state


def rule_issues(state: ResearchState, brief: Brief) -> list[str]:
    issues: list[str] = []
    if len(brief.summary.strip()) < 30:
        issues.append("summary is too short")
    if not brief.key_observations:
        issues.append("no key observations")
    if len(brief.competitors) > 2:
        issues.append("more than two competitors")
    if not brief.sources:
        issues.append("no sources listed")
    if not brief.missing_information:
        issues.append("no missing information listed")
    summary_text = re.sub(r"\s+", " ", brief.summary).lower()
    for observation in brief.key_observations:
        core = re.sub(r"\s*\(Source:.*\)\s*$", "", observation)
        core = re.sub(r"^Sample data(?: placeholder)?:\s*", "", core)
        if len(core) > 25 and core.lower() in summary_text:
            issues.append("summary repeats an observation instead of synthesizing")
            break
    origin = (state.research.data_origin or "").lower() if state.research else ""
    if "sample" in origin and not any("sample" in item.lower() for item in brief.key_observations):
        issues.append("observations do not label the sample evidence")
    if "web search" in origin and not any("web search" in item.lower() or "source:" in item.lower() for item in brief.key_observations):
        issues.append("observations do not cite web search evidence")
    text = " ".join([brief.summary] + brief.key_observations).lower()
    if re.search(r"\b(largest|fastest|leading|number one|#1)\b", text):
        issues.append("unsupported superlative claim")
    return issues
