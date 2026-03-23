import logging
from pathlib import Path

import uvicorn
import yaml

from src.agent.agent import Agent
from src.web.app import app, sim_state

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

    # Populate shared simulation state
    sim_state.topic = sim["topic"]
    sim_state.model = sim.get("model", "llama3.1:8b")
    sim_state.temperature = sim.get("temperature", 0.8)
    sim_state.iterations = sim.get("iterations", 50)
    sim_state.max_memory_items = sim.get("max_memory_items", 10)
    sim_state.agents = agents
    sim_state.db_path = DATA_DIR / "simulation.db"

    seed = sim.get("seed_post")
    if seed:
        sim_state.seed_post_agent = seed.get("agent", "")
        sim_state.seed_post_content = seed.get("content", "")

    logger.info(f"Starting server on {server['host']}:{server['port']}")
    logger.info(f"Open http://localhost:{server['port']} in your browser")

    uvicorn.run(app, host=server["host"], port=server["port"], log_level="info")


if __name__ == "__main__":
    main()