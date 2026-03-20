from src.agent.agent import Agent, AgentPersona
from src.agent.memory import AgentMemory, MemoryItem
from src.agent.actions import ActionType, AgentAction


def test_agent_from_config():
    config = {
        "name": "Test Agent",
        "age": 30,
        "traits": "friendly, curious",
        "background": "A test agent for unit testing.",
        "current_focus": "Testing the system.",
        "opinion_stance": 1,
        "sentiment_bias": 0.5,
    }
    agent = Agent.from_config(config, file_key="test_agent")
    assert agent.name == "Test Agent"
    assert agent.persona.age == 30
    assert agent.file_key == "test_agent"


def test_memory_rolling_window():
    memory = AgentMemory(max_items=3)
    for i in range(5):
        memory.add(MemoryItem(
            iteration=i,
            agent_name="Test",
            action="post",
            content=f"Post {i}",
        ))
    assert len(memory) == 3
    items = memory.get_recent()
    assert items[0].content == "Post 2"
    assert items[2].content == "Post 4"


def test_memory_format_for_prompt():
    memory = AgentMemory(max_items=10)
    memory.add(MemoryItem(iteration=1, agent_name="Alice", action="post", content="Hello world"))
    memory.add(MemoryItem(iteration=1, agent_name="Bob", action="comment", content="Nice!", target="Alice"))
    memory.add(MemoryItem(iteration=1, agent_name="Charlie", action="like", content="", target="Alice"))

    formatted = memory.format_for_prompt()
    assert 'Alice posted: "Hello world"' in formatted
    assert 'Bob replied to Alice: "Nice!"' in formatted
    assert "Charlie liked Alice's post" in formatted


def test_action_types():
    action = AgentAction(action=ActionType.POST, content="Test post")
    assert action.action == ActionType.POST
    assert action.content == "Test post"
    assert action.target_agent == ""
