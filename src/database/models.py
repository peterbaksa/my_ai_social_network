from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), nullable=False, index=True)
    iteration = Column(Integer, nullable=False)
    agent_name = Column(String(100), nullable=False)
    action = Column(String(20), nullable=False)
    content = Column(Text, default="")
    target_agent = Column(String(100), default="")
    opinion_stance = Column(Integer, default=0)
    sentiment_bias = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
