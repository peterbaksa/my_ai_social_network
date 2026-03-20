from src.simulation.feed import FeedManager
from src.agent.memory import MemoryItem


def test_feed_manager_add_and_retrieve():
    feed = FeedManager()
    feed.add_item(MemoryItem(iteration=1, agent_name="Alice", action="post", content="Hello"))
    feed.add_item(MemoryItem(iteration=1, agent_name="Bob", action="comment", content="Hi!", target="Alice"))

    result = feed.get_feed_for_agent("Charlie")
    assert "Alice" in result
    assert "Hello" in result
    assert "Bob" in result


def test_feed_manager_empty():
    feed = FeedManager()
    result = feed.get_feed_for_agent("Alice")
    assert "empty" in result.lower() or "first" in result.lower()


def test_feed_manager_max_items():
    feed = FeedManager()
    for i in range(30):
        feed.add_item(MemoryItem(iteration=i, agent_name=f"Agent{i}", action="post", content=f"Post {i}"))

    result = feed.get_feed_for_agent("Observer", max_items=5)
    # Should only show last 5 posts
    assert "Agent25" in result
    assert "Agent29" in result
