import asyncio
from typing import List
from tavily import AsyncTavilyClient
from langchain_core.tools import tool
from server.config import settings

# Initialize the async Tavily client using our config
tavily_client = AsyncTavilyClient(api_key=settings.TAVILY_API_KEY)

async def tavily_search(query: str, max_results: int = 5, search_depth: str = "basic") -> list[dict]:
    """
    Search the web using Tavily API and return a list of results.
    Each result contains: title, url, content, score.
    """
    response = await tavily_client.search(
        query=query, 
        max_results=max_results,
        search_depth=search_depth
    )
    
    # Extract only the fields we care about and truncate content to save tokens!
    results = []
    for raw_result in response.get("results", [])[:3]: # Force max 3 results
        # Truncate content to max 1500 chars to avoid Groq 6000 TPM limit
        content = raw_result.get("content", "")
        if len(content) > 1500:
            content = content[:1500] + "..."
            
        results.append({
            "title": raw_result.get("title"),
            "url": raw_result.get("url"),
            "content": content,
            "score": raw_result.get("score")
        })
        
    return results

# Wrap the async function into a LangChain tool
@tool
async def web_search_tool(query: str) -> list[dict]:
    """
    Search the web for current information. 
    Use this to find facts, news, and research data.
    """
    return await tavily_search(query, max_results=5)

if __name__ == "__main__":
    # Test script to verify it works (run with: python -m server.tools.search)
    import os
    
    # Small check if the API key is set
    if not settings.TAVILY_API_KEY:
        print("Error: TAVILY_API_KEY is not set in your .env file!")
        exit(1)
        
    async def test():
        print("Testing Tavily Search Tool...")
        results = await tavily_search("best backend frameworks 2025")
        for i, res in enumerate(results, 1):
            print(f"\nResult {i}: {res['title']}")
            print(f"URL: {res['url']}")
            print(f"Content snippet: {res['content'][:100]}...")
            
    asyncio.run(test())
