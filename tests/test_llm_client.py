from src.llm.client import parse_action, build_prompt
from src.agent.agent import Agent
from src.agent.actions import ActionType


def test_parse_action_valid_post():
    raw = '{"action": "post", "content": "Hello world!", "target_agent": ""}'
    action = parse_action(raw)
    assert action.action == ActionType.POST
    assert action.content == "Hello world!"


def test_parse_action_valid_comment():
    raw = '{"action": "comment", "content": "I agree!", "target_agent": "Alice"}'
    action = parse_action(raw)
    assert action.action == ActionType.COMMENT
    assert action.target_agent == "Alice"


def test_parse_action_with_surrounding_text():
    raw = 'Here is my response:\n{"action": "like", "content": "", "target_agent": "Bob"}\nDone.'
    action = parse_action(raw)
    assert action.action == ActionType.LIKE
    assert action.target_agent == "Bob"


def test_parse_action_invalid_json():
    raw = "I want to post something but I forgot the format"
    action = parse_action(raw)
    assert action.action == ActionType.IGNORE


def test_parse_action_empty():
    action = parse_action("")
    assert action.action == ActionType.IGNORE


def test_build_prompt_structure():
    config = {
        "name": "Test Agent",
        "age": 30,
        "traits": "friendly",
        "background": "A test agent.",
        "current_focus": "Testing.",
        "opinion_stance": 0,
        "sentiment_bias": 0.0,
    }
    agent = Agent.from_config(config, file_key="test")
    messages = build_prompt(agent, "Test topic", "No activity yet.")
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "Test Agent" in messages[0]["content"]
    assert "Test topic" in messages[0]["content"]
