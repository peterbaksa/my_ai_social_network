from pydantic import BaseModel, Field


class AgentSchema(BaseModel):
    file_key: str = ""
    name: str
    age: int = 30
    traits: str = ""
    background: str = ""
    current_focus: str = ""
    opinion_stance: int = Field(0, ge=-2, le=2)
    sentiment_bias: float = Field(0.0, ge=-1.0, le=1.0)


class SimulationConfigSchema(BaseModel):
    topic: str = ""
    iterations: int = Field(50, ge=1, le=500)
    model: str = "llama3.1:8b"
    temperature: float = Field(0.8, ge=0.0, le=2.0)
    max_memory_items: int = Field(10, ge=1, le=100)
    seed_post_agent: str = ""
    seed_post_content: str = ""


class ConfigResponse(BaseModel):
    simulation: SimulationConfigSchema
    agents: list[AgentSchema]
