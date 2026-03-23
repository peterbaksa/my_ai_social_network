import asyncio
import logging
from dataclasses import dataclass, field
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from src.agent.agent import Agent, AgentPersona
from src.agent.memory import AgentMemory
from src.database.repository import Repository
from src.simulation.engine import SimulationEngine
from src.web.schemas import AgentSchema, ConfigResponse, SimulationConfigSchema
from src.web.websocket import ConnectionManager

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="AI Social Network")
manager = ConnectionManager()


@dataclass
class SimulationState:
    """Mutable runtime config — populated by main.py, editable via REST API."""
    topic: str = ""
    model: str = "llama3.1:8b"
    temperature: float = 0.8
    iterations: int = 50
    max_memory_items: int = 10
    seed_post_agent: str = ""
    seed_post_content: str = ""
    agents: list[Agent] = field(default_factory=list)
    db_path: Path = Path("data/simulation.db")
    _engine: SimulationEngine | None = None


sim_state = SimulationState()


def _build_engine() -> SimulationEngine:
    repository = Repository(sim_state.db_path)
    # Reset agent memories for a fresh run
    for agent in sim_state.agents:
        agent.memory = AgentMemory(max_items=sim_state.max_memory_items)

    seed_post = None
    if sim_state.seed_post_agent and sim_state.seed_post_content:
        seed_post = {"agent": sim_state.seed_post_agent, "content": sim_state.seed_post_content}

    engine = SimulationEngine(
        agents=sim_state.agents,
        repository=repository,
        topic=sim_state.topic,
        model=sim_state.model,
        temperature=sim_state.temperature,
        iterations=sim_state.iterations,
        seed_post=seed_post,
    )
    sim_state._engine = engine
    return engine


def _agent_to_schema(agent: Agent) -> AgentSchema:
    return AgentSchema(
        file_key=agent.file_key,
        name=agent.persona.name,
        age=agent.persona.age,
        traits=agent.persona.traits,
        background=agent.persona.background,
        current_focus=agent.persona.current_focus,
        opinion_stance=agent.persona.opinion_stance,
        sentiment_bias=agent.persona.sentiment_bias,
    )


# ── HTML ────────────────────────────────────────────────
@app.get("/")
async def index():
    index_file = STATIC_DIR / "index.html"
    return HTMLResponse(content=index_file.read_text(encoding="utf-8"))


# ── Config API ──────────────────────────────────────────
@app.get("/api/config", response_model=ConfigResponse)
async def get_config():
    return ConfigResponse(
        simulation=SimulationConfigSchema(
            topic=sim_state.topic,
            iterations=sim_state.iterations,
            model=sim_state.model,
            temperature=sim_state.temperature,
            max_memory_items=sim_state.max_memory_items,
            seed_post_agent=sim_state.seed_post_agent,
            seed_post_content=sim_state.seed_post_content,
        ),
        agents=[_agent_to_schema(a) for a in sim_state.agents],
    )


@app.put("/api/config")
async def update_config(config: SimulationConfigSchema):
    sim_state.topic = config.topic
    sim_state.iterations = config.iterations
    sim_state.model = config.model
    sim_state.temperature = config.temperature
    sim_state.max_memory_items = config.max_memory_items
    sim_state.seed_post_agent = config.seed_post_agent
    sim_state.seed_post_content = config.seed_post_content
    return {"status": "ok"}


# ── Agents API ──────────────────────────────────────────
@app.get("/api/agents", response_model=list[AgentSchema])
async def get_agents():
    return [_agent_to_schema(a) for a in sim_state.agents]


@app.post("/api/agents", response_model=AgentSchema)
async def create_agent(data: AgentSchema):
    # Generate file_key from name if not provided
    file_key = data.file_key or data.name.lower().replace(" ", "_").replace(".", "")
    persona = AgentPersona(
        name=data.name,
        age=data.age,
        traits=data.traits,
        background=data.background,
        current_focus=data.current_focus,
        opinion_stance=data.opinion_stance,
        sentiment_bias=data.sentiment_bias,
    )
    agent = Agent(persona=persona, memory=AgentMemory(max_items=sim_state.max_memory_items), file_key=file_key)
    sim_state.agents.append(agent)
    return _agent_to_schema(agent)


@app.put("/api/agents/{file_key}", response_model=AgentSchema)
async def update_agent(file_key: str, data: AgentSchema):
    for agent in sim_state.agents:
        if agent.file_key == file_key:
            agent.persona.name = data.name
            agent.persona.age = data.age
            agent.persona.traits = data.traits
            agent.persona.background = data.background
            agent.persona.current_focus = data.current_focus
            agent.persona.opinion_stance = data.opinion_stance
            agent.persona.sentiment_bias = data.sentiment_bias
            return _agent_to_schema(agent)
    raise HTTPException(status_code=404, detail="Agent not found")


@app.delete("/api/agents/{file_key}")
async def delete_agent(file_key: str):
    for i, agent in enumerate(sim_state.agents):
        if agent.file_key == file_key:
            sim_state.agents.pop(i)
            return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Agent not found")


# ── WebSocket ───────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "start":
                # Stop any running simulation first
                if sim_state._engine is not None:
                    sim_state._engine.stop()
                    await asyncio.sleep(0.1)
                engine = _build_engine()
                engine.set_event_callback(manager.broadcast)
                asyncio.create_task(engine.run(resume=False))
            elif data == "resume":
                if sim_state._engine is not None:
                    sim_state._engine.stop()
                    await asyncio.sleep(0.1)
                engine = _build_engine()
                engine.set_event_callback(manager.broadcast)
                asyncio.create_task(engine.run(resume=True))
            elif data == "stop" and sim_state._engine is not None:
                sim_state._engine.stop()
    except WebSocketDisconnect:
        manager.disconnect(websocket)