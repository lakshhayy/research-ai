# ResearchPilot — Multi-Agent Deep Research System | Master Project Plan

## Context For AI Assistant

I am building **ResearchPilot** — a multi-agent AI research system where a user types any research query ("What are the best backend frameworks in 2025 and why?") and a LangGraph-orchestrated pipeline of 5 specialized agents autonomously plans sub-questions, searches the web in parallel, critiques findings, retries weak research branches, and synthesizes a structured markdown report with sources, confidence score, and follow-up questions.

The agent graph uses **LangGraph's StateGraph** with conditional edges — the Critic agent evaluates research quality and dynamically decides whether to loop back for more research or proceed to synthesis. This is NOT a linear chain — it is a genuine reasoning graph that evaluates its own output quality.

**Three unique differentiating features:**
1. **Conditional Retry Loop** — Critic scores each research branch 0–10; branches below threshold trigger targeted re-search (max 2 retries per branch) — the system self-evaluates and self-corrects
2. **Parallel Researcher Execution** — LangGraph's `Send` API fans out one researcher agent per sub-question simultaneously, then fans back in at the Critic — map-reduce pattern
3. **Live Graph Execution Stream** — Frontend shows which node is currently active in real-time via SSE, with findings accumulating live as each researcher finishes

### How We Are Building This
- I will ask you for **one chunk of code at a time**, per the weekly plan below
- Each chunk should be **focused, complete, and explained briefly**
- Do NOT generate the entire app at once
- Do NOT skip steps or combine weeks
- Always write in **Python** for the backend unless specified
- Always write in **TypeScript + React** for the frontend unless specified
- Always match the **exact folder structure** defined below
- When I say "next chunk", give me the next logical piece

---

## Tech Stack

### Frontend
- React + TypeScript + Vite
- Tailwind CSS
- Shadcn/ui (component library)
- TanStack Query (react-query) for API calls
- React Router v6
- EventSource API (native browser SSE consumer)
- TanStack Table (for structured result rendering)

### Backend
- **Python 3.11+**
- **FastAPI** — async HTTP framework
- **Uvicorn** — ASGI server
- **Pydantic v2** — data validation + typed models
- Python-dotenv for env management
- HTTPX for async HTTP calls

### Agent Orchestration
- **LangGraph** — StateGraph, nodes, conditional edges, Send API
- **LangChain** — tool wrappers, LLM interfaces, memory
- **LangChain-Google-GenAI** — Gemini integration
- **LangChain-Groq** — Groq/Llama fallback LLM
- **Tavily Python SDK** — web search tool built for LLM agents (free tier)

### LLM Providers
- **Primary:** Google Gemini 1.5 Flash (`gemini-1.5-flash`) — free tier, fast, strong reasoning
- **Fallback:** Groq `llama-3.1-8b-instant` — free tier, low latency
- Model is swappable by changing one config variable

### Database
- **PostgreSQL**
- **SQLAlchemy 2.0** (async) — ORM
- **Alembic** — migrations
- JSONB columns for findings and structured results

### Infrastructure
- Redis (optional for future job queue — not used in MVP)
- **Railway** — backend + PostgreSQL hosting
- **Vercel** — frontend hosting
- **Docker + docker-compose** — local dev

### Streaming
- **FastAPI SSE** via `sse-starlette` library
- Streams graph execution events (node start, node finish, findings, final report) to frontend
- Same conceptual pattern as WebSockets but simpler — server → client only

---

## Folder Structure

```
researchpilot/
├── server/
│   ├── agents/
│   │   ├── planner.py           → query → list of sub-questions
│   │   ├── researcher.py        → sub-question + Tavily → findings dict
│   │   ├── critic.py            → findings → scores dict + gaps list
│   │   ├── synthesizer.py       → all findings → structured markdown report
│   │   └── grader.py            → report → confidence score + follow-up questions
│   ├── graph/
│   │   ├── state.py             → ResearchState TypedDict definition
│   │   ├── nodes.py             → each agent wrapped as a LangGraph node function
│   │   ├── edges.py             → conditional edge functions (should_retry etc.)
│   │   └── builder.py           → StateGraph construction, node wiring, compilation
│   ├── tools/
│   │   └── search.py            → Tavily search tool + LangChain wrapper
│   ├── db/
│   │   ├── connection.py        → SQLAlchemy async engine + session
│   │   ├── models.py            → ORM models for research_sessions + research_steps
│   │   └── migrations/          → Alembic migration files
│   ├── routes/
│   │   ├── research.py          → POST /research, GET /research/:id, SSE stream
│   │   └── health.py            → GET /health
│   ├── services/
│   │   └── sse.py               → SSE event registry + emit helpers
│   ├── config.py                → all env vars + settings via Pydantic BaseSettings
│   └── main.py                  → FastAPI app entry, middleware, router registration
│
├── client/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/              → shadcn components
│   │   │   ├── QueryInput.tsx   → research query input + submit button
│   │   │   ├── GraphVisualizer.tsx → live pipeline diagram (nodes lighting up)
│   │   │   ├── FindingsStream.tsx  → findings appearing per researcher as they finish
│   │   │   ├── ReportViewer.tsx → final markdown report renderer
│   │   │   ├── ConfidenceBadge.tsx → confidence % + color indicator
│   │   │   └── FollowUpChips.tsx → clickable follow-up question chips
│   │   ├── pages/
│   │   │   ├── Home.tsx         → query input + live graph + report
│   │   │   ├── History.tsx      → all past research sessions
│   │   │   └── SessionDetail.tsx → full replay of any past session
│   │   ├── hooks/
│   │   │   ├── useResearchSSE.ts → consumes SSE stream for live graph events
│   │   │   └── useSessions.ts    → TanStack Query for session CRUD
│   │   ├── lib/
│   │   │   └── api.ts           → axios instance pointing to FastAPI backend
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── index.html
│   └── vite.config.ts
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Database Schema

```
research_sessions
  id                (uuid, pk)
  query             (text)                         ← user's original research question
  status            (enum: 'running' | 'completed' | 'failed')
  sub_questions     (jsonb, nullable)              ← list of sub-questions from Planner
  findings          (jsonb, nullable)              ← dict: sub_question → findings text
  critique          (jsonb, nullable)              ← dict: sub_question → score (0-10)
  retry_count       (integer, default 0)           ← how many retry loops happened
  final_report      (text, nullable)               ← synthesized markdown report
  confidence_score  (float, nullable)              ← 0.0 to 1.0
  follow_up_questions (jsonb, nullable)            ← list of suggested follow-up queries
  sources           (jsonb, nullable)              ← list of source URLs
  error             (text, nullable)
  created_at        (timestamp)
  completed_at      (timestamp, nullable)

research_steps
  id                (uuid, pk)
  session_id        (fk → research_sessions)
  step_number       (integer)
  node_name         (text)                         ← 'planner' | 'researcher' | 'critic' | 'synthesizer' | 'grader'
  sub_question      (text, nullable)               ← for researcher steps
  input_data        (jsonb)                        ← what was passed to this node
  output_data       (jsonb)                        ← what the node returned
  duration_ms       (integer)                      ← how long this node took
  created_at        (timestamp)
```

---

## API Routes

```
RESEARCH
POST   /api/research                → submit query → run graph → return session_id
GET    /api/research                → get all sessions (history, paginated, newest first)
GET    /api/research/:id            → get full session detail + all steps
DELETE /api/research/:id            → cancel a running session

STREAMING
GET    /api/research/:id/stream     → SSE endpoint — streams live graph events as session runs

HEALTH
GET    /api/health                  → server health check
```

---

## The Graph State (Core of LangGraph)

```python
# server/graph/state.py

from typing import TypedDict, Annotated
import operator

class ResearchState(TypedDict):
    # Input
    query: str
    session_id: str

    # Planner output
    sub_questions: list[str]

    # Researcher output — Annotated[list, operator.add] means findings ACCUMULATE
    # across parallel researcher nodes instead of overwriting each other
    findings: Annotated[list[dict], operator.add]

    # Critic output
    critique: dict                    # { sub_question: score (0-10) }
    gaps: list[str]                   # sub-questions that scored too low

    # Loop control
    retry_count: int                  # how many retry loops have happened

    # Synthesizer output
    final_report: str

    # Grader output
    confidence_score: float
    follow_up_questions: list[str]
    sources: list[str]
```

This single file is what interviewers will ask about. The `Annotated[list, operator.add]` on `findings` is what enables parallel researchers to each write their own findings without clobbering each other — LangGraph merges them automatically.

---

## The Agent Graph (Visual)

```
              [User Query]
                   ↓
            ┌─────────────┐
            │   PLANNER   │  → breaks query into 3-5 sub-questions
            └──────┬──────┘
                   ↓ (LangGraph Send API — one per sub-question)
         ┌─────────────────────────┐
         │   PARALLEL RESEARCHERS  │
         │  [R1] [R2] [R3] [R4]   │  → each searches Tavily for its sub-question
         │  (all run at same time) │  → findings accumulate in state via operator.add
         └──────────┬──────────────┘
                    ↓
            ┌─────────────┐
            │    CRITIC   │  → scores each finding 0-10, identifies gaps
            └──────┬──────┘
                   ↓
       ┌───────────────────────────┐
       │     CONDITIONAL EDGE      │
       │  avg_score < 6.0          │
       │  AND retry_count < 2  ────┼──→ back to PARALLEL RESEARCHERS (retry weak branches)
       │                           │
       │  avg_score >= 6.0         │
       │  OR retry_count >= 2  ────┼──→ SYNTHESIZER
       └───────────────────────────┘
                   ↓
            ┌─────────────┐
            │ SYNTHESIZER │  → combines all findings into structured markdown report
            └──────┬──────┘
                   ↓
            ┌─────────────┐
            │   GRADER    │  → confidence score + follow-up questions
            └──────┬──────┘
                   ↓
            [Final Report]
```

---

## The Conditional Edge (The Key Differentiator)

```python
# server/graph/edges.py

from .state import ResearchState

def should_retry(state: ResearchState) -> str:
    """
    Called by LangGraph after every Critic node execution.
    Returns either 'retry' (loops back to researchers) or 'synthesize' (proceeds forward).
    This is what makes ResearchPilot an AGENT, not just a pipeline.
    """
    critique = state.get("critique", {})
    retry_count = state.get("retry_count", 0)

    if not critique:
        return "synthesize"

    scores = list(critique.values())
    avg_score = sum(scores) / len(scores) if scores else 0

    # Only retry if quality is low AND we haven't exhausted retries
    if avg_score < 6.0 and retry_count < 2:
        return "retry"

    return "synthesize"
```

---

## How The Graph Runs (Read This — It Is The Core)

```
User submits: "What are the best backend frameworks in 2025?"
        ↓
POST /api/research → session row created (status: running) → graph.ainvoke() called async
        ↓
Frontend opens SSE stream: GET /api/research/:id/stream
        ↓
┌──────────────────────────── GRAPH EXECUTION ───────────────────────────────┐
│                                                                             │
│  Node 1 — PLANNER                                                           │
│    Input:  query = "What are the best backend frameworks in 2025?"         │
│    Action: Gemini call → returns 4 sub-questions                            │
│    Output: state.sub_questions = [Q1, Q2, Q3, Q4]                          │
│    SSE:    emit { type: 'node_complete', node: 'planner', data: [...] }     │
│                                                                             │
│  Node 2 — RESEARCHERS (parallel via Send API)                              │
│    Input:  one sub-question each                                            │
│    Action: each calls Tavily search + Gemini summarizes results             │
│    Output: findings accumulate in state.findings (operator.add)             │
│    SSE:    emit per researcher as it finishes (frontend shows live)         │
│                                                                             │
│  Node 3 — CRITIC                                                            │
│    Input:  state.findings (all 4)                                           │
│    Action: Gemini scores each finding + identifies gaps                     │
│    Output: state.critique = { Q1: 8, Q2: 4, Q3: 7, Q4: 3 }               │
│    SSE:    emit { type: 'node_complete', node: 'critic', scores: {...} }    │
│                                                                             │
│  Conditional Edge:                                                          │
│    avg_score = (8+4+7+3)/4 = 5.5 → BELOW 6.0 → retry                     │
│    retry_count becomes 1                                                    │
│    Only Q2 and Q4 (low scorers) go back to Researcher                      │
│                                                                             │
│  Node 2 again — RESEARCHERS (only weak branches)                           │
│    Q2 and Q4 re-searched with more specific queries                        │
│    New findings replace old findings for those sub-questions                │
│                                                                             │
│  Node 3 again — CRITIC                                                      │
│    New avg_score = 7.2 → ABOVE 6.0 → proceed                              │
│                                                                             │
│  Node 4 — SYNTHESIZER                                                       │
│    Input:  all findings (original Q1/Q3 + retried Q2/Q4)                  │
│    Action: Gemini writes structured markdown report                         │
│    Output: state.final_report                                               │
│                                                                             │
│  Node 5 — GRADER                                                            │
│    Input:  final_report                                                     │
│    Action: Gemini scores overall quality + generates follow-up questions    │
│    Output: confidence_score = 0.81, follow_up_questions = [...]            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
        ↓
Session updated: status = 'completed', all fields saved to DB
        ↓
SSE emits: { type: 'done', report: '...', confidence: 0.81, follow_ups: [...] }
        ↓
Frontend renders full report
```

---

## How SSE Streaming Works

```
Client opens: GET /api/research/:id/stream
        ↓
Server registers the response in SSE registry (dict: session_id → list[StreamingResponse])
        ↓
As graph nodes execute inside graph.ainvoke():
  → After each node: call sse.emit(session_id, event_data)
  → Server writes: data: { type: 'node_complete', node: 'planner', ... }\n\n
        ↓
Frontend EventSource receives each event
  → Updates GraphVisualizer (lights up completed nodes)
  → Appends findings to FindingsStream as researchers finish
        ↓
On graph finish: server sends { type: 'done', report, confidence, follow_ups }
Frontend renders ReportViewer
```

### SSE Event Types

```typescript
// What the frontend receives over the stream

{ type: 'node_start',    node: 'planner' }
{ type: 'node_complete', node: 'planner',     data: { sub_questions: [...] } }
{ type: 'node_start',    node: 'researcher',  sub_question: 'Q1' }
{ type: 'node_complete', node: 'researcher',  sub_question: 'Q1', findings: '...' }
{ type: 'node_start',    node: 'critic' }
{ type: 'node_complete', node: 'critic',      scores: { Q1: 8, Q2: 4 }, retrying: true }
{ type: 'retry',         retry_count: 1,      weak_branches: ['Q2', 'Q4'] }
{ type: 'node_start',    node: 'synthesizer' }
{ type: 'node_complete', node: 'synthesizer', report: '...' }
{ type: 'node_complete', node: 'grader',      confidence: 0.81, follow_ups: [...] }
{ type: 'done',          session_id: '...',   report: '...', confidence: 0.81 }
{ type: 'error',         message: '...' }
```

---

## Agent Prompts (What Each Agent Is Told)

### Planner
```
You are a research planning agent. Your job is to decompose a research query into
3-5 specific, non-overlapping sub-questions that together fully cover the topic.

Rules:
- Each sub-question must be answerable with a web search
- Sub-questions must not overlap or repeat each other
- Cover different angles: current state, comparisons, trends, opinions, data

Query: {query}

Return ONLY a JSON array of strings. No preamble. No markdown.
Example: ["What are the most used backend frameworks in 2025?", "..."]
```

### Researcher
```
You are a research agent. You have been given a specific sub-question to research.
You have access to a web search tool. Use it to find relevant, current information.

Sub-question: {sub_question}

Instructions:
- Search for 2-3 different queries related to the sub-question
- Synthesize the findings into a clear, factual summary (150-250 words)
- Include specific data points, names, and numbers where available
- List the sources you used

Return a JSON object: { "summary": "...", "sources": ["url1", "url2"], "key_points": ["..."] }
```

### Critic
```
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

Return ONLY a JSON object: { "score": 7, "gaps": ["missing X", "needs more Y"] }
```

### Synthesizer
```
You are a research synthesis agent. Combine research findings from multiple sub-questions
into a single coherent, well-structured markdown report.

Original query: {query}
Research findings: {all_findings}

Report structure:
## [Title]
### Executive Summary (2-3 sentences)
### [Section per major theme found in findings]
### Key Takeaways (bullet points)
### Sources

Rules:
- Write for a technical audience
- Use markdown formatting
- Do not repeat information across sections
- Be specific — include numbers, names, dates where available
```

### Grader
```
You are a research quality grader. Read the final report and assess its overall quality.

Report: {report}
Original query: {query}

Return ONLY a JSON object:
{
  "confidence_score": 0.82,       // 0.0 to 1.0
  "reasoning": "...",             // one sentence explaining the score
  "follow_up_questions": [        // 3 questions the user might want to ask next
    "...",
    "...",
    "..."
  ]
}
```

---

## Environment Variables

### server/.env
```
PORT=8000
ENVIRONMENT=development
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/researchpilot
CLIENT_URL=http://localhost:5173
GEMINI_API_KEY=               ← free from aistudio.google.com
GROQ_API_KEY=                 ← free from console.groq.com
TAVILY_API_KEY=               ← free from tavily.com (1000 searches/month free)
MAX_RETRY_COUNT=2
MIN_QUALITY_SCORE=6.0
MAX_SUB_QUESTIONS=5
```

### client/.env
```
VITE_API_URL=http://localhost:8000
```

---

## 3-Week Build Plan

---

### WEEK 1 — Core Agent Graph (Python + LangGraph + No HTTP Yet)

**Goal:** The full 5-node graph runs end-to-end in a Python script. No FastAPI, no frontend. Just prove the graph works.

---

#### Chunk 1.1 — Python project setup
- Initialize `server/` as a Python project
- `pyproject.toml` or `requirements.txt` with all dependencies:
  `fastapi, uvicorn, langgraph, langchain, langchain-google-genai, langchain-groq, tavily-python, sqlalchemy[asyncio], asyncpg, alembic, pydantic, pydantic-settings, python-dotenv, sse-starlette`
- `server/config.py` — Pydantic `BaseSettings` class loading all env vars
- `server/main.py` — bare FastAPI app with just GET /api/health returning `{ status: "ok" }`
- Verify: `uvicorn main:app --reload` runs without errors

#### Chunk 1.2 — Database setup
- `server/db/models.py` — SQLAlchemy models for `research_sessions` + `research_steps`
- `server/db/connection.py` — async engine + `AsyncSession` factory
- Alembic init + first migration
- Verify: tables created in PostgreSQL via `alembic upgrade head`

#### Chunk 1.3 — Tavily search tool
- `server/tools/search.py`
- `tavily_search(query: str, max_results: int = 5) → list[dict]` async function
- Each result: `{ title, url, content, score }`
- LangChain `Tool` wrapper so it can be passed to agents
- Test script: search for "best backend frameworks 2025" → print results

#### Chunk 1.4 — Graph state
- `server/graph/state.py`
- Full `ResearchState` TypedDict as defined above
- Explain every field and the `Annotated[list, operator.add]` pattern

#### Chunk 1.5 — Planner agent
- `server/agents/planner.py`
- `run_planner(state: ResearchState) → dict` async function
- Calls Gemini with the planner prompt
- Parses JSON response → list of sub-questions
- Returns `{ "sub_questions": [...] }`
- Test: hardcode a query, run planner, print sub-questions

#### Chunk 1.6 — Researcher agent
- `server/agents/researcher.py`
- `run_researcher(state: ResearchState) → dict` async function
- Called once per sub-question (parallel via Send API later)
- Calls Tavily search + Gemini summarizes results
- Returns `{ "findings": [{ "sub_question": "...", "summary": "...", "sources": [...], "key_points": [...] }] }`
- Note: returns a LIST so operator.add accumulates across parallel calls

#### Chunk 1.7 — Critic agent
- `server/agents/critic.py`
- `run_critic(state: ResearchState) → dict`
- Scores each finding in `state.findings` using Gemini
- Returns `{ "critique": { sub_question: score }, "gaps": [...], "retry_count": N+1 }`

#### Chunk 1.8 — Synthesizer + Grader agents
- `server/agents/synthesizer.py` → takes all findings → returns `{ "final_report": "..." }`
- `server/agents/grader.py` → takes report → returns `{ "confidence_score": 0.X, "follow_up_questions": [...], "sources": [...] }`

#### Chunk 1.9 — Graph builder + conditional edge
- `server/graph/edges.py` — `should_retry(state) → "retry" | "synthesize"`
- `server/graph/nodes.py` — wrap each agent as a LangGraph node function
- `server/graph/builder.py`:
  - Build `StateGraph(ResearchState)`
  - Add all 5 nodes
  - Wire edges including `add_conditional_edges` after Critic
  - Compile graph → `app = graph.compile()`
- Test script in `server/test_graph.py`:
  - `asyncio.run(app.ainvoke({ "query": "...", "session_id": "test-123" }))`
  - Print final state
  - Verify retry loop triggers if scores are low

**Week 1 Checklist:**
- [ ] FastAPI server starts without errors
- [ ] PostgreSQL tables created via Alembic
- [ ] Tavily search returns results for any query
- [ ] Planner breaks query into 3-5 sub-questions
- [ ] Researcher returns findings for a sub-question
- [ ] Critic scores findings and identifies gaps
- [ ] Conditional edge routes to retry or synthesize correctly
- [ ] Retry loop increments retry_count and caps at MAX_RETRY_COUNT
- [ ] Synthesizer produces a coherent markdown report
- [ ] Grader returns confidence score + follow-up questions
- [ ] Full graph test script runs end-to-end ✅

---

### WEEK 2 — FastAPI Routes + SSE Streaming + DB Persistence

**Goal:** Submit a research query via HTTP, watch it run via SSE, find result in DB.

---

#### Chunk 2.1 — SSE service
- `server/services/sse.py`
- `sse_registry: dict[str, list[asyncio.Queue]]` — one queue per connected client per session
- `register_client(session_id) → asyncio.Queue`
- `emit(session_id, event: dict)` — puts event on all queues for that session
- `deregister_client(session_id, queue)`
- Using queues instead of raw Response objects — cleaner for async FastAPI

#### Chunk 2.2 — Graph with SSE integration
- Modify each node in `server/graph/nodes.py` to call `sse.emit()` after completion
- Emit `node_start` before each node, `node_complete` after
- Emit `retry` event when conditional edge routes back
- Emit `done` event when grader finishes
- SSE events should match the event type schema defined above

#### Chunk 2.3 — Research HTTP routes
- `server/routes/research.py`
- `POST /api/research`:
  - Validate request body: `{ query: str }` (Pydantic model, max 500 chars)
  - Create `research_sessions` row (status: running)
  - Launch `graph.ainvoke()` as a background task (`asyncio.create_task`)
  - Return `{ session_id }` immediately (non-blocking)
- `GET /api/research` — paginated list of sessions, newest first
- `GET /api/research/:id` — session detail + all steps
- `DELETE /api/research/:id` — mark session as cancelled (graph checks this)

#### Chunk 2.4 — SSE stream route
- `server/routes/research.py` — add streaming endpoint
- `GET /api/research/:id/stream`
- Uses `sse-starlette` `EventSourceResponse`
- Registers client queue, yields events as they arrive
- If session already completed: immediately send all steps + done event (replay mode)
- Handles client disconnect cleanup

#### Chunk 2.5 — DB persistence inside graph
- After each node completes: save a `research_steps` row to DB
- On graph finish: update `research_sessions` with all final fields
- On graph error: update status = 'failed', save error message
- Use SQLAlchemy async session properly (no blocking calls)

#### Chunk 2.6 — End-to-end integration test
- POST a research query via curl → get session_id
- Open SSE stream in second terminal → watch events arrive
- Verify final session row in DB has correct status + report
- Test query: "What are the most popular programming languages in 2025 and what are they used for?"

**Week 2 Checklist:**
- [ ] POST /api/research creates session + starts graph in background
- [ ] SSE stream delivers node events in real-time
- [ ] Retry events visible in SSE stream when triggered
- [ ] All steps saved to research_steps table
- [ ] Final session row has report, confidence, follow_ups, sources
- [ ] Session status transitions: running → completed (or failed)
- [ ] Replay mode works: SSE on completed session sends all steps immediately
- [ ] Error handling: failed sessions saved with error message

---

### WEEK 3 — Frontend: Live Graph UI + Report Viewer

**Goal:** User submits query from browser, watches agents run live, reads final report.

---

#### Chunk 3.1 — React project setup
- Vite + React + TypeScript scaffold in `client/`
- Tailwind CSS + Shadcn/ui installed
- React Router v6: routes for `/` (Home), `/history` (History), `/sessions/:id` (Detail)
- Axios instance in `client/src/lib/api.ts` pointing to FastAPI backend

#### Chunk 3.2 — QueryInput component
- Large textarea for research query
- Submit button → POST /api/research → stores session_id in state → opens SSE stream
- Character counter (max 500)
- 4 example queries as clickable chips:
  - "What are the best backend frameworks in 2025 and why?"
  - "Compare Rust vs Go for systems programming in 2025"
  - "What is the current state of LLM agent frameworks?"
  - "What are the top open source projects gaining traction this year?"

#### Chunk 3.3 — useResearchSSE hook
- `client/src/hooks/useResearchSSE.ts`
- Opens `EventSource` to `GET /api/research/:id/stream`
- Maintains state: `activeNode`, `completedNodes`, `findings[]`, `isComplete`, `finalReport`, `confidence`, `followUps`
- Updates state as each SSE event arrives
- Handles `done`, `error`, `retry` events
- Closes EventSource on unmount or on `done`

#### Chunk 3.4 — GraphVisualizer component
- Shows the 5 nodes as boxes connected by arrows: Planner → Researchers → Critic → Synthesizer → Grader
- Active node: glowing/pulsing animation
- Completed node: green checkmark
- Retry loop: animated arrow going back from Critic to Researchers with retry count shown
- Researchers box shows N parallel agents (e.g. "4 researchers running")

#### Chunk 3.5 — FindingsStream component
- As each researcher finishes: a card appears with the sub-question + summary
- Score badge added once Critic runs (green if ≥6, red if <6)
- "Retrying..." label on low-score cards during retry

#### Chunk 3.6 — ReportViewer component
- Renders final markdown report using `react-markdown` + `remark-gfm`
- Confidence badge: color-coded (green >80%, yellow 60-80%, red <60%)
- Sources list with clickable links
- Follow-up question chips — clicking one submits it as a new research query
- "Copy Report" button

#### Chunk 3.7 — Home page
- QueryInput at top
- Once submitted: GraphVisualizer appears below input
- FindingsStream appears as researchers complete
- ReportViewer appears at bottom once done
- Total time taken shown on completion

#### Chunk 3.8 — History + SessionDetail pages
- History: table of past sessions (query truncated, status, confidence, time, created_at)
- Click any row → SessionDetail
- SessionDetail: full replay showing all steps, findings per researcher, final report
- "Research again" button → submits same query

**Week 3 Checklist:**
- [ ] Query submits and session starts from UI
- [ ] GraphVisualizer shows active node in real-time
- [ ] Nodes complete and light up as graph progresses
- [ ] Retry loop visible in GraphVisualizer with counter
- [ ] Findings appear per researcher as they complete
- [ ] Score badges show on findings after Critic runs
- [ ] Final report renders as formatted markdown
- [ ] Confidence badge shows correct color
- [ ] Follow-up chips clickable and submit new query
- [ ] History page lists all past sessions
- [ ] SessionDetail replays full session
- [ ] UI is responsive on mobile

---

## How To Use This Document With AI Assistant

When starting a new coding session, paste this at the top:

> "I am building ResearchPilot — a multi-agent deep research system using LangGraph and FastAPI. Here is the full project plan and context: [paste this document]. I am currently on [Week X, Chunk Y]. Please give me only the code for that specific chunk. Explain each part briefly. Match the exact folder structure defined above."

---

## Interview Questions To Prepare

**"How does your agent decide whether to retry research?"**
→ After the Critic node scores each finding 0-10, a conditional edge function checks if the average score is below 6.0. If yes and retry_count < 2, LangGraph routes back to the Researcher nodes for the weak branches only. This is a cycle in the graph — not possible with a linear LangChain pipeline.

**"What is LangGraph and why did you use it instead of LangChain LCEL?"**
→ LangChain LCEL builds linear chains — input flows through steps sequentially. LangGraph builds stateful graphs — nodes can loop, branch conditionally, and run in parallel. I needed a retry loop (Critic → conditional → Researcher again) which is a cycle. LCEL can't express cycles.

**"How does parallel research work technically?"**
→ LangGraph's `Send` API. The Planner outputs N sub-questions. I use `Send` to dispatch one Researcher node invocation per sub-question — they all execute concurrently. Findings accumulate in the state using `Annotated[list, operator.add]` so parallel writes don't overwrite each other. They fan back in at the Critic node.

**"What is the TypedDict state and why does it matter?"**
→ LangGraph passes a single state object through every node. TypedDict makes it typed and explicit — every node knows exactly what fields exist and what types they are. The `operator.add` reducer on `findings` is how I handle concurrent writes from parallel nodes without race conditions.

**"How do you prevent infinite retry loops?"**
→ `retry_count` field in state. The conditional edge checks `retry_count < 2` before routing back to researchers. After 2 retries, it always proceeds to synthesis regardless of scores.

**"How does the frontend know which node is running in real-time?"**
→ Server-Sent Events. FastAPI registers each connected browser client in a queue registry. As each LangGraph node starts and completes, the graph emits typed events to the SSE service, which pushes them to all connected clients. The React `EventSource` hook maintains a `activeNode` state that drives the GraphVisualizer animations.

**"Why SSE instead of WebSockets for streaming?"**
→ Agent execution events are strictly unidirectional — server pushes to client. SSE is simpler, HTTP-native, auto-reconnects, and works through proxies without a protocol upgrade. WebSockets add bidirectional complexity I don't need.

**"What's your LLM setup and how would you swap models?"**
→ Primary is Gemini 1.5 Flash — fast, free tier, strong reasoning. Fallback is Groq Llama-3.1. The model is configured in one `config.py` file. Since all agents use LangChain's `ChatGoogleGenerativeAI` or `ChatGroq` interface, swapping models is a one-line config change — no agent code changes.

**"How is this different from just calling an LLM API once with a big prompt?"**
→ Three things a single call can't do: (1) parallel execution — four researchers run simultaneously, cutting latency by ~65%; (2) self-evaluation — the Critic independently scores quality, separate from the researcher so there's no self-serving bias; (3) targeted retry — only weak branches get re-researched, not the whole query. A single prompt would be slower, produce lower quality, and have no mechanism to improve its own output.

---

## Resume Bullets (Fill In After Shipping)

```
ResearchPilot — Multi-Agent Deep Research System                  [GitHub] [Live Demo]
Python, LangGraph, LangChain, FastAPI, Gemini API, Tavily, PostgreSQL

• Designed a 5-node LangGraph StateGraph (Planner → Researchers → Critic →
  Synthesizer → Grader) with typed state accumulation using TypedDict and
  operator.add reducers for concurrent-safe parallel writes

• Implemented a self-evaluating retry loop via LangGraph conditional edges —
  Critic node scores each research branch 0-10; branches below threshold
  trigger targeted re-search (max 2 retries), preventing both low-quality
  synthesis and infinite loops

• Parallelized sub-question research using LangGraph's Send API (map-reduce
  pattern) — N researcher agents run concurrently per query, reducing total
  research latency by ~65% vs sequential execution

• Streamed graph execution state (active node, per-researcher findings, retry
  events, final report) to frontend via FastAPI SSE — users watch the agent
  reasoning live, node by node, with retry loops visible in the UI

• Built structured output pipeline using Pydantic models throughout — every
  LLM response parsed and validated before entering graph state, eliminating
  silent failures from malformed JSON

• Deployed on Railway with PostgreSQL persistence — every research session,
  all intermediate steps, and retry history stored for full replay
```

---

## Quick Reference: Key LangGraph Concepts Used

| Concept | Where Used | Why |
|---|---|---|
| `StateGraph(TypedDict)` | `graph/builder.py` | Typed state flowing through all nodes |
| `Annotated[list, operator.add]` | `graph/state.py` | Parallel researcher writes accumulate safely |
| `add_conditional_edges` | `graph/builder.py` | Critic → retry or synthesize decision |
| `Send` API | `graph/nodes.py` | Fan-out one researcher per sub-question |
| `graph.ainvoke()` | `routes/research.py` | Async graph execution |
| `graph.astream()` | Optional upgrade | Stream state updates instead of SSE |
| `interrupt_before` | Optional upgrade | Human-in-the-loop before synthesis |
