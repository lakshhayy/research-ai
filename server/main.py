from fastapi import FastAPI
from server.config import settings

app = FastAPI(title="ResearchPilot API", version="1.0.0")

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
