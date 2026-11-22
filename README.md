# Multi-Agent Market Research App

A small Streamlit prototype for the AI Traineeship Assignment. Enter a company or industry and four roles run in sequence to produce a short research brief:

**Orchestrator → Researcher → Analyst → Critic**

The app works with **no API key** using clearly labelled illustrative sample data. In **LLM mode**, small talk uses the chat API; research queries use **hybrid evidence**: live web search when `TAVILY_API_KEY` is configured, otherwise labelled sample data fallback. All evidence is passed through as labelled sources in the brief.

## Project structure

| Layer | File | Purpose |
| --- | --- | --- |
| Controller / View | `app.py` | Streamlit interface and result display |
| Controller | `run_cli.py` | Terminal demo of the same workflow |
| Service | `workflow.py` | Sequences the roles and manages the one allowed revision |
| Roles | `agents/orchestrator.py`, `agents/researcher.py`, `agents/analyst.py`, `agents/critic.py` | One role per file; shared prompts and helpers live in `agents/common.py` |
| Repository | `repository.py` | Single evidence-access entry point; chooses web search or sample fallback |
| Search adapter | `search_client.py` | Optional Tavily web search; normalizes results into labelled findings |
| Data source | `sample_data.py` | Labelled illustrative datasets and topic matching fallback |
| Domain | `models.py` | Pydantic models for the query, findings, draft, critique and final brief |
| Adapter | `llm_client.py` | Optional OpenAI-compatible chat-completions client (standard library only) |
| Docs | `README.md`, `sample_output.md`, `.env.example` | Setup, example run and placeholders — no secrets |

## Architecture

A layered monolith is used because there is one screen, no database and no need for independent deployment:

```text
Controller / View (app.py, run_cli.py)
    -> Service (workflow.py)
        -> Roles (agents/*)
            -> Repository (repository.py)
                -> Data source (sample_data.py)
```

`models.py` is shared by every layer and `llm_client.py` is an optional external adapter. Each role receives and updates the same `ResearchState`, so handoffs stay explicit. No web framework beyond Streamlit, message queue or microservices are involved.

## Data strategy: hybrid (chosen)

| Choice | Pros | Cons |
| --- | --- | --- |
| Sample data only | Offline, deterministic, easy to grade | Limited topics, not current |
| Web search only | Current sources for any topic | Needs key/network, non-deterministic, fails offline |
| **Hybrid (chosen)** | Works offline with sample fallback; uses live web search in LLM mode when configured; keeps evidence labelled | Web results need verification and can vary by run |

Default behavior: no keys = offline sample data. With `OPENAI_API_KEY`, small talk uses chat and research uses hybrid evidence. Add `TAVILY_API_KEY` to enable live web search; if search fails or is not configured, Researcher falls back to `sample_data.py`.

## How the handoffs work

One `ResearchState` object is created from the query and updated by each role:

1. **Orchestrator** classifies intent. Small talk gets a short `reply` and the workflow stops. Research queries get a scope and up to three research questions (`OrchestratorOutput`).
2. **Researcher** looks up the matching labelled sample dataset and records findings with source objects and information gaps (`ResearcherOutput`). No claim is added without a source.
3. **Analyst** writes a structured `Brief`: summary, up to two competitors, key observations, sources and missing information.
4. **Critic** checks the brief against the findings. If structural problems are found it requests one revision; the analyst revises once, using the feedback, and the critic performs a final check.

The Streamlit app shows the brief as the main result and keeps handoffs/findings/critic/shared state in a collapsed "Workflow details" expander. The assignment evaluates role handoffs, so they remain visible, but the primary UI stays focused on the brief.

## Setup and run

Requires Python 3.10 or newer (tested on Python 3.11+).

```bash
# 1. Create and activate a virtual environment
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

# 2. Install dependencies
python -m pip install -r requirements.txt

# 3. Start the app
streamlit run app.py
```

Streamlit prints a local URL (normally `http://localhost:8501`). Open it in a browser, enter a query such as `Analyze the food delivery market in Nepal.` and click **Start research**.

Optional terminal run without a browser:

```bash
python run_cli.py --query "Analyze the food delivery market in Nepal."
```

## Optional LLM + hybrid search mode

```bash
copy .env.example .env      # Windows
cp .env.example .env        # macOS / Linux
```

Edit `.env`:

- `OPENAI_API_KEY`: enables LLM mode (small talk chat + LLM-assisted research roles).
- `TAVILY_API_KEY`: optional; enables live web search for research queries in LLM mode.
- `SEARCH_PROVIDER=auto|tavily|none`: controls web search.
- `RESEARCH_MODE=auto|sample|llm`: `auto` uses LLM when key exists; `sample` forces offline; `llm` requires key.

If web search is unavailable, the app falls back to labelled sample data instead of breaking.

Never commit `.env` or an API key. The repository contains only `.env.example` with empty placeholders.

## Data and limitations

- `sample_data.py` contains **illustrative, unverified** data for seven example markets: food delivery, ride hailing, e-commerce, digital wallets/fintech, EdTech, IT outsourcing and tourism in Nepal. Other queries get an honest placeholder result that states no topic-specific evidence is available.
- Live web search is optional and only used for research queries when LLM mode and `TAVILY_API_KEY` are configured. Without it, the app uses labelled sample data. To add offline coverage, append a topic to `TOPICS` in `sample_data.py`.
- Every finding carries a labelled `Source`; web results are labelled as web search and sample findings are labelled as sample data.
- The critic requests at most one revision, as required. Rule-based checks cover the required sections, competitor count, sources, evidence labels, summary repetition and unsupported superlatives.
- This is a teaching prototype, not investment advice or verified market intelligence.

## Submission contents

Source code, this README, `.env.example` and `sample_output.md` are all in the repository root. No API keys or other secrets are included.
