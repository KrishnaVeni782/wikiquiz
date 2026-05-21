# Submission Checklist — WikiQuiz
# ═══════════════════════════════════════════════════════════════════════════

## Screenshots to take (save as screenshots/ in repo root)

□ tab1_generate.png
  - URL field filled with a Wikipedia URL
  - Quiz generation result visible with article hero, entity tags,
    question cards showing difficulty badges

□ tab1_take_quiz.png
  - Switch to "Take Quiz" mode
  - Some answers selected
  - Score banner showing after Submit

□ tab2_history.png
  - At least 3 rows in the history table
  - Shows article titles, URLs, question counts, dates

□ tab2_modal.png
  - "Details →" clicked on a row
  - Full quiz modal open over the history table

□ swagger_ui.png
  - http://localhost:8000/docs showing all endpoints

## How to take screenshots

  macOS:     Cmd+Shift+4  (drag to select area)
  Windows:   Win+Shift+S  (Snipping Tool)
  Linux:     Flameshot / Scrot

  Save them in wikiquiz/screenshots/ and commit.

## Final GitHub repo structure

wikiquiz/
├── .gitignore
├── README.md
├── DEPLOYMENT.md
├── render.yaml
├── netlify.toml
├── backend/
│   ├── app/ ...
│   ├── requirements.txt
│   ├── schema.sql
│   └── .env.example        ← NOT .env (never commit secrets!)
├── frontend/
│   └── index.html
├── sample_data/
│   ├── test_urls.txt
│   ├── output_alan_turing.json
│   ├── output_black_hole.json
│   ├── output_gandhi.json
│   └── prompt_templates.txt
└── screenshots/
    ├── tab1_generate.png
    ├── tab1_take_quiz.png
    ├── tab2_history.png
    ├── tab2_modal.png
    └── swagger_ui.png

## Commit and push

git add .
git commit -m "complete submission: backend, frontend, sample data, screenshots"
git push origin main

## Google Form submission

Fill in:
  - GitHub repo URL: https://github.com/YOUR_USERNAME/wikiquiz
  - Live backend URL: https://wikiquiz-backend.onrender.com
  - Live frontend URL: https://wikiquiz.netlify.app
  - Notes: mention bonus features (Take Quiz mode, caching, raw text storage)

## Evaluation criteria mapping

Criterion             → Where to find it
─────────────────────────────────────────────────────────────
Prompt Design         → sample_data/prompt_templates.txt + app/services/llm.py
Quiz Quality          → output_*.json + live generation
Extraction Quality    → app/services/scraper.py
Functionality         → README.md step 6 + swagger screenshot
Code Quality          → All files; docstrings throughout
Error Handling        → routes.py (try/catch + HTTP status codes)
UI Design             → frontend/index.html + screenshots
Database Accuracy     → tab2_history.png + tab2_modal.png screenshots
Testing Evidence      → sample_data/ folder + screenshots

## Bonus features checklist

☑ Take Quiz mode with scoring
☑ URL caching (re-scrapes only on new URLs)
☑ Raw HTML stored (raw_text column)
☑ Section-wise display in UI
☑ LLM-augmented related topics
