from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from server.config import settings
from server.graph.state import ResearchState

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=settings.GEMINI_API_KEY,
    temperature=0.4 # Slightly higher temperature for better narrative flow
)

SYNTHESIZER_PROMPT = """
You are a research synthesis agent. Combine research findings from multiple sub-questions
into a single coherent, well-structured markdown report.

Original query: {query}

Research findings:
{all_findings}

Report structure:
## [Title]
### Executive Summary (2-3 sentences)
### [Section per major theme found in findings]
### Key Takeaways (bullet points)
### Sources

Rules:
- Write for a technical audience
- Use standard markdown formatting
- Do not repeat information across sections
- Be specific — include numbers, names, dates where available
- Make sure to list all distinct sources at the bottom
"""

async def run_synthesizer(state: ResearchState) -> dict:
    """
    The Synthesizer node.
    It takes the original query and all the accumulated findings,
    and writes the final markdown report.
    """
    query = state.get("query", "")
    findings = state.get("findings", [])
    
    # Format the findings into a large string for the LLM
    formatted_findings = ""
    for finding in findings:
        formatted_findings += f"Sub-question: {finding.get('sub_question')}\n"
        formatted_findings += f"Summary: {finding.get('summary')}\n"
        formatted_findings += f"Sources: {', '.join(finding.get('sources', []))}\n\n"
        
    prompt = SYNTHESIZER_PROMPT.format(
        query=query,
        all_findings=formatted_findings
    )
    
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    
    # The response is just standard markdown text, not JSON, so no parsing needed!
    report = response.content.strip()
    
    return {"final_report": report}

if __name__ == "__main__":
    import asyncio
    
    if not settings.GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY is not set.")
        exit(1)
        
    async def test():
        print("Testing Synthesizer Agent...\n")
        mock_state = {
            "query": "What are the best backend frameworks in 2025?",
            "findings": [
                {
                    "sub_question": "What is FastAPI?",
                    "summary": "FastAPI is a modern web framework for Python.",
                    "sources": ["https://fastapi.tiangolo.com"]
                },
                {
                    "sub_question": "What is Express.js?",
                    "summary": "Express is a fast, unopinionated web framework for Node.js.",
                    "sources": ["https://expressjs.com"]
                }
            ]
        }
        
        result = await run_synthesizer(mock_state)
        print(result["final_report"])
        
    asyncio.run(test())
