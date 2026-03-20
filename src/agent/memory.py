from collections import deque

from pydantic import BaseModel


class MemoryItem(BaseModel):
    iteration: int
    agent_name: str
    action: str
    content: str
    target: str = ""


class AgentMemory:
    def __init__(self, max_items: int = 10):
        self._items: deque[MemoryItem] = deque(maxlen=max_items)

    def add(self, item: MemoryItem) -> None:
        self._items.append(item)

    def get_recent(self, count: int | None = None) -> list[MemoryItem]:
        items = list(self._items)
        if count is not None:
            return items[-count:]
        return items

    def format_for_prompt(self) -> str:
        if not self._items:
            return "No activity yet."
        lines = []
        for item in self._items:
            if item.action == "post":
                lines.append(f"- {item.agent_name} posted: \"{item.content}\"")
            elif item.action == "comment":
                lines.append(f"- {item.agent_name} replied to {item.target}: \"{item.content}\"")
            elif item.action == "like":
                lines.append(f"- {item.agent_name} liked {item.target}'s post")
            elif item.action == "ignore":
                pass
        return "\n".join(lines) if lines else "No notable activity yet."

    def clear(self) -> None:
        self._items.clear()

    def __len__(self) -> int:
        return len(self._items)
