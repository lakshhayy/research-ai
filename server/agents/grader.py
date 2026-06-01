import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from server.config import settings
from server.graph.state import ResearchState

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=settings.GEMINI_API_KEY,
    temperature=0.2 
)

GRADER_PROMPT = """
You are a research quality grader. Read the final report and assess its overall quality.

Report: 
{report}

Original query: {query}

Return ONLY a JSON object matching this structure exactly. No markdown blocks like ```json.
{{
  "confidence_score": 0.82,       
  "reasoning": "...",             
  "follow_up_questions": [        
    "...",
    "...",
    "..."
  ]
}}

Rules:
- confidence_score must be a float between 0.0 and 1.0
- reasoning is a 1-sentence explanation of the score
- follow_up_questions is a list of exactly 3 logical questions the user might want to ask next
"""

async def run_grader(state: ResearchState) -> dict:
    """
    The Grader node runs last. 
    It evaluates the final report, generates a confidence score, 
    and predicts follow-up questions for the user interface.
    """
    query = state.get("query", "")
    report = state.get("final_report", "")
    findings = state.get("findings", [])
    
    prompt = GRADER_PROMPT.format(
        query=query,
        report=report
    )
    
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    
    try:
        text = response.content.strip().strip('`').removeprefix('json').strip()
        data = json.loads(text)
    except Exception as e:
        print(f"Failed to parse grader output: {response.content}")
        data = {
            "confidence_score": 0.0,
            "reasoning": "Failed to parse LLM evaluation.",
            "follow_up_questions": []
        }
        
    # We also need to extract all unique sources from the findings to display in the UI
    all_sources = set()
    for finding in findings:
        for source in finding.get("sources", []):
            all_sources.add(source)
            
    return {
        "confidence_score": data.get("confidence_score", 0.0),
        "follow_up_questions": data.get("follow_up_questions", []),
        "sources": list(all_sources)
    }

if __name__ == "__main__":
    import asyncio
    
    if not settings.GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY is not set.")
        exit(1)
        
    async def test():
        print("Testing Grader Agent...\n")
        mock_state = {
            "query": "What are the best backend frameworks in 2025?",
            "final_report": "## Best Frameworks\nFastAPI and Express are great.",
            "findings": [{"sources": ["https://google.com"]}]
        }
        
        result = await run_grader(mock_state)
        print(json.dumps(result, indent=2))
        
    asyncio.run(test())
