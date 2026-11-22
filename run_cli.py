"""Headless demo: prints every handoff and the final brief. No Streamlit needed."""

from __future__ import annotations

import argparse

from workflow import run_research

DEFAULT_QUERY = "Analyze the food delivery market in Nepal."

parser = argparse.ArgumentParser(description="Run the four-agent market research workflow in the terminal.")
parser.add_argument("--query", default=DEFAULT_QUERY, help="Company or industry to research.")
args = parser.parse_args()

print(f"Query: {args.query}\n")
try:
    state = run_research(args.query, on_step=lambda message: print(f"- {message}"))
except ValueError as exc:
    print(f"Input error: {exc}")
    raise SystemExit(2) from exc
print(f"\nMode: {state.mode}\n")
if state.reply:
    print(state.reply)
    raise SystemExit(0)
print("Handoffs:")
for index, message in enumerate(state.trace, start=1):
    print(f"{index}. {message}")
print("\n" + state.final_brief.to_markdown())
