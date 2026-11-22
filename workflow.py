"""Service layer: sequences the four roles and manages the single allowed revision."""

from __future__ import annotations

import llm_client
from agents import analyst, critic, orchestrator, researcher
from agents.common import StepCallback
from models import ResearchState


class MarketResearchWorkflow:
    def __init__(self, use_llm: bool | None = None) -> None:
        self.use_llm = llm_client.use_llm() if use_llm is None else use_llm

    def run(self, query: str, on_step: StepCallback = None) -> ResearchState:
        query = query.strip()
        if not query:
            raise ValueError("Enter a company or industry to research.")

        state = ResearchState(query=query, mode="LLM" if self.use_llm else "Sample data")

        orchestrator.run(state, self.use_llm)
        if state.orchestrator.intent == "small_talk":
            state.reply = state.orchestrator.reply
            self._step(on_step, "Orchestrator: small talk detected; no research workflow started.")
            state.log("Workflow", "returned a reply instead of a brief.")
            return state

        self._step(on_step, f"Orchestrator: planned scope '{state.orchestrator.scope}' ({len(state.orchestrator.research_questions)} questions).")
        researcher.run(state, self.use_llm)
        self._step(on_step, f"Researcher: {len(state.research.findings)} findings from {state.research.data_origin}.")
        analyst.run(state, self.use_llm)
        self._step(on_step, "Analyst: wrote the first brief from the findings.")
        critic.run(state, self.use_llm)
        self._step(on_step, f"Critic: {state.critique.verdict} — {state.critique.feedback}")

        if state.critique and state.critique.verdict == "revise" and state.revision_count < 1:
            state.revision_count += 1
            self._step(on_step, "Critic requested one revision; handing feedback back to the analyst.")
            analyst.run(state, self.use_llm, revision=True)
            self._step(on_step, "Analyst: revised the brief using the critic's feedback.")
            critic.run(state, self.use_llm, final_check=True)
            self._step(on_step, f"Critic: final review — {state.critique.verdict}.")

        state.final_brief = state.draft.model_copy(deep=True)
        return state

    @staticmethod
    def _step(callback: StepCallback, message: str) -> None:
        if callback:
            callback(message)


def run_research(query: str, on_step: StepCallback = None, use_llm: bool | None = None) -> ResearchState:
    """Convenience entry point used by the Streamlit app and the CLI demo."""

    workflow = MarketResearchWorkflow(use_llm=use_llm)
    return workflow.run(query, on_step=on_step)
