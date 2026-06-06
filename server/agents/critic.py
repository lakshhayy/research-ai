import json
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from server.config import settings
from server.graph.state import ResearchState

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=settings.GROQ_API_KEY,
    temperature=0.1 # Very low temperature for strict grading
)

CRITIC_PROMPT = """
You are a research quality critic. You will evaluate multiple research findings and give each a quality score.

Findings:
{findings}

Score each finding from 0-10 based on:
- Relevance to its sub-question (0-4 points)
- Specificity and data quality (0-3 points)
- Recency and credibility of sources (0-3 points)

Score < 6 means the research needs to be redone.
Score >= 6 means the research is acceptable.

Return ONLY a JSON object exactly matching this structure. No markdown blocks like ```json.
{{
  "critique": {{
    "sub_question_1": 7,
    "sub_question_2": 4
  }},
  "gaps": ["missing X", "needs more Y"]
}}
"""

async def run_critic(state: ResearchState) -> dict:
    """
    The Critic node evaluates all findings currently in the state in a SINGLE LLM call.
    It returns a critique dictionary containing scores, identifies any gaps, 
    and increments the retry count.
    """
    findings = state.get("findings", [])
    
    # Format all findings into a single string
    formatted_findings = ""
    for f in findings:
        formatted_findings += f"Sub-question: {f.get('sub_question')}\n"
        formatted_findings += f"Summary: {f.get('summary')}\n\n"
        
    prompt = CRITIC_PROMPT.format(
        findings=formatted_findings
    )
    
    print("🤖 Critic evaluating all findings at once...")
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    
    try:
        text = response.content.strip().strip('`').removeprefix('json').strip()
        data = json.loads(text)
        critique = data.get("critique", {})
        all_gaps = data.get("gaps", [])
    except Exception as e:
        print(f"Failed to parse critic output: {response.content}")
        critique = {f.get("sub_question"): 0 for f in findings}
        all_gaps = ["Failed to generate a valid critique."]

    # Increment retry count for the state
    current_retry = state.get("retry_count", 0)
    
    return {
        "critique": critique,
        "gaps": all_gaps,
        "retry_count": current_retry + 1
    }

if __name__ == "__main__":
    import asyncio
    
    if not settings.GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY is not set.")
        exit(1)
        
    async def test():
        print("Testing Critic Agent...")
        # Mocking the state after Researcher has run
        mock_state = {
            "retry_count": 0,
            "findings": [
                {
                    "sub_question": "What is Python?",
                    "summary": "Python is a snake. It is very long and eats mice."
                },
                {
                    "sub_question": "What is FastAPI?",
                    "summary": "FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.8+ based on standard Python type hints."
                }
            ]
        }
        
        result = await run_critic(mock_state)
        print(json.dumps(result, indent=2))
        
    asyncio.run(test())
