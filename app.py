"""Streamlit UI for the four-agent market research workflow."""

from __future__ import annotations

import streamlit as st

import llm_client
from workflow import run_research

st.set_page_config(page_title="Multi-Agent Market Research", layout="wide")
st.title("Multi-Agent Market Research")
st.caption("Orchestrator → Researcher → Analyst → Critic. Short briefs from labelled evidence.")

with st.sidebar:
    st.header("Run mode")
    try:
        llm_on = llm_client.use_llm()
    except llm_client.LLMError as exc:
        st.warning(str(exc))
        llm_on = False
    st.write("LLM enabled" if llm_on else "Offline sample-data mode")
    st.caption(
        "Offline mode uses illustrative sample datasets included in this repository. "
        "Add OPENAI_API_KEY to .env to let the same LLM power all four roles."
    )
    st.divider()
    st.markdown("**Submission project:** AI Traineeship Assignment — basic multi-agent app.")

examples = [
    "Analyze the food delivery market in Nepal.",
    "Research ride hailing in Nepal.",
    "Analyze online shopping in Nepal.",
]
columns = st.columns(len(examples))
for column, example in zip(columns, examples):
    if column.button(example, use_container_width=True, key=example):
        st.session_state["query"] = example
        st.rerun()

query = st.text_input("Company or industry", key="query", placeholder="e.g. Analyze the food delivery market in Nepal.")
if st.button("Start research", type="primary"):
    st.session_state.pop("state", None)
    st.session_state.pop("error", None)
    try:
        with st.status("Running the four-agent workflow…", expanded=True) as status:
            state = run_research(query, on_step=status.write, use_llm=llm_on)
            status.update(label="Run complete", state="complete", expanded=False)
        st.session_state["state"] = state
    except Exception as exc:
        st.session_state["error"] = str(exc)

if st.session_state.get("error"):
    st.error(f"Research failed: {st.session_state['error']}")

state = st.session_state.get("state")
reply = getattr(state, "reply", "") if state else ""
if state and reply:
    st.subheader("Assistant reply")
    st.write(reply)
    st.caption("No research brief was generated for this input.")
elif state and state.final_brief:
    brief = state.final_brief
    st.subheader("Research brief")
    st.markdown(brief.to_markdown())
    st.download_button(
        "Download brief (.md)",
        data=brief.to_markdown(),
        file_name="research_brief.md",
        mime="text/markdown",
    )

    with st.expander("Workflow details", expanded=False):
        st.caption(
            "The assignment evaluates whether roles and handoffs work; the brief above is the main result. "
            "These tabs show the supporting evidence and state."
        )
        tab_handoffs, tab_findings, tab_critic, tab_state = st.tabs(
            ["Agent handoffs", "Research findings", "Critic review", "Shared state (JSON)"]
        )
        with tab_handoffs:
            for index, message in enumerate(state.trace, start=1):
                st.write(f"{index}. {message}")
        with tab_findings:
            st.markdown(f"**Data origin:** {state.research.data_origin}")
            for finding in state.research.findings:
                st.markdown(f"- **{finding.category.title()}** — {finding.claim}  \n  Source: {finding.source.title}")
            st.markdown("**Missing information**")
            for gap in state.research.missing_information:
                st.markdown(f"- {gap}")
        with tab_critic:
            st.write(f"**Verdict:** {state.critique.verdict}")
            st.write(state.critique.feedback)
            st.write(f"**Revision count:** {state.revision_count} (maximum allowed: 1)")
        with tab_state:
            st.json(state.model_dump())
