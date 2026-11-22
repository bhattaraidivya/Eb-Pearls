"""Orchestrator role: turns the user query into a scoped research plan."""

from __future__ import annotations

import re

from pydantic import ValidationError

import llm_client
from agents.common import BASE_SYSTEM, try_llm
from models import OrchestratorOutput, ResearchState

OFFLINE_REPLY = (
    "I don't have enough data for that in offline mode. "
    "Ask for a research topic I have sample data for, like food delivery, ride hailing, e-commerce, "
    "digital wallets, EdTech, IT outsourcing, or tourism in Nepal."
)
CHAT_SYSTEM = (
    "You are a helpful assistant in a market-research app. "
    "Reply briefly and naturally. If the user wants research on a company or industry, "
    "ask them to provide that specific research topic."
)

SMALL_TALK_PATTERNS = (
    r"^(?:hi|hello|hey|yo|greetings|hi there|hello there|good morning|good afternoon|good evening)$",
    r"^(?:how(?:'?s| is) (?:the )?weather|what(?:'?s| is) the weather|weather)$",
    r"^(?:how(?:'?s| is) it going|how are you|how(?:'?s) things)$",
    r"^(?:thanks|thank you|bye|goodbye|see you)$",
)


def _is_small_talk(query: str) -> bool:
    text = re.sub(r"\s+", " ", query.strip().lower()).rstrip(" .!?")
    return any(re.fullmatch(pattern, text) for pattern in SMALL_TALK_PATTERNS)


def _small_talk_reply(state: ResearchState, use_llm: bool) -> str:
    if use_llm:
        return llm_client.call_text(CHAT_SYSTEM, state.query)
    return OFFLINE_REPLY


def run(state: ResearchState, use_llm: bool) -> ResearchState:
    if _is_small_talk(state.query):
        reply = _small_talk_reply(state, use_llm)
        state.orchestrator = OrchestratorOutput(scope="", intent="small_talk", reply=reply)
        mode = "LLM chat" if use_llm else "offline mode"
        state.log("Orchestrator", f"classified the input as small talk; replied via {mode}.")
        return state

    scope = re.sub(
        r"^(?:please\s+)?(?:analyze|analyse|research|compare|summarize|summarise|brief me on|tell me about)\s+(?:the\s+)?",
        "",
        state.query.strip(),
        flags=re.IGNORECASE,
    ).rstrip(".? ")
    fallback = OrchestratorOutput(
        scope=scope or state.query.rstrip(".?"),
        research_questions=[
            "What market context is described in the available evidence?",
            "Which competitors appear in the available evidence?",
            "What customer needs and operational constraints are mentioned?",
        ],
    )

    result = None
    if use_llm:
        data = try_llm(
            state,
            BASE_SYSTEM,
            f"Role: Orchestrator. User query: {state.query!r}. "
            "Return JSON: {\"intent\": \"research\"|\"small_talk\", \"scope\": string, "
            "\"reply\": string, \"research_questions\": [at most 3 short strings]}. "
            "Use intent='small_talk' for greetings, weather, chit-chat or anything that is not a company/industry research request. "
            "For small talk, set scope='', research_questions=[] and put a short helpful reply in reply.",
        )
        if data:
            try:
                candidate = OrchestratorOutput(**data)
                if candidate.intent == "small_talk":
                    result = OrchestratorOutput(scope="", intent="small_talk", reply=_small_talk_reply(state, use_llm))
                elif candidate.scope.strip():
                    candidate.intent = "research"
                    candidate.reply = ""
                    result = candidate
            except ValidationError:
                pass

    state.orchestrator = result or fallback
    state.log(
        "Orchestrator",
        f"accepted query; scope='{state.orchestrator.scope}'; passed {len(state.orchestrator.research_questions)} questions to Researcher.",
    )
    return state
