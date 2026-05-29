CREATE TABLE IF NOT EXISTS articles (
    id          SERIAL PRIMARY KEY,
    url         TEXT        NOT NULL UNIQUE,
    title       TEXT        NOT NULL,
    summary     TEXT,
    sections    JSONB       DEFAULT '[]',          
    key_entities JSONB      DEFAULT '{}',          
    related_topics JSONB    DEFAULT '[]',          
    raw_text    TEXT,                              
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS quizzes (
    id          SERIAL PRIMARY KEY,
    article_id  INTEGER     NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    questions   JSONB       NOT NULL DEFAULT '[]', -- array of question objects
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_articles_url ON articles(url);
CREATE INDEX        IF NOT EXISTS idx_quizzes_article ON quizzes(article_id);
