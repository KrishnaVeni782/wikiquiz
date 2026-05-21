# WikiQuiz — AI-Powered Quiz Generator

Generate multiple-choice quizzes from any Wikipedia article using Gemini AI.

![Tab 1: Generate Quiz](screenshots/tab1_generate.png)
![Tab 2: Past Quizzes](screenshots/tab2_history.png)

---

## Features

- **Scrape** any Wikipedia article with BeautifulSoup
- **Extract** title, summary, sections, key entities (people/orgs/locations), and related topics
- **Generate** 5–10 MCQ questions with difficulty levels and explanations via Gemini 1.5 Flash
- **Store** all data in PostgreSQL (with caching — same URL reuses scraped data)
- **Take-Quiz mode** — answers hidden until submitted, with scoring
- **History tab** — browse all past quizzes with full detail modal

---

## Project Structure

```
wikiquiz/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py          # FastAPI endpoints
│   │   ├── core/
│   │   │   └── config.py          # Pydantic settings (.env)
│   │   ├── db/
│   │   │   ├── database.py        # SQLAlchemy engine + session
│   │   │   └── crud.py            # DB read/write helpers
│   │   ├── models/
│   │   │   └── models.py          # ORM table definitions
│   │   ├── schemas/
│   │   │   └── schemas.py         # Pydantic request/response models
│   │   ├── services/
│   │   │   ├── scraper.py         # BeautifulSoup Wikipedia scraper
│   │   │   └── llm.py             # LangChain + Gemini integration
│   │   └── main.py                # FastAPI app factory
│   ├── schema.sql                 # Raw SQL schema (reference)
│   ├── requirements.txt
│   └── .env.example               # Copy to .env and fill in values
│
├── frontend/
│   └── index.html                 # Single-file React-free frontend
│
└── sample_data/
    ├── test_urls.txt              # 3 test Wikipedia URLs
    ├── output_alan_turing.json    # Sample API output
    ├── output_black_hole.json
    ├── output_gandhi.json
    └── prompt_templates.txt       # LangChain prompts used
```

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.11+ |
| PostgreSQL | 14+ |
| pip | latest |

---

## Setup

### 1 — Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/wikiquiz.git
cd wikiquiz
```

### 2 — Get a free Gemini API key

1. Go to https://aistudio.google.com/app/apikey
2. Click **Create API key**
3. Copy the key (looks like `AIzaSy...`)

### 3 — Create the PostgreSQL database

```bash
# macOS (Homebrew)
brew services start postgresql@16
createdb wikiquiz

# Ubuntu / Debian
sudo service postgresql start
sudo -u postgres createdb wikiquiz

# Windows (PowerShell as Admin)
# Make sure PostgreSQL is running, then:
& "C:\Program Files\PostgreSQL\16\bin\createdb.exe" -U postgres wikiquiz
```

### 4 — Configure environment variables

```bash
cd backend
cp .env.example .env
```

Edit `.env`:

```dotenv
GEMINI_API_KEY=AIzaSy...your_key_here...
DATABASE_URL=postgresql://postgres:your_pg_password@localhost:5432/wikiquiz
ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500,http://localhost:3000
```

### 5 — Install Python dependencies

```bash
cd backend
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

### 6 — Run the backend

```bash
# From inside backend/ with venv active
uvicorn app.main:app --reload --port 8000
```

Visit http://localhost:8000/docs for the interactive Swagger UI.

Tables are created automatically on first startup.

### 7 — Open the frontend

No build step needed. Just open the file in a browser:

```bash
# macOS
open frontend/index.html

# Linux
xdg-open frontend/index.html

# Windows
start frontend/index.html
```

Or serve it (recommended, to avoid CORS issues with some browsers):

```bash
# Python one-liner from the frontend/ directory
cd frontend
python -m http.server 5500
# Then visit http://localhost:5500
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/generate` | Scrape URL + generate quiz |
| GET | `/api/quizzes` | List all past quizzes |
| GET | `/api/quizzes/{id}` | Get quiz by article ID |
| GET | `/api/health` | Liveness probe |

### POST /api/generate — Request body

```json
{
  "url": "https://en.wikipedia.org/wiki/Alan_Turing",
  "num_questions": 7
}
```

- `num_questions`: integer 5–10 (default 7)

### Sample cURL

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://en.wikipedia.org/wiki/Alan_Turing", "num_questions": 7}'
```

---

## Environment Variables Reference

| Variable | Required | Description | Where to get |
|----------|----------|-------------|--------------|
| `GEMINI_API_KEY` | ✅ | Gemini LLM API key | https://aistudio.google.com/app/apikey |
| `DATABASE_URL` | ✅ | PostgreSQL connection string | Your DB host |
| `ALLOWED_ORIGINS` | ✅ | Comma-separated CORS origins | Your frontend URL(s) |

---

## Running Tests (Manual)

```bash
# Health check
curl http://localhost:8000/api/health

# Generate quiz
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"url":"https://en.wikipedia.org/wiki/Black_hole","num_questions":5}'

# List quizzes
curl http://localhost:8000/api/quizzes

# Get quiz #1
curl http://localhost:8000/api/quizzes/1
```

---

## Deployment

See Step 9 in the walkthrough for full deployment instructions.

**Quick reference:**

| Component | Platform | Notes |
|-----------|----------|-------|
| Backend | Render / Railway | Set env vars in dashboard |
| Database | Render Postgres / Supabase | Copy connection string |
| Frontend | Netlify / Vercel | Set `API_BASE` in `index.html` |

---

## LangChain Prompt Templates

See `sample_data/prompt_templates.txt` for the full quiz generation and
related-topics prompts, plus design rationale.

Model: **gemini-1.5-flash** (free tier, generous quota)
Temperature: **0.4** (factual grounding with varied distractors)

---

## Bonus Features Implemented

- ✅ **Take Quiz mode** — answers hidden until submitted with score
- ✅ **URL caching** — same URL reuses scraped data, only regenerates quiz
- ✅ **Raw HTML stored** — `raw_text` column in `articles` table
- ✅ **Section-wise display** — sections shown as tags in UI
- ✅ **Related topics augmented by LLM** — adds to scraped See-also links
