-- ============================================================
-- WikiQuiz PostgreSQL Schema
-- Run this once against your database, or let SQLAlchemy
-- create tables automatically via Base.metadata.create_all()
-- ============================================================

CREATE TABLE IF NOT EXISTS articles (
    id          SERIAL PRIMARY KEY,
    url         TEXT        NOT NULL UNIQUE,
    title       TEXT        NOT NULL,
    summary     TEXT,
    sections    JSONB       DEFAULT '[]',          -- list of section headings
    key_entities JSONB      DEFAULT '{}',          -- {people, organizations, locations}
    related_topics JSONB    DEFAULT '[]',          -- list of related topic strings
    raw_text    TEXT,                              -- full scraped text (bonus)
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS quizzes (
    id          SERIAL PRIMARY KEY,
    article_id  INTEGER     NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    questions   JSONB       NOT NULL DEFAULT '[]', -- array of question objects
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for fast URL lookup (cache check)
CREATE UNIQUE INDEX IF NOT EXISTS idx_articles_url ON articles(url);
CREATE INDEX        IF NOT EXISTS idx_quizzes_article ON quizzes(article_id);
