import asyncio
import logging
from pathlib import Path

import uvicorn
import yaml

from src.agent.agent import Agent
from src.database.repository import Repository
from src.simulation.engine import SimulationEngine
from src.web.app import app, set_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"


def load_settings() -> dict:
    settings_path = CONFIG_DIR / "settings.yaml"
    with open(settings_path) as f:
        return yaml.safe_load(f)


def load_agents(max_memory: int) -> list[Agent]:
    personas_dir = CONFIG_DIR / "personas"
    agents = []
    for persona_file in sorted(personas_dir.glob("*.yaml")):
        with open(persona_file) as f:
            config = yaml.safe_load(f)
        file_key = persona_file.stem
        agent = Agent.from_config(config, file_key=file_key, max_memory=max_memory)
        agents.append(agent)
        logger.info(f"Loaded agent: {agent.name} ({file_key})")
    return agents


def main():
    settings = load_settings()
    sim = settings["simulation"]
    server = settings["server"]

    # Ensure data directory exists
    DATA_DIR.mkdir(exist_ok=True)

    # Load agents
    agents = load_agents(max_memory=sim.get("max_memory_items", 10))
    logger.info(f"Loaded {len(agents)} agents")

    # Initialize database
    db_path = DATA_DIR / "simulation.db"
    repository = Repository(db_path)

    # Create simulation engine
    engine = SimulationEngine(
        agents=agents,
        repository=repository,
        topic=sim["topic"],
        model=sim.get("model", "llama3.1:8b"),
        temperature=sim.get("temperature", 0.8),
        iterations=sim.get("iterations", 50),
        seed_post=sim.get("seed_post"),
    )

    # Wire engine into the web app
    set_engine(engine)

    logger.info(f"Starting server on {server['host']}:{server['port']}")
    logger.info(f"Open http://localhost:{server['port']} in your browser")

    uvicorn.run(app, host=server["host"], port=server["port"], log_level="info")


if __name__ == "__main__":
    main()
