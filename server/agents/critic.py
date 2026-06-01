import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from server.config import settings
from server.graph.state import ResearchState

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=settings.GEMINI_API_KEY,
    temperature=0.1 # Very low temperature for strict grading
)

CRITIC_PROMPT = """
You are a research quality critic. You will evaluate research findings on a sub-question
and give a quality score.

Sub-question: {sub_question}
Findings: {findings}

Score the findings from 0-10 based on:
- Relevance to the sub-question (0-4 points)
- Specificity and data quality (0-3 points)
- Recency and credibility of sources (0-3 points)

Score < 6 means the research needs to be redone.
Score >= 6 means the research is acceptable.

Return ONLY a JSON object matching this structure exactly. No markdown blocks like ```json.
{{
  "score": 7,
  "gaps": ["missing X", "needs more Y"]
}}
"""

async def run_critic(state: ResearchState) -> dict:
    """
    The Critic node evaluates all findings currently in the state.
    It returns a critique dictionary containing scores, identifies any gaps, 
    and increments the retry count.
    """
    findings = state.get("findings", [])
    
    critique = {}
    all_gaps = []
    
    # Evaluate each finding individually
    for finding in findings:
        sub_question = finding.get("sub_question", "Unknown")
        summary = finding.get("summary", "")
        
        prompt = CRITIC_PROMPT.format(
            sub_question=sub_question,
            findings=summary
        )
        
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        
        try:
            text = response.content.strip().strip('`').removeprefix('json').strip()
            data = json.loads(text)
            score = data.get("score", 0)
            gaps = data.get("gaps", [])
        except Exception as e:
            print(f"Failed to parse critic output for '{sub_question}': {response.content}")
            score = 0
            gaps = ["Failed to generate a valid critique."]
            
        critique[sub_question] = score
        if score < settings.MIN_QUALITY_SCORE:
            all_gaps.extend(gaps)

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
