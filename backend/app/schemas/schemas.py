"""
app/schemas/schemas.py
───────────────────────
Pydantic v2 models for request validation and response serialisation.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, HttpUrl, field_validator


# ── Request ───────────────────────────────────────────────────────────────────

class GenerateQuizRequest(BaseModel):
    url: str
    num_questions: int = 7    # default 7; client can request 5–10

    @field_validator("num_questions")
    @classmethod
    def clamp_questions(cls, v: int) -> int:
        return max(5, min(10, v))

    @field_validator("url")
    @classmethod
    def must_be_wikipedia(cls, v: str) -> str:
        if "wikipedia.org/wiki/" not in v:
            raise ValueError(
                "URL must be a Wikipedia article URL "
                "(e.g. https://en.wikipedia.org/wiki/Alan_Turing)"
            )
        return v.strip()


# ── Question sub-schema ───────────────────────────────────────────────────────

class QuestionOut(BaseModel):
    question:    str
    options:     dict[str, str]   # {"A": ..., "B": ..., "C": ..., "D": ...}
    answer:      str
    difficulty:  str
    explanation: str


# ── Key entities sub-schema ───────────────────────────────────────────────────

class KeyEntitiesOut(BaseModel):
    people:        list[str] = []
    organizations: list[str] = []
    locations:     list[str] = []


# ── Full article + quiz response ──────────────────────────────────────────────

class ArticleQuizOut(BaseModel):
    id:             int
    url:            str
    title:          str
    summary:        str
    key_entities:   KeyEntitiesOut
    sections:       list[str]
    quiz:           list[QuestionOut]
    related_topics: list[str]
    created_at:     datetime

    model_config = {"from_attributes": True}


# ── History list item (Tab 2 table row) ──────────────────────────────────────

class ArticleListItem(BaseModel):
    id:         int
    url:        str
    title:      str
    created_at: datetime
    num_questions: int = 0

    model_config = {"from_attributes": True}


# ── Error response ────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str
