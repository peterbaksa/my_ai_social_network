import json
from collections.abc import AsyncGenerator

import ollama

from src.agent.agent import Agent
from src.agent.actions import AgentAction, ActionType


SYSTEM_PROMPT_TEMPLATE = """You are {name}, a {age}-year-old person on a social network.

Your personality: {traits}
Your background: {background}

Current topic of discussion: {topic}
Your current focus: {current_focus}

Your opinion stance on the topic: {stance_description}
Your tone tends to be: {tone_description}

IMPORTANT RULES:
- Stay in character at all times. You ARE {name}, not an AI.
- Write naturally as a real person would on social media. Keep posts under 2-3 sentences.
- You can only do ONE action per turn.
- React to what others have said. Agree, disagree, ask questions, share your perspective.
- Never break character or mention that you are an AI.

Respond with ONLY a valid JSON object in this exact format:
{{"action": "post|comment|like|ignore", "content": "your message here", "target_agent": "name of person you're replying to or liking"}}

If you choose "post", leave "target_agent" empty.
If you choose "like" or "comment", set "target_agent" to the person's name.
If you choose "ignore", leave both "content" and "target_agent" empty."""


def _stance_description(stance: int) -> str:
    descriptions = {
        -2: "You strongly disagree with the mainstream optimism about this topic",
        -1: "You are skeptical and see more problems than solutions",
        0: "You see both sides and try to bring nuance and evidence",
        1: "You are cautiously optimistic but acknowledge challenges",
        2: "You strongly support the change and see it as progress",
    }
    return descriptions.get(stance, "You have a nuanced view")


def _tone_description(bias: float) -> str:
    if bias >= 0.5:
        return "positive, encouraging, enthusiastic"
    if bias >= 0.1:
        return "generally positive but measured"
    if bias >= -0.1:
        return "neutral and balanced"
    if bias >= -0.5:
        return "somewhat critical and cautious"
    return "negative, frustrated, confrontational"


def build_prompt(agent: Agent, topic: str, feed: str) -> list[dict]:
    system = SYSTEM_PROMPT_TEMPLATE.format(
        name=agent.persona.name,
        age=agent.persona.age,
        traits=agent.persona.traits,
        background=agent.persona.background,
        topic=topic,
        current_focus=agent.persona.current_focus,
        stance_description=_stance_description(agent.persona.opinion_stance),
        tone_description=_tone_description(agent.persona.sentiment_bias),
    )
    user_message = f"Here is what happened recently on the social network:\n{feed}\n\nWhat do you want to do?"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_message},
    ]


def parse_action(raw_text: str) -> AgentAction:
    text = raw_text.strip()
    # Try to extract JSON from the response
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        return AgentAction(action=ActionType.IGNORE)
    try:
        data = json.loads(text[start:end])
        return AgentAction(
            action=ActionType(data.get("action", "ignore")),
            content=data.get("content", ""),
            target_agent=data.get("target_agent", ""),
        )
    except (json.JSONDecodeError, ValueError):
        return AgentAction(action=ActionType.IGNORE)


async def generate_streaming(
    model: str,
    messages: list[dict],
    temperature: float = 0.8,
) -> AsyncGenerator[str, None]:
    client = ollama.AsyncClient()
    stream = await client.chat(
        model=model,
        messages=messages,
        stream=True,
        options={"temperature": temperature},
    )
    async for chunk in stream:
        token = chunk["message"]["content"]
        if token:
            yield token


async def generate(
    model: str,
    messages: list[dict],
    temperature: float = 0.8,
) -> str:
    client = ollama.AsyncClient()
    response = await client.chat(
        model=model,
        messages=messages,
        options={"temperature": temperature},
    )
    return response["message"]["content"]
