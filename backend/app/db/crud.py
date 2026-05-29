from __future__ import annotations
import logging
from typing import Any
from sqlalchemy.orm import Session
from app.models.models import Article, Quiz
logger = logging.getLogger(__name__)

def get_article_by_url(db: Session, url: str) -> Article | None:
    return db.query(Article).filter(Article.url == url).first()
def get_article_by_id(db: Session, article_id: int) -> Article | None:
    return db.query(Article).filter(Article.id == article_id).first()
def get_all_articles(db: Session, skip: int = 0, limit: int = 100) -> list[Article]:
    return (
        db.query(Article)
        .order_by(Article.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
def create_article(
    db: Session,
    url: str,
    title: str,
    summary: str,
    sections: list[str],
    key_entities: dict[str, list[str]],
    related_topics: list[str],
    raw_text: str,
) -> Article:
    article = Article(
        url=url,
        title=title,
        summary=summary,
        sections=sections,
        key_entities=key_entities,
        related_topics=related_topics,
        raw_text=raw_text,
    )
    db.add(article)
    db.flush()   # get id without committing
    return article
def update_article(db: Session, article: Article, **kwargs: Any) -> Article:
    """Patch any subset of article fields."""
    for field, value in kwargs.items():
        setattr(article, field, value)
    db.flush()
    return article
def create_quiz(
    db: Session,
    article_id: int,
    questions: list[dict],
) -> Quiz:
    quiz = Quiz(article_id=article_id, questions=questions)
    db.add(quiz)
    db.flush()
    return quiz
def update_quiz(db: Session, quiz: Quiz, questions: list[dict]) -> Quiz:
    quiz.questions = questions
    db.flush()
    return quiz
