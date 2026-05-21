import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import crud
from app.schemas.schemas import GenerateQuizRequest, ArticleQuizOut, ArticleListItem, QuestionOut, KeyEntitiesOut
from app.services.scraper import scrape_wikipedia
from app.services.llm import generate_quiz, generate_related_topics

logger = logging.getLogger(__name__)
router = APIRouter()

def _build_response(article, quiz):
    ke = article.key_entities or {}
    return ArticleQuizOut(
        id=article.id,
        url=article.url,
        title=article.title,
        summary=article.summary or "",
        key_entities=KeyEntitiesOut(
            people=ke.get("people", []),
            organizations=ke.get("organizations", []),
            locations=ke.get("locations", []),
        ),
        sections=article.sections or [],
        quiz=[QuestionOut(**q) for q in (quiz.questions or [])],
        related_topics=article.related_topics or [],
        created_at=article.created_at,
    )

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/generate", response_model=ArticleQuizOut)
def generate_quiz_endpoint(payload: GenerateQuizRequest, db: Session = Depends(get_db)):
    url = payload.url
    existing = crud.get_article_by_url(db, url)

    if existing:
        scraped = {
            "title": existing.title,
            "summary": existing.summary,
            "sections": existing.sections or [],
            "key_entities": existing.key_entities or {},
            "related_topics": existing.related_topics or [],
            "raw_text": existing.raw_text or "",
        }
        article = existing
    else:
        try:
            scraped = scrape_wikipedia(url)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Scraping failed: {e}")
        article = None

    try:
        questions = generate_quiz(
            scraped["title"],
            scraped["raw_text"],
            scraped["sections"],
            payload.num_questions,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {e}")

    try:
        related = generate_related_topics(scraped["title"], scraped["summary"], scraped["related_topics"])
    except Exception:
        related = scraped["related_topics"]

    try:
        if article is None:
            article = crud.create_article(
                db=db,
                url=url,
                title=scraped["title"],
                summary=scraped["summary"],
                sections=scraped["sections"],
                key_entities=scraped["key_entities"],
                related_topics=related,
                raw_text=scraped["raw_text"],
            )
        else:
            crud.update_article(db, article, related_topics=related)

        if article.quiz:
            quiz = crud.update_quiz(db, article.quiz, questions)
        else:
            quiz = crud.create_quiz(db, article.id, questions)

        db.commit()
        db.refresh(article)
        db.refresh(quiz)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    return _build_response(article, quiz)

@router.get("/quizzes", response_model=list[ArticleListItem])
def list_quizzes(db: Session = Depends(get_db)):
    articles = crud.get_all_articles(db)
    return [
        ArticleListItem(
            id=a.id, url=a.url, title=a.title,
            created_at=a.created_at,
            num_questions=len(a.quiz.questions) if a.quiz else 0,
        ) for a in articles
    ]

@router.get("/quizzes/{quiz_id}", response_model=ArticleQuizOut)
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    article = crud.get_article_by_id(db, quiz_id)
    if not article or not article.quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return _build_response(article, article.quiz)