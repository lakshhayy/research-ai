from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from server.config import settings
from server.graph.state import ResearchState
from server.agents.planner import run_planner
from server.agents.researcher import run_researcher
from server.agents.critic import run_critic
from server.agents.synthesizer import run_synthesizer
from server.agents.grader import run_grader

def map_sub_questions(state: ResearchState):
    """
    This is the core of our parallel processing. 
    It reads the sub_questions from the state and returns a list of Send objects.
    LangGraph will spin up a separate Researcher node for EACH Send object simultaneously.
    """
    sub_questions = state.get("sub_questions", [])
    search_depth = state.get("search_depth", "basic")
    
    # We map each sub-question to a new Researcher payload
    return [
        Send("researcher", {"sub_question": sq, "search_depth": search_depth})
        for sq in sub_questions
    ]

def route_critic(state: ResearchState):
    """
    Conditional routing logic based on the Critic's scores.
    """
    critique = state.get("critique", {})
    retry_count = state.get("retry_count", 0)
    
    # Check if ANY of the sub-question scores fell below our minimum standard
    needs_retry = any(score < settings.MIN_QUALITY_SCORE for score in critique.values())
    
    if needs_retry and retry_count < settings.MAX_RETRY_COUNT:
        print(f"🔄 Quality below {settings.MIN_QUALITY_SCORE}. Looping back! (Retry {retry_count}/{settings.MAX_RETRY_COUNT})")
        # In a more advanced version we might just re-run specific failed researchers, 
        # but for simplicity, we tell the planner to come up with completely new angles.
        return "planner"
    
    print("✅ Quality passed (or max retries reached). Moving to Synthesizer.")
    return "synthesizer"

# 1. Initialize the Graph
builder = StateGraph(ResearchState)

# 2. Add all our Agent Nodes
builder.add_node("planner", run_planner)
builder.add_node("researcher", run_researcher)
builder.add_node("critic", run_critic)
builder.add_node("synthesizer", run_synthesizer)
builder.add_node("grader", run_grader)

# 3. Define the Control Flow Edges
# Start -> Planner
builder.add_edge(START, "planner")

# Planner -> (Parallel Map) -> Researchers
builder.add_conditional_edges(
    "planner", 
    map_sub_questions, 
    ["researcher"] # This tells LangGraph the Send objects will target the "researcher" node
)

# Researchers -> Critic
# Notice we just add a normal edge. LangGraph is smart enough to wait for ALL
# parallel researchers to finish before it triggers the single Critic node!
builder.add_edge("researcher", "critic")

# Critic -> (Conditional Logic) -> Synthesizer OR Planner
builder.add_conditional_edges(
    "critic", 
    route_critic,
    {
        "planner": "planner",
        "synthesizer": "synthesizer"
    }
)

# Synthesizer -> Grader -> End
builder.add_edge("synthesizer", "grader")
builder.add_edge("grader", END)

# 4. Compile the Graph
# This turns our blueprint into an executable app
graph = builder.compile()
