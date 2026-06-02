import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from server.config import settings
from server.tools.search import tavily_search

# We use the same fast and free Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=settings.GEMINI_API_KEY,
    temperature=0.3
)

RESEARCHER_PROMPT = """
You are a research agent. You have been given a specific sub-question to research.
You have access to web search results. Use them to synthesize a clear, factual summary.

Sub-question: {sub_question}

Search Results:
{search_results}

Instructions:
- Synthesize the findings into a clear, factual summary (150-250 words)
- Include specific data points, names, and numbers where available
- Base your summary ONLY on the provided search results

Return ONLY a JSON object exactly matching this structure. No markdown blocks like ```json.
{{
  "summary": "...",
  "sources": ["url1", "url2"],
  "key_points": ["point 1", "point 2"]
}}
"""

async def run_researcher(state: dict) -> dict:
    """
    The Researcher node.
    When we implement parallel execution (Send API), LangGraph will pass a custom dictionary 
    to this node containing just the 'sub_question' for this specific branch.
    """
    sub_question = state.get("sub_question")
    search_depth = state.get("search_depth", "basic")
    
    if not sub_question:
        raise ValueError("Researcher node requires a 'sub_question' in the state payload.")
        
    # 1. Call our Tavily Tool
    raw_results = await tavily_search(sub_question, max_results=3, search_depth=search_depth)
    
    # Extract URLs for the prompt
    sources = [res.get("url") for res in raw_results if res.get("url")]
    
    # Format the results into a string for the prompt
    formatted_results = "\n\n".join([
        f"Title: {res.get('title')}\nURL: {res.get('url')}\nContent: {res.get('content')}"
        for res in raw_results
    ])
    
    # 2. Ask Gemini to summarize
    prompt = RESEARCHER_PROMPT.format(
        sub_question=sub_question,
        search_results=formatted_results
    )
    
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    
    # 3. Parse JSON
    try:
        text = response.content.strip().strip('`').removeprefix('json').strip()
        data = json.loads(text)
    except Exception as e:
        print(f"Failed to parse researcher output: {response.content}")
        data = {
            "summary": "Failed to synthesize findings.",
            "sources": sources,
            "key_points": []
        }
    
    # 4. Construct the final finding dictionary
    finding = {
        "sub_question": sub_question,
        "summary": data.get("summary", ""),
        "sources": data.get("sources", sources),
        "key_points": data.get("key_points", [])
    }
    
    # Returns a LIST! Why? Because in state.py, we defined `findings` with `operator.add`
    # Returning a list ensures LangGraph adds this to the global state rather than overwriting.
    return {"findings": [finding]}

if __name__ == "__main__":
    import asyncio
    
    if not settings.GEMINI_API_KEY or not settings.TAVILY_API_KEY:
        print("Error: Ensure both GEMINI_API_KEY and TAVILY_API_KEY are set.")
        exit(1)
        
    async def test():
        print("Testing Researcher Agent...")
        # Simulating the payload LangGraph's Send API will give us
        mock_state = {"sub_question": "What are the most popular backend frameworks in 2025?"}
        
        result = await run_researcher(mock_state)
        print(json.dumps(result, indent=2))
        
    asyncio.run(test())
