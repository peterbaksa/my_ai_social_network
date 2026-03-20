from pathlib import Path

from sqlalchemy import create_engine, desc, func, select
from sqlalchemy.orm import Session

from src.database.models import Base, Post


class Repository:
    def __init__(self, db_path: str | Path):
        self._engine = create_engine(f"sqlite:///{db_path}", echo=False)
        Base.metadata.create_all(self._engine)

    def save_action(
        self,
        session_id: str,
        iteration: int,
        agent_name: str,
        action: str,
        content: str = "",
        target_agent: str = "",
        opinion_stance: int = 0,
        sentiment_bias: float = 0.0,
    ) -> Post:
        with Session(self._engine) as session:
            post = Post(
                session_id=session_id,
                iteration=iteration,
                agent_name=agent_name,
                action=action,
                content=content,
                target_agent=target_agent,
                opinion_stance=opinion_stance,
                sentiment_bias=sentiment_bias,
            )
            session.add(post)
            session.commit()
            session.refresh(post)
            return post

    def get_last_session_id(self) -> str | None:
        with Session(self._engine) as session:
            stmt = select(Post.session_id).order_by(desc(Post.id)).limit(1)
            return session.scalar(stmt)

    def get_last_iteration(self, session_id: str) -> int:
        with Session(self._engine) as session:
            stmt = select(func.max(Post.iteration)).where(Post.session_id == session_id)
            result = session.scalar(stmt)
            return result if result is not None else 0

    def get_session_posts(self, session_id: str) -> list[Post]:
        with Session(self._engine) as session:
            stmt = select(Post).where(Post.session_id == session_id).order_by(Post.id)
            return list(session.scalars(stmt).all())

    def get_all_posts(self) -> list[Post]:
        with Session(self._engine) as session:
            stmt = select(Post).order_by(Post.id)
            return list(session.scalars(stmt).all())
