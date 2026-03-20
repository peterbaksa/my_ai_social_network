from enum import Enum

from pydantic import BaseModel


class ActionType(str, Enum):
    POST = "post"
    COMMENT = "comment"
    LIKE = "like"
    IGNORE = "ignore"


class AgentAction(BaseModel):
    action: ActionType
    content: str = ""
    target_agent: str = ""
    target_post_id: int | None = None
