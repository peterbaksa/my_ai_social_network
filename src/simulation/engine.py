import asyncio
import logging
import uuid
from collections.abc import Callable, Awaitable

from src.agent.agent import Agent
from src.agent.actions import AgentAction, ActionType
from src.agent.memory import MemoryItem
from src.database.repository import Repository
from src.llm.client import build_prompt, generate, parse_action
from src.simulation.feed import FeedManager

logger = logging.getLogger(__name__)

# Type for the callback that sends events to WebSocket clients
EventCallback = Callable[[dict], Awaitable[None]]


class SimulationEngine:
    def __init__(
        self,
        agents: list[Agent],
        repository: Repository,
        topic: str,
        model: str = "llama3.1:8b",
        temperature: float = 0.8,
        iterations: int = 50,
        seed_post: dict | None = None,
    ):
        self.agents = {a.file_key: a for a in agents}
        self.agents_ordered = agents
        self.repository = repository
        self.topic = topic
        self.model = model
        self.temperature = temperature
        self.iterations = iterations
        self.seed_post = seed_post
        self.feed = FeedManager()
        self._event_callback: EventCallback | None = None
        self._running = False
        self._session_id: str = ""

    def set_event_callback(self, callback: EventCallback) -> None:
        self._event_callback = callback

    async def _emit(self, event: dict) -> None:
        if self._event_callback:
            await self._event_callback(event)

    def _restore_session(self, session_id: str) -> int:
        """Restore feed and agent memories from an existing session. Returns last iteration."""
        posts = self.repository.get_session_posts(session_id)
        for post in posts:
            item = MemoryItem(
                iteration=post.iteration,
                agent_name=post.agent_name,
                action=post.action,
                content=post.content,
                target=post.target_agent,
            )
            self.feed.add_item(item)
            # Restore personal memory for the agent who made this action
            for agent in self.agents_ordered:
                if agent.name == post.agent_name:
                    agent.memory.add(item)
                    break

        last_iteration = self.repository.get_last_iteration(session_id)
        logger.info(f"Restored session {session_id}: {len(posts)} actions, last iteration {last_iteration}")
        return last_iteration

    async def _run_agent_turn(self, agent: Agent, iteration: int) -> AgentAction:
        feed_text = self.feed.get_feed_for_agent(agent.name)
        messages = build_prompt(agent, self.topic, feed_text)

        await self._emit({
            "type": "agent_thinking",
            "agent": agent.name,
            "iteration": iteration,
        })

        # Collect full response from LLM (no raw streaming to UI)
        full_response = await generate(self.model, messages, self.temperature)
        action = parse_action(full_response)

        # Stream only the clean content to UI word by word
        if action.content:
            words = action.content.split(" ")
            for i, word in enumerate(words):
                chunk = word if i == 0 else " " + word
                await self._emit({
                    "type": "stream_chunk",
                    "agent": agent.name,
                    "chunk": chunk,
                    "iteration": iteration,
                })
                await asyncio.sleep(0.03)

        await self._emit({
            "type": "agent_action",
            "agent": agent.name,
            "action": action.action.value,
            "content": action.content,
            "target_agent": action.target_agent,
            "iteration": iteration,
        })

        return action

    def _record_action(self, agent: Agent, action: AgentAction, iteration: int) -> None:
        # Save to database
        self.repository.save_action(
            session_id=self._session_id,
            iteration=iteration,
            agent_name=agent.name,
            action=action.action.value,
            content=action.content,
            target_agent=action.target_agent,
            opinion_stance=agent.persona.opinion_stance,
            sentiment_bias=agent.persona.sentiment_bias,
        )

        # Add to global feed
        memory_item = MemoryItem(
            iteration=iteration,
            agent_name=agent.name,
            action=action.action.value,
            content=action.content,
            target=action.target_agent,
        )
        self.feed.add_item(memory_item)

        # Add to agent's personal memory
        agent.memory.add(memory_item)

    async def _inject_seed_post(self) -> None:
        if not self.seed_post:
            return

        agent_key = self.seed_post["agent"]
        content = self.seed_post["content"]

        if agent_key not in self.agents:
            logger.warning(f"Seed post agent '{agent_key}' not found, skipping.")
            return

        agent = self.agents[agent_key]
        seed_action = AgentAction(
            action=ActionType.POST,
            content=content,
        )

        self._record_action(agent, seed_action, iteration=0)

        await self._emit({
            "type": "agent_action",
            "agent": agent.name,
            "action": "post",
            "content": content,
            "target_agent": "",
            "iteration": 0,
        })

        logger.info(f"Seed post by {agent.name}: {content}")

    async def run(self, resume: bool = False) -> None:
        self._running = True
        start_iteration = 1

        if resume:
            last_session = self.repository.get_last_session_id()
            if last_session:
                self._session_id = last_session
                last_iter = self._restore_session(last_session)
                start_iteration = last_iter + 1
                if start_iteration > self.iterations:
                    logger.info(f"Session {last_session} already completed ({last_iter}/{self.iterations}).")
                    await self._emit({"type": "simulation_end"})
                    self._running = False
                    return
                logger.info(f"Resuming session {self._session_id} from iteration {start_iteration}")
                # Replay previous actions to UI
                posts = self.repository.get_session_posts(self._session_id)
                for post in posts:
                    await self._emit({
                        "type": "agent_action",
                        "agent": post.agent_name,
                        "action": post.action,
                        "content": post.content,
                        "target_agent": post.target_agent,
                        "iteration": post.iteration,
                    })
            else:
                resume = False

        if not resume:
            self._session_id = str(uuid.uuid4())[:8]
            logger.info(f"New session: {self._session_id}")

        await self._emit({
            "type": "simulation_start",
            "iterations": self.iterations,
            "session_id": self._session_id,
            "resume": resume,
        })

        # Inject seed post only for new sessions
        if not resume:
            await self._inject_seed_post()

        for iteration in range(start_iteration, self.iterations + 1):
            if not self._running:
                break

            await self._emit({
                "type": "iteration_start",
                "iteration": iteration,
                "total": self.iterations,
            })

            logger.info(f"--- Iteration {iteration}/{self.iterations} (session {self._session_id}) ---")

            for agent in self.agents_ordered:
                if not self._running:
                    break

                try:
                    action = await self._run_agent_turn(agent, iteration)
                    self._record_action(agent, action, iteration)
                except Exception as e:
                    logger.error(f"Agent {agent.name} failed: {e}")
                    await self._emit({
                        "type": "agent_error",
                        "agent": agent.name,
                        "error": str(e),
                        "iteration": iteration,
                    })

            await self._emit({
                "type": "iteration_end",
                "iteration": iteration,
                "total": self.iterations,
            })

        self._running = False
        await self._emit({"type": "simulation_end"})
        logger.info("Simulation complete.")

    def stop(self) -> None:
        self._running = False
