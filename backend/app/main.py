import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import adversaries, agents, events, goals, input, journal, succession
from app.config import settings
from app.db.connection import close_db, init_db

orchestrator_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    global orchestrator_task
    if settings.anthropic_api_key:
        from app.llm.anthropic import AnthropicProvider
        from app.orchestrator.scheduler import Orchestrator
        provider = AnthropicProvider(api_key=settings.anthropic_api_key)
        orch = Orchestrator(provider=provider)
        app.state.orchestrator = orch
        orchestrator_task = asyncio.create_task(orch.start())
    yield
    if orchestrator_task:
        app.state.orchestrator.running = False
        orchestrator_task.cancel()
    await close_db()

app = FastAPI(title="Fantastic Harness", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(goals.router)
app.include_router(agents.router)
app.include_router(events.router)
app.include_router(input.router)
app.include_router(adversaries.router)
app.include_router(journal.router)
app.include_router(succession.router)

@app.get("/health")
async def health():
    return {"status": "ok"}
