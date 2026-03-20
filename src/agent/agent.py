from dataclasses import dataclass, field

from src.agent.memory import AgentMemory


@dataclass
class AgentPersona:
    name: str
    age: int
    traits: str
    background: str
    current_focus: str
    opinion_stance: int
    sentiment_bias: float


@dataclass
class Agent:
    persona: AgentPersona
    memory: AgentMemory = field(default_factory=AgentMemory)
    file_key: str = ""

    @classmethod
    def from_config(cls, config: dict, file_key: str, max_memory: int = 10) -> "Agent":
        persona = AgentPersona(
            name=config["name"],
            age=config["age"],
            traits=config["traits"],
            background=config["background"].strip(),
            current_focus=config["current_focus"].strip(),
            opinion_stance=config["opinion_stance"],
            sentiment_bias=config["sentiment_bias"],
        )
        return cls(persona=persona, memory=AgentMemory(max_items=max_memory), file_key=file_key)

    @property
    def name(self) -> str:
        return self.persona.name
