# 🚀 ResearchPilot

ResearchPilot is an **autonomous AI research orchestration system**. Unlike standard chatbots that provide reactive, surface-level answers, ResearchPilot utilizes a directed acyclic graph (DAG) of specialized AI agents to autonomously plan, scrape the web, self-correct, and synthesize deep research reports.

![ResearchPilot Architecture](https://img.shields.io/badge/Architecture-LangGraph-blue)
![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)
![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- **Agentic Pipeline (LangGraph)**: Uses a 5-node state machine:
  1. `Planner`: Breaks complex queries into 3 targeted sub-questions.
  2. `Researchers`: A parallel Map-Reduce node that spawns 3 concurrent sub-agents to autonomously scrape the web using the Tavily API.
  3. `Critic (Self-Correction Loop)`: Evaluates findings (0-10 score) and conditionally routes back to the Planner if the data quality is too low (< 6.0).
  4. `Synthesizer`: Compiles approved findings into a styled Markdown report.
  5. `Grader`: Assigns a final Confidence Score to the report.
- **Real-Time Observability (SSE)**: The FastAPI backend streams the internal thoughts and state transitions of the agents via Server-Sent Events (SSE). 
- **Premium Frontend**: A React/Vite application built with Tailwind CSS v3, Shadcn UI, and Framer Motion. Features a deep dark mode "Glassmorphism" aesthetic with real-time animated graph visualizations.

### Graph Architecture

```mermaid
%%{init: {'flowchart': {'curve': 'linear'}}}%%
graph TD;
	__start__([__start__]):::first
	planner(planner)
	researcher(researcher)
	critic(critic)
	synthesizer(synthesizer)
	grader(grader)
	__end__([__end__]):::last
	
	__start__ --> planner;
	critic -.-> planner;
	critic -.-> synthesizer;
	planner -.-> researcher;
	researcher --> critic;
	synthesizer --> grader;
	grader --> __end__;
	
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc
```

---

## 🛠️ Tech Stack

- **AI Orchestration**: LangGraph, LangChain
- **Backend**: FastAPI, Uvicorn, SSE-Starlette, SQLAlchemy (AsyncPG for PostgreSQL)
- **Frontend**: React 19, Vite, TypeScript, Tailwind CSS, Framer Motion, Shadcn UI
- **Deployment**: Render (Infrastructure as Code via `render.yaml`)

---

## 🚀 Quickstart (Local Development)

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- Docker (for PostgreSQL)

### 2. Environment Setup
Create a `.env` file in the root directory and add your API keys:
```env
PORT=8000
ENVIRONMENT=development
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/researchpilot
CLIENT_URL=http://localhost:5173

GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
```

### 3. Start the Database
```bash
docker-compose up -d
```

### 4. Start the Backend
```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
python main.py
```

### 5. Start the Frontend
Open a new terminal window:
```bash
cd client
npm install
npm run dev
```

Visit `http://localhost:5173` in your browser. Type a query, hit Send, and watch the agents go to work!

---

## ☁️ Deployment

ResearchPilot is configured for 1-click deployment to **Render** using the included `render.yaml` Blueprint.

1. Connect your GitHub repository to Render (Blueprints).
2. Render will autonomously spin up the FastAPI Web Service and build the React Static Site.
3. Input your API Keys (`GEMINI_API_KEY`, `GROQ_API_KEY`, `TAVILY_API_KEY`) securely in the Render dashboard when prompted.
