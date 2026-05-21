"""
app/services/scraper.py
────────────────────────
Scrapes a Wikipedia article URL with requests + BeautifulSoup.

Extracts:
  - title          – the article's <h1> heading
  - summary        – first two non-empty paragraphs (lead section)
  - sections       – all <h2> / <h3> headings (table of contents)
  - key_entities   – naive NER: capitalised tokens grouped into
                     people / organizations / locations using
                     keyword heuristics (no heavy NLP dependency)
  - related_topics – "See also" links from the Wikipedia article
  - raw_text       – full visible text (for LLM context)
"""

import re
import logging
from typing import Any

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "WikiQuizBot/1.0 (educational project; "
        "contact: wikiquizbot@example.com)"
    )
}
REQUEST_TIMEOUT = 15  # seconds

# Keyword hints used for lightweight entity classification
PEOPLE_HINTS    = {"born", "died", "mathematician", "scientist", "engineer",
                   "philosopher", "politician", "author", "artist", "professor",
                   "director", "founder", "president", "minister", "general"}
ORG_HINTS       = {"university", "college", "institute", "academy", "school",
                   "corporation", "company", "association", "society",
                   "department", "ministry", "committee", "laboratory", "lab",
                   "park", "bletchley", "cia", "fbi", "nasa", "mit", "ibm"}
LOC_HINTS       = {"kingdom", "states", "country", "city", "town", "republic",
                   "island", "ocean", "river", "mountain", "continent",
                   "england", "france", "germany", "india", "china", "japan",
                   "london", "paris", "berlin", "washington", "york", "cambridge"}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _clean_text(text: str) -> str:
    """Collapse whitespace and strip citation brackets like [1], [note 2]."""
    text = re.sub(r"\[\d+\]|\[note \d+\]|\[a\]|\[b\]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _classify_entity(name: str) -> str:
    """Return 'people' | 'organizations' | 'locations' | 'other'."""
    lower = name.lower()
    if any(h in lower for h in LOC_HINTS):
        return "locations"
    if any(h in lower for h in ORG_HINTS):
        return "organizations"
    # Multi-word, each word capitalised → likely a person name
    parts = name.split()
    if len(parts) >= 2 and all(p[0].isupper() for p in parts if p):
        return "people"
    return "other"


def _extract_entities(soup: BeautifulSoup) -> dict[str, list[str]]:
    """
    Extract named entities from the article body using simple heuristics:
      1. Grab all <b> tags in the first few sections (Wikipedia bolds key terms).
      2. Pull <a> hrefs that look like /wiki/Person_Name patterns.
      3. Deduplicate and classify.
    """
    entities: dict[str, list[str]] = {"people": [], "organizations": [], "locations": []}

    # Bold tags (first ~5 000 chars worth of content)
    body_div = soup.find("div", {"id": "mw-content-text"})
    if not body_div:
        return entities

    seen: set[str] = set()

    # Strategy 1 – bold text in lead
    for tag in body_div.find_all("b")[:40]:
        name = _clean_text(tag.get_text())
        if 2 < len(name) < 60 and name not in seen:
            seen.add(name)
            cat = _classify_entity(name)
            if cat != "other":
                entities[cat].append(name)

    # Strategy 2 – internal wiki links that look like named entities
    for a in body_div.find_all("a", href=True)[:200]:
        href: str = a["href"]
        if href.startswith("/wiki/") and ":" not in href:
            name = href.replace("/wiki/", "").replace("_", " ")
            # Keep only multi-word, all-caps-first tokens
            parts = name.split()
            if (
                len(parts) >= 2
                and all(p[0].isupper() for p in parts if p)
                and name not in seen
                and len(name) < 60
            ):
                seen.add(name)
                cat = _classify_entity(name)
                if cat != "other":
                    entities[cat].append(name)

    # Deduplicate preserving order, limit to 10 per category
    for cat in entities:
        seen_cat: list[str] = []
        for item in entities[cat]:
            if item not in seen_cat:
                seen_cat.append(item)
        entities[cat] = seen_cat[:10]

    return entities


def _extract_related_topics(soup: BeautifulSoup) -> list[str]:
    """Pull links from the 'See also' section."""
    topics: list[str] = []
    see_also_heading = soup.find(id="See_also")
    if see_also_heading:
        section = see_also_heading.find_parent(["h2", "h3"])
        if section:
            ul = section.find_next_sibling("ul")
            if ul:
                for li in ul.find_all("li"):
                    text = _clean_text(li.get_text())
                    if text:
                        topics.append(text)
    return topics[:10]


# ── Main scrape function ─────────────────────────────────────────────────────

def scrape_wikipedia(url: str) -> dict[str, Any]:
    """
    Fetch and parse a Wikipedia article.

    Returns a dict with keys:
        title, summary, sections, key_entities, related_topics, raw_text

    Raises:
        ValueError  – if the URL is not a Wikipedia article URL
        RuntimeError – on network / parse failures
    """
    # ── Validate URL ──────────────────────────────────────────────────────
    if "wikipedia.org/wiki/" not in url:
        raise ValueError(
            f"Not a valid Wikipedia article URL: {url!r}. "
            "Expected a URL like https://en.wikipedia.org/wiki/Alan_Turing"
        )

    # ── Fetch ─────────────────────────────────────────────────────────────
    logger.info("Fetching Wikipedia URL: %s", url)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Request timed out after {REQUEST_TIMEOUT}s for URL: {url}")
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.response.status_code} fetching {url}: {exc}")
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Network error fetching {url}: {exc}")

    # ── Parse ─────────────────────────────────────────────────────────────
    soup = BeautifulSoup(resp.text, "lxml")

    # Title
    title_tag = soup.find("h1", {"id": "firstHeading"}) or soup.find("h1")
    title = _clean_text(title_tag.get_text()) if title_tag else "Unknown Title"

    # Summary – first 2 substantial paragraphs from the lead section
    content_div = soup.find("div", {"id": "mw-content-text"})
    summary_parts: list[str] = []
    if content_div:
        for p in content_div.find_all("p"):
            text = _clean_text(p.get_text())
            if len(text) > 80:          # skip stubs / empty paras
                summary_parts.append(text)
            if len(summary_parts) >= 2:
                break
    summary = " ".join(summary_parts) or "No summary available."

    # Sections – all h2 / h3 headings (skip meta headings)
    skip_headings = {
        "See also", "References", "Further reading",
        "External links", "Notes", "Citations", "Bibliography"
    }
    sections: list[str] = []
    for heading in soup.find_all(["h2", "h3"]):
        span = heading.find("span", {"class": "mw-headline"})
        text = _clean_text(span.get_text() if span else heading.get_text())
        if text and text not in skip_headings:
            sections.append(text)

    # Key entities
    key_entities = _extract_entities(soup)

    # Related topics
    related_topics = _extract_related_topics(soup)

    # Raw text – all paragraphs joined (used as LLM context)
    all_paragraphs = [
        _clean_text(p.get_text())
        for p in (content_div.find_all("p") if content_div else [])
        if len(_clean_text(p.get_text())) > 40
    ]
    raw_text = "\n\n".join(all_paragraphs)

    # ── Warn if thin article ──────────────────────────────────────────────
    if len(raw_text) < 500:
        logger.warning("Article text is very short (%d chars). Quiz quality may be low.", len(raw_text))

    logger.info(
        "Scraped '%s': %d sections, %d chars of text",
        title, len(sections), len(raw_text)
    )

    return {
        "title":          title,
        "summary":        summary,
        "sections":       sections,
        "key_entities":   key_entities,
        "related_topics": related_topics,
        "raw_text":       raw_text[:15_000],   # cap at 15k chars – fits in LLM context
    }
