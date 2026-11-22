"""Structured data shared by the four agents."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Intent = Literal["research", "small_talk"]


class Source(BaseModel):
    title: str
    kind: str = "Sample data"
    url: str = ""
    note: str = ""


class Finding(BaseModel):
    category: Literal["market", "competitor", "customer", "other"] = "other"
    claim: str
    source: Source


class OrchestratorOutput(BaseModel):
    scope: str
    intent: Intent = "research"
    reply: str = ""
    research_questions: list[str] = Field(default_factory=list)


class ResearcherOutput(BaseModel):
    findings: list[Finding] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    data_origin: str = "Labelled sample data (illustrative, not live research)"


class Brief(BaseModel):
    topic: str
    summary: str
    competitors: list[str] = Field(default_factory=list)
    key_observations: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    revision_note: str = ""

    def to_markdown(self) -> str:
        lines = [f"# Research brief: {self.topic}", "", "## Summary", self.summary, "", "## Competitors"]
        if self.competitors:
            lines.extend(f"- {name}" for name in self.competitors)
        else:
            lines.append("- None identified in the available evidence.")
        lines += ["", "## Key observations"]
        if self.key_observations:
            lines.extend(f"- {item}" for item in self.key_observations)
        else:
            lines.append("- No supported observations available.")
        lines += ["", "## Sources and missing information", "**Sources**"]
        if self.sources:
            lines.extend(f"- {item}" for item in self.sources)
        else:
            lines.append("- No sources available.")
        lines += ["", "**Missing information**"]
        if self.missing_information:
            lines.extend(f"- {item}" for item in self.missing_information)
        else:
            lines.append("- None recorded.")
        if self.revision_note:
            lines += ["", f"**Revision note:** {self.revision_note}"]
        return "\n".join(lines) + "\n"


class CriticOutput(BaseModel):
    verdict: Literal["approve", "revise"]
    feedback: str
    issues: list[str] = Field(default_factory=list)


class ResearchState(BaseModel):
    """One state object is passed from role to role and updated at each handoff."""

    query: str
    mode: Literal["Sample data", "LLM"] = "Sample data"
    reply: str = ""
    orchestrator: OrchestratorOutput | None = None
    research: ResearcherOutput | None = None
    draft: Brief | None = None
    critique: CriticOutput | None = None
    final_brief: Brief | None = None
    revision_count: int = 0
    trace: list[str] = Field(default_factory=list)

    def log(self, role: str, message: str) -> None:
        self.trace.append(f"{role} -> {message}")
