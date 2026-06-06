import uuid
import json
import asyncio
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from server.schemas import ResearchRequest
from server.graph.builder import graph

router = APIRouter()

@router.post("/api/research")
async def start_research(request: Request, body: ResearchRequest):
    """
    This endpoint kicks off the LangGraph and streams the updates 
    back to the client using Server-Sent Events (SSE).
    """
    session_id = str(uuid.uuid4())
    
    async def event_generator():
        # 1. Setup the initial state just like we did in test_graph.py
        initial_state = {
            "query": body.query,
            "session_id": session_id,
            "search_depth": body.search_depth,
            "retry_count": 0,
            "findings": []
        }
        
        # We yield a custom dictionary. sse_starlette automatically formats this
        # into the standard `data: {...}\n\n` SSE protocol shape.
        yield {"data": json.dumps({"type": "connected", "session_id": session_id})}
        
        try:
            report = ""
            score = 0.0
            
            # 2. Iterate through the graph as it runs
            async for output in graph.astream(initial_state, stream_mode="updates"):
                
                if await request.is_disconnected():
                    print(f"Client disconnected for session {session_id}. Stopping graph.")
                    break
                    
                for node_name, node_state in output.items():
                    if "final_report" in node_state:
                        report = node_state["final_report"]
                    if "confidence_score" in node_state:
                        score = node_state["confidence_score"]
                        
                    msg = ""
                    if node_name == "planner":
                        msg = f"Planner generated {len(node_state.get('sub_questions', []))} research angles."
                    elif node_name == "researcher":
                        msg = "A researcher finished gathering web data."
                    elif node_name == "critic":
                        msg = "Critic evaluated the research quality."
                    elif node_name == "synthesizer":
                        msg = "Drafting the final markdown report..."
                    elif node_name == "grader":
                        msg = f"Report finalized with confidence score: {score}"
                    
                    if msg:
                        yield {"data": json.dumps({
                            "type": "update",
                            "node": node_name,
                            "message": msg
                        })}
                        
            # 3. Once the graph fully finishes, return the captured data
            yield {"data": json.dumps({
                "type": "complete",
                "report": report,
                "confidence_score": score
            })}
            
        except Exception as e:
            yield {"data": json.dumps({"type": "error", "message": str(e)})}

    # We return an EventSourceResponse which keeps the HTTP connection open!
    return EventSourceResponse(event_generator())
