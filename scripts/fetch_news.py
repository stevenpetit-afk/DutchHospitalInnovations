#!/usr/bin/env python3
"""
fetch_news.py
=============
Haalt dagelijks nieuws op over innovaties uit de 8 Nederlandse UMC's.
Bronnen: Google News RSS, PubMed RSS, directe UMC persberichtenfeeds.
Resultaten worden opgeslagen in data/articles.json.

Gebruik:
    python scripts/fetch_news.py
"""

import json
import os
import re
import hashlib
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup

# ── Configuratie ────────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)

DATA_DIR   = Path(__file__).parent.parent / "data"
OUTPUT_FILE = DATA_DIR / "articles.json"
MAX_ARTICLES = 500          # maximaal te bewaren artikelen
MAX_AGE_DAYS = 90           # artikelen ouder dan dit worden niet opgenomen
REQUEST_TIMEOUT = 15        # seconden

# ── UMC-definities ───────────────────────────────────────────────────────────────

UMCS = {
    "Amsterdam UMC": {
        "feeds": [
            "https://www.amsterdamumc.org/nl/actueel/nieuws.feed.xml",
            "https://news.google.com/rss/search?q=Amsterdam+UMC+innovatie+onderzoek&hl=nl&gl=NL&ceid=NL:nl",
            "https://news.google.com/rss/search?q=%22Amsterdam+UMC%22+doorbraak&hl=nl&gl=NL&ceid=NL:nl",
        ],
        "keywords": ["amsterdam umc", "amc", "vumc", "amsterdam university medical"],
    },
    "Erasmus MC": {
        "feeds": [
            "https://www.erasmusmc.nl/nl-nl/actueel/nieuws.feed.xml",
            "https://news.google.com/rss/search?q=Erasmus+MC+innovatie+onderzoek&hl=nl&gl=NL&ceid=NL:nl",
            "https://news.google.com/rss/search?q=%22Erasmus+MC%22+doorbraak&hl=nl&gl=NL&ceid=NL:nl",
        ],
        "keywords": ["erasmus mc", "erasmus medisch centrum", "erasmus university medical"],
    },
    "LUMC": {
        "feeds": [
            "https://www.lumc.nl/nieuws/?_format=rss",
            "https://news.google.com/rss/search?q=LUMC+Leiden+innovatie+onderzoek&hl=nl&gl=NL&ceid=NL:nl",
            "https://news.google.com/rss/search?q=%22Leids+Universitair+Medisch+Centrum%22+doorbraak&hl=nl&gl=NL&ceid=NL:nl",
        ],
        "keywords": ["lumc", "leids universitair medisch centrum", "leiden university medical center"],
    },
    "Maastricht UMC+": {
        "feeds": [
            "https://www.mumc.nl/nieuws/rss",
            "https://news.google.com/rss/search?q=Maastricht+UMC+innovatie+onderzoek&hl=nl&gl=NL&ceid=NL:nl",
            "https://news.google.com/rss/search?q=%22MUMC%22+doorbraak+medisch&hl=nl&gl=NL&ceid=NL:nl",
        ],
        "keywords": ["maastricht umc", "mumc", "azm", "academisch ziekenhuis maastricht"],
    },
    "Radboudumc": {
        "feeds": [
            "https://www.radboudumc.nl/nieuws?format=rss",
            "https://news.google.com/rss/search?q=Radboudumc+innovatie+onderzoek&hl=nl&gl=NL&ceid=NL:nl",
            "https://news.google.com/rss/search?q=%22Radboudumc%22+doorbraak&hl=nl&gl=NL&ceid=NL:nl",
        ],
        "keywords": ["radboudumc", "radboud umc", "umcn", "universitair medisch centrum nijmegen"],
    },
    "UMCG": {
        "feeds": [
            "https://www.umcg.nl/NL/OVER_HET_UMCG/Nieuws/Paginas/default.aspx?RSS=1",
            "https://news.google.com/rss/search?q=UMCG+Groningen+innovatie+onderzoek&hl=nl&gl=NL&ceid=NL:nl",
            "https://news.google.com/rss/search?q=%22UMCG%22+doorbraak+medisch&hl=nl&gl=NL&ceid=NL:nl",
        ],
        "keywords": ["umcg", "universitair medisch centrum groningen", "university medical center groningen"],
    },
    "UMC Utrecht": {
        "feeds": [
            "https://www.umcutrecht.nl/nl/nieuws.rss",
            "https://news.google.com/rss/search?q=UMC+Utrecht+innovatie+onderzoek&hl=nl&gl=NL&ceid=NL:nl",
            "https://news.google.com/rss/search?q=%22UMC+Utrecht%22+doorbraak&hl=nl&gl=NL&ceid=NL:nl",
        ],
        "keywords": ["umc utrecht", "universitair medisch centrum utrecht", "university medical center utrecht"],
    },
}

# Thematische trefwoorden voor het taggen van artikelen
TOPIC_KEYWORDS = {
    "AI & machine learning":     ["kunstmatige intelligentie", "machine learning", "deep learning", "ai ", "algoritme", "neural"],
    "Kanker & oncologie":        ["kanker", "tumor", "oncologie", "chemotherapie", "immunotherapie", "carcinoom"],
    "Genomica & genetica":       ["dna", "gen", "genome", "genomica", "crispr", "erfelijk", "mutatie", "genetisch"],
    "Neurologie":                ["hersenen", "neurologie", "parkinson", "alzheimer", "beroerte", "ms ", "multiple sclerose"],
    "Cardiologie":               ["hart", "hartziek", "cardiologie", "vaatziekte", "hartfalen", "stent"],
    "Chirurgie & robotica":      ["robot", "chirurgie", "laparoscoop", "minimalinvasief", "operatietechniek"],
    "Farmacologie":              ["medicijn", "geneesmiddel", "therapie", "behandeling", "klinische studie", "trial"],
    "Diagnostiek & beeldvorming":["mri", "ct-scan", "diagnose", "biomarker", "echografie", "röntgen"],
    "Regeneratieve geneeskunde": ["stamcel", "organoïde", "weefsel", "regeneratief", "transplantatie"],
    "Infectieziekten":           ["infectie", "bacterie", "virus", "antibiotica", "vaccinatie", "vaccin", "covid", "pandemie"],
    "Zeldzame ziekten":          ["zeldzame ziekte", "orphan drug", "weesgeneesmiddel"],
    "Subsidie & samenwerking":   ["subsidie", "eu-project", "samenwerking", "consortium", "zon mw", "health~holland"],
}

# Innovatie-gerelateerde trefwoorden (minstens één moet matchen voor inclusie)
INNOVATION_KEYWORDS = [
    "innovatie", "doorbraak", "ontdekking", "onderzoek", "studie", "trial",
    "therapie", "behandeling", "technologie", "robot", "ai ", "kunstmatige intelligentie",
    "nieuw", "eerste", "revolutionair", "methode", "vaccin", "geneesmiddel",
    "klinisch", "patent", "subsidie", "prijs", "award",
]

# ── Hulpfuncties ─────────────────────────────────────────────────────────────────

def fetch_feed(url: str) -> list[dict]:
    """Haalt een RSS/Atom-feed op en geeft een lijst van entry-dicts terug."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; UMCInnovatiesBot/1.0)"}
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        return feed.entries
    except Exception as e:
        log.warning(f"Feed mislukt ({url}): {e}")
        return []


def clean_html(html_text: str) -> str:
    """Verwijdert HTML-tags uit een string."""
    if not html_text:
        return ""
    return BeautifulSoup(html_text, "html.parser").get_text(" ", strip=True)


def truncate(text: str, max_chars: int = 280) -> str:
    """Knipt tekst af op een zingrens."""
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars].rfind(" ")
    return text[: cut if cut > 0 else max_chars].rstrip(".,;:!?") + "…"


def article_id(url: str, title: str) -> str:
    """Stabiele unieke ID voor een artikel."""
    return hashlib.md5(f"{url}|{title}".encode()).hexdigest()


def parse_date(entry) -> datetime | None:
    """Probeert een publicatiedatum uit een feedparser entry te halen."""
    for attr in ("published_parsed", "updated_parsed", "created_parsed"):
        val = getattr(entry, attr, None)
        if val:
            try:
                return datetime(*val[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return None


def assign_tags(text: str) -> list[str]:
    """Kent thematische tags toe op basis van trefwoorden in de tekst."""
    text_lower = text.lower()
    tags = []
    for topic, kws in TOPIC_KEYWORDS.items():
        if any(kw in text_lower for kw in kws):
            tags.append(topic)
    return tags


def is_innovation_relevant(text: str) -> bool:
    """Controleert of een artikel voldoende innovatiegerelateerd is."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in INNOVATION_KEYWORDS)


def umc_matches(text: str, umc_keywords: list[str]) -> bool:
    """Controleert of het artikel daadwerkelijk over dit UMC gaat."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in umc_keywords)


def get_source_name(url: str) -> str:
    """Leidt een leesbare bronnaam af uit een URL."""
    try:
        domain = urlparse(url).netloc.lower()
        domain = re.sub(r"^www\.", "", domain)
        return domain.split(".")[0].upper() if "." in domain else domain
    except Exception:
        return "Onbekend"

# ── Hoofdlogica ───────────────────────────────────────────────────────────────────

def fetch_for_umc(umc_name: str, config: dict) -> list[dict]:
    """Haalt nieuws op voor één UMC en geeft genormaliseerde artikeldicts terug."""
    articles = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)

    for feed_url in config["feeds"]:
        log.info(f"  → Ophalen: {feed_url[:80]}…")
        entries = fetch_feed(feed_url)

        for entry in entries:
            title = clean_html(getattr(entry, "title", "")).strip()
            if not title:
                continue

            # Datum
            pub_date = parse_date(entry)
            if pub_date and pub_date < cutoff:
                continue

            # URL
            link = getattr(entry, "link", "")
            if not link:
                continue

            # Samenvatting
            summary_raw = (
                getattr(entry, "summary", "")
                or getattr(entry, "description", "")
                or ""
            )
            summary = truncate(clean_html(summary_raw))

            # Volledige tekst voor relevantiechecks
            full_text = f"{title} {summary}"

            # Filter: moet innovatiegerelateerd zijn
            if not is_innovation_relevant(full_text):
                continue

            # Filter: voor Google News-feeds ook UMC-naam controleren
            if "news.google.com" in feed_url and not umc_matches(full_text, config["keywords"]):
                continue

            tags = assign_tags(full_text)

            article = {
                "id":        article_id(link, title),
                "umc":       umc_name,
                "title":     title,
                "summary":   summary,
                "url":       link,
                "source":    get_source_name(link),
                "published": pub_date.isoformat() if pub_date else datetime.now(timezone.utc).isoformat(),
                "tags":      tags,
            }
            articles.append(article)

    return articles


def deduplicate(articles: list[dict]) -> list[dict]:
    """Verwijdert dubbele artikelen op basis van ID."""
    seen = set()
    unique = []
    for a in articles:
        if a["id"] not in seen:
            seen.add(a["id"])
            unique.append(a)
    return unique


def load_existing() -> list[dict]:
    """Laadt bestaande artikelen uit het outputbestand als dat bestaat."""
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE, encoding="utf-8") as f:
                data = json.load(f)
            return data.get("articles", [])
        except Exception as e:
            log.warning(f"Kon bestaande data niet laden: {e}")
    return []


def save(articles: list[dict]) -> None:
    """Slaat artikelen op als JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "total": len(articles),
        "articles": articles,
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    log.info(f"✓ Opgeslagen: {len(articles)} artikelen → {OUTPUT_FILE}")


# ── Entry point ───────────────────────────────────────────────────────────────────

def main():
    log.info("=" * 60)
    log.info("UMC Innovaties — nieuws ophalen")
    log.info(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log.info("=" * 60)

    new_articles = []

    for umc_name, config in UMCS.items():
        log.info(f"\n[{umc_name}]")
        articles = fetch_for_umc(umc_name, config)
        log.info(f"  Gevonden: {len(articles)} artikelen")
        new_articles.extend(articles)

    # Samenvoegen met bestaande artikelen
    existing = load_existing()
    combined = deduplicate(new_articles + existing)

    # Sorteren op datum (nieuwste eerst)
    def sort_key(a):
        try:
            return datetime.fromisoformat(a["published"])
        except Exception:
            return datetime.min.replace(tzinfo=timezone.utc)

    combined.sort(key=sort_key, reverse=True)

    # Maximaal aantal bewaren
    combined = combined[:MAX_ARTICLES]

    save(combined)

    log.info("\n" + "=" * 60)
    log.info(f"Klaar! Totaal: {len(combined)} unieke artikelen")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
