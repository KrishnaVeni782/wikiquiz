# Deployment Guide — WikiQuiz
# ═══════════════════════════════════════════════════════════════════════════

## Option A — Render (backend + DB) + Netlify (frontend)   ← RECOMMENDED FREE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP A1: Push to GitHub
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

git init
git add .
git commit -m "initial commit"
gh repo create wikiquiz --public --push
# or: git remote add origin https://github.com/YOU/wikiquiz.git && git push -u origin main

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP A2: Deploy PostgreSQL on Render
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Go to https://dashboard.render.com
2. New → PostgreSQL
3. Name: wikiquiz-db   Plan: Free
4. Click Create Database
5. Copy "External Database URL" (starts with postgresql://)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP A3: Deploy Backend on Render
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. New → Web Service
2. Connect your GitHub repo
3. Settings:
   - Root Directory:  backend
   - Runtime:         Python 3
   - Build Command:   pip install -r requirements.txt
   - Start Command:   uvicorn app.main:app --host 0.0.0.0 --port $PORT
4. Environment Variables (click "Add Environment Variable" for each):
   - GEMINI_API_KEY   = AIzaSy... (your key)         [mark as Secret ✓]
   - DATABASE_URL     = postgresql://... (from step A2)
   - ALLOWED_ORIGINS  = https://your-app.netlify.app  (fill in after step A4)
5. Health Check Path: /api/health
6. Click Create Web Service
7. Wait ~3 min for build. Note your backend URL:
   https://wikiquiz-backend.onrender.com

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP A4: Update frontend API_BASE and deploy to Netlify
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Open frontend/index.html
2. Find this line near the top of the <script>:
      const API_BASE = 'http://localhost:8000/api';
3. Replace with your Render backend URL:
      const API_BASE = 'https://wikiquiz-backend.onrender.com/api';
4. Save and commit:
   git add frontend/index.html && git commit -m "update API_BASE for production" && git push

5. Go to https://app.netlify.com
6. New site → Import from Git → pick your repo
7. Build settings are auto-read from netlify.toml:
   - Publish directory: frontend
8. Click Deploy site
9. Copy your Netlify URL (e.g. https://wikiquiz.netlify.app)

10. Back in Render → wikiquiz-backend → Environment:
    Update ALLOWED_ORIGINS to your actual Netlify URL, then click Save.
    The service will redeploy automatically.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP A5: Verify deployment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

curl https://wikiquiz-backend.onrender.com/api/health
# Should return: {"status":"ok"}

curl -X POST https://wikiquiz-backend.onrender.com/api/generate \
  -H "Content-Type: application/json" \
  -d '{"url":"https://en.wikipedia.org/wiki/Alan_Turing","num_questions":5}'

Then open your Netlify URL in a browser and test the UI.

Note: Render free tier spins down after 15 min of inactivity.
First request after spin-down takes ~30s. This is normal on the free plan.

═══════════════════════════════════════════════════════════════════════════
## Option B — Railway (backend + DB) + Vercel (frontend)
═══════════════════════════════════════════════════════════════════════════

STEP B1: Deploy to Railway
  1. Go to https://railway.app → New Project → Deploy from GitHub
  2. Select your repo
  3. Railway auto-detects Python. Add these env vars:
     GEMINI_API_KEY, DATABASE_URL (from Railway Postgres plugin), ALLOWED_ORIGINS
  4. Add a Postgres plugin: New → Database → Add PostgreSQL
  5. Copy DATABASE_URL from the plugin's Connect tab
  6. Your backend URL will be: https://wikiquiz-production.up.railway.app

STEP B2: Deploy frontend to Vercel
  1. Go to https://vercel.com → New Project → import your repo
  2. Root Directory: frontend   Framework Preset: Other
  3. Add env var in Vercel dashboard:
     (not needed — API_BASE is hardcoded in index.html; update it first)
  4. Deploy

═══════════════════════════════════════════════════════════════════════════
## Option C — Supabase (DB only) + any backend host
═══════════════════════════════════════════════════════════════════════════

1. Create a free project at https://supabase.com
2. Go to Settings → Database → Connection string → URI mode
3. Copy the URI (replace [YOUR-PASSWORD] with your DB password)
4. Use that as DATABASE_URL in your backend's environment

═══════════════════════════════════════════════════════════════════════════
## Troubleshooting
═══════════════════════════════════════════════════════════════════════════

CORS error in browser console:
  → ALLOWED_ORIGINS must include exactly your frontend's origin
  → No trailing slash: https://wikiquiz.netlify.app  (not .../  )

"GEMINI_API_KEY is not set":
  → Check the env var is set in Render/Railway dashboard, not just .env.example

"Database error: relation 'articles' does not exist":
  → Tables are auto-created on startup; check backend logs for SQLAlchemy errors
  → Ensure DATABASE_URL points to the correct database

Render cold-start timeout (30s):
  → Normal on free tier. The frontend shows a spinner during generation.

LLM returns < 3 valid questions:
  → Likely a Gemini quota issue (free tier: 15 req/min, 1500 req/day)
  → Wait 1 minute and retry
