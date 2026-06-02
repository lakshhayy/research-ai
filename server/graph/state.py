from typing import TypedDict, Annotated
import operator

class ResearchState(TypedDict):
    # --- Input ---
    query: str
    session_id: str
    search_depth: str # "basic" or "advanced"

    # --- Planner output ---
    sub_questions: list[str]

    # --- Researcher output ---
    # Annotated[list, operator.add] tells LangGraph how to handle state updates for this field.
    # Instead of overwriting the list when a new finding comes in, it APPENDS (adds) it.
    # This is crucial for parallel researchers, so they don't overwrite each other's work!
    findings: Annotated[list[dict], operator.add]

    # --- Critic output ---
    critique: dict                    # Dictionary mapping: { sub_question: score (0-10) }
    gaps: list[str]                   # List of sub-questions that scored too low

    # --- Loop control ---
    retry_count: int                  # How many retry loops have happened

    # --- Synthesizer output ---
    final_report: str

    # --- Grader output ---
    confidence_score: float
    follow_up_questions: list[str]
    sources: list[str]
