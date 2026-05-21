import json
import logging
import re
import urllib.request
from app.core.config import settings

logger = logging.getLogger(__name__)

QUIZ_PROMPT = """You are an expert quiz writer. Create a quiz based ONLY on this Wikipedia article.

TITLE: {title}
SECTIONS: {sections}
TEXT: {article_text}

Generate EXACTLY {num_questions} questions. Each must have:
- "question": the question
- "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}}
- "answer": "A" or "B" or "C" or "D"
- "difficulty": "easy" or "medium" or "hard"
- "explanation": one sentence explanation

Return ONLY a valid JSON array. No markdown. No extra text."""


def _call_api(prompt_text):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.GEMINI_API_KEY}",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "WikiQuiz",
    }
    body = json.dumps({
        "model": "openrouter/auto",
        "messages": [{"role": "user", "content": prompt_text}],
        "max_tokens": 4096,
    }).encode()
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        raise RuntimeError(f"API error {e.code}: {error_body}")


def _parse_json(raw):
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    match = re.search(r"\[.*\]", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)
    return json.loads(cleaned)


def generate_quiz(title, article_text, sections, num_questions=7):
    prompt = QUIZ_PROMPT.format(
        title=title,
        sections=", ".join(sections) if sections else "General",
        article_text=article_text[:10000],
        num_questions=num_questions,
    )
    logger.info("Calling OpenRouter API...")
    raw = _call_api(prompt)
    logger.info("Got response: %s", raw[:200])
    questions = _parse_json(raw)
    valid = []
    for q in questions:
        if all(k in q for k in ["question", "options", "answer", "difficulty", "explanation"]):
            if all(k in q["options"] for k in ["A", "B", "C", "D"]):
                valid.append(q)
    logger.info("Valid questions: %d", len(valid))
    return valid


def generate_related_topics(title, summary, existing_topics):
    try:
        prompt = f"""Suggest 8 related Wikipedia article titles for: {title}
Existing: {", ".join(existing_topics)}
Return ONLY a JSON array of strings. No markdown. Example: ["Topic 1", "Topic 2"]"""
        raw = _call_api(prompt)
        topics = _parse_json(raw)
        if isinstance(topics, list):
            return list(dict.fromkeys(existing_topics + [str(t) for t in topics]))[:10]
    except Exception as e:
        logger.warning("Related topics failed: %s", e)
    return existing_topics