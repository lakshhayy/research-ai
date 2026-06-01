import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from server.config import settings
from server.graph.state import ResearchState

# Initialize the Gemini model
# We use gemini-1.5-flash because it is fast, free, and excellent at reasoning tasks
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    api_key=settings.GEMINI_API_KEY,
    temperature=0.2 # Low temperature for more deterministic/structured output
)

PLANNER_PROMPT = """
You are a research planning agent. Your job is to decompose a research query into
3-5 specific, non-overlapping sub-questions that together fully cover the topic.

Rules:
- Each sub-question must be answerable with a web search
- Sub-questions must not overlap or repeat each other
- Cover different angles: current state, comparisons, trends, opinions, data

Query: {query}

Return ONLY a JSON array of strings. No preamble. No markdown blocks like ```json.
Example: ["What are the most used backend frameworks in 2025?", "How do they compare in performance?"]
"""

async def run_planner(state: ResearchState) -> dict:
    """
    The Planner node in our LangGraph.
    Takes the user's query and breaks it down into sub-questions.
    Returns a dict with the key 'sub_questions' to update the state.
    """
    query = state["query"]
    
    # Format the prompt
    prompt = PLANNER_PROMPT.format(query=query)
    
    # Call the LLM
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    
    try:
        # Parse the JSON array from the response text
        # We strip backticks just in case the LLM ignored the instruction not to use them
        text = response.content.strip().strip('`').removeprefix('json').strip()
        sub_questions = json.loads(text)
    except Exception as e:
        # Fallback if parsing fails
        print(f"Failed to parse planner output: {response.content}")
        sub_questions = [query] # Just use the original query as a single sub-question
        
    # Return the dictionary to update the graph state
    return {"sub_questions": sub_questions}

if __name__ == "__main__":
    # Test script (run with: python -m server.agents.planner)
    import asyncio
    
    if not settings.GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY is not set in your .env file!")
        exit(1)
        
    async def test():
        state = {"query": "What are the best backend frameworks in 2025 and why?"}
        print(f"Testing Planner with query: '{state['query']}'\n")
        
        result = await run_planner(state)
        
        print("Generated Sub-questions:")
        for i, sq in enumerate(result["sub_questions"], 1):
            print(f"{i}. {sq}")
            
    asyncio.run(test())
