from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from server.config import settings

# 1. Initialize the FastAPI application
app = FastAPI(
    title="ResearchPilot API",
    description="Backend API for the autonomous research agent.",
    version="1.0.0"
)

# 2. Add CORS Middleware
# CORS (Cross-Origin Resource Sharing) is a security feature in browsers.
# Since our React frontend will run on a different port (e.g., localhost:5173),
# we must explicitly tell FastAPI to "allow" requests from that frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CLIENT_URL, "http://localhost:5173"], # Allows the React frontend to talk to us
    allow_credentials=True,
    allow_methods=["*"], # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

# 3. Create a simple health check route
# This is a standard practice to make sure the API is actually running.
@app.get("/")
async def health_check():
    return {
        "status": "online",
        "message": "ResearchPilot API is up and running!"
    }

from server.routes import research

app.include_router(research.router)

if __name__ == "__main__":
    # 4. Start the Uvicorn server if this file is run directly
    print("🚀 Starting FastAPI Server...")
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
