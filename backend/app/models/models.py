from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
class Article(Base):
    __tablename__ = "articles"

    id              = Column(Integer, primary_key=True, index=True)
    url             = Column(Text, unique=True, nullable=False, index=True)
    title           = Column(Text, nullable=False)
    summary         = Column(Text)
    sections        = Column(JSONB, default=list)   
    key_entities    = Column(JSONB, default=dict)   
    related_topics  = Column(JSONB, default=list)   
    raw_text        = Column(Text)                  
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    quiz            = relationship("Quiz", back_populates="article", uselist=False,
                                   cascade="all, delete-orphan")
class Quiz(Base):
    __tablename__ = "quizzes"

    id          = Column(Integer, primary_key=True, index=True)
    article_id  = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    questions   = Column(JSONB, nullable=False, default=list)
    # Each element in questions:
    # {
    #   "question": str,
    #   "options": {"A": str, "B": str, "C": str, "D": str},
    #   "answer": str,          # "A" | "B" | "C" | "D"
    #   "difficulty": str,      # "easy" | "medium" | "hard"
    #   "explanation": str
    # }
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    article     = relationship("Article", back_populates="quiz")
