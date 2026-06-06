from pydantic import BaseModel, Field
from typing import Literal

class ResearchRequest(BaseModel):
    """
    This schema defines what data the React frontend is allowed to send to us 
    when starting a new research task.
    """
    query: str = Field(..., description="The user's research topic or question", min_length=5)
    search_depth: Literal["basic", "advanced"] = Field(
        default="basic", 
        description="How deep the search should go"
    )

class ResearchResponse(BaseModel):
    """
    This schema defines the shape of the immediate response we send back to the frontend
    after they submit a ResearchRequest.
    """
    session_id: str
    message: str
