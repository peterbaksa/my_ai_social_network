from src.agent.memory import MemoryItem


class FeedManager:
    def __init__(self):
        self._global_feed: list[MemoryItem] = []

    def add_item(self, item: MemoryItem) -> None:
        self._global_feed.append(item)

    def get_feed_for_agent(self, agent_name: str, max_items: int = 15) -> str:
        recent = self._global_feed[-max_items:]
        if not recent:
            return "The social network is empty. Be the first to post!"

        lines = []
        for item in recent:
            if item.action == "post":
                lines.append(f"- {item.agent_name} posted: \"{item.content}\"")
            elif item.action == "comment":
                lines.append(f"- {item.agent_name} replied to {item.target}: \"{item.content}\"")
            elif item.action == "like":
                lines.append(f"- {item.agent_name} liked {item.target}'s post")
        return "\n".join(lines) if lines else "No notable activity yet."

    def get_all(self) -> list[MemoryItem]:
        return list(self._global_feed)

    def clear(self) -> None:
        self._global_feed.clear()
