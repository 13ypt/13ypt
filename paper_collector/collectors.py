"""
Paper collectors using free academic APIs.
無料の学術APIを使った論文収集モジュール

Supported sources:
  - OpenAlex (https://openalex.org/) — free, comprehensive
  - CrossRef (https://www.crossref.org/) — free, DOI-based metadata
"""

import time
import logging
from datetime import datetime, timedelta

import requests

from . import config

logger = logging.getLogger(__name__)


def _make_session(email=None):
    session = requests.Session()
    session.headers.update({"User-Agent": "EgyptPaperCollector/1.0"})
    if email:
        session.headers["User-Agent"] += f" (mailto:{email})"
    return session


# ---------------------------------------------------------------------------
# OpenAlex collector
# ---------------------------------------------------------------------------

def collect_openalex(days_back=None):
    """
    Search OpenAlex for papers matching configured queries.
    Returns a list of paper dicts.
    """
    if days_back is None:
        days_back = config.DEFAULT_DAYS_BACK

    from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    session = _make_session(config.OPENALEX_EMAIL)
    papers = []

    for query in config.SEARCH_QUERIES:
        logger.info("OpenAlex: searching '%s' from %s", query, from_date)
        params = {
            "search": query,
            "filter": f"from_publication_date:{from_date}",
            "per_page": min(config.MAX_RESULTS_PER_QUERY, 200),
            "sort": "publication_date:desc",
        }
        if config.OPENALEX_EMAIL:
            params["mailto"] = config.OPENALEX_EMAIL

        try:
            resp = session.get(
                f"{config.OPENALEX_BASE_URL}/works", params=params, timeout=30
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            logger.warning("OpenAlex request failed for '%s': %s", query, e)
            time.sleep(config.REQUEST_DELAY)
            continue

        for work in data.get("results", []):
            authors = ", ".join(
                a.get("author", {}).get("display_name", "")
                for a in work.get("authorships", [])
            )
            doi = work.get("doi", "")
            if doi and doi.startswith("https://doi.org/"):
                doi = doi[len("https://doi.org/"):]

            paper = {
                "title": work.get("title", ""),
                "authors": authors,
                "abstract": _reconstruct_abstract(work.get("abstract_inverted_index")),
                "doi": doi or None,
                "url": work.get("primary_location", {}).get("landing_page_url", "")
                       or work.get("id", ""),
                "published_date": work.get("publication_date", ""),
                "source": "OpenAlex",
                "query_matched": query,
            }
            papers.append(paper)

        time.sleep(config.REQUEST_DELAY)

    logger.info("OpenAlex: found %d papers total", len(papers))
    return papers


def _reconstruct_abstract(inverted_index):
    """Reconstruct abstract text from OpenAlex inverted index format."""
    if not inverted_index:
        return ""
    word_positions = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort()
    return " ".join(w for _, w in word_positions)


# ---------------------------------------------------------------------------
# CrossRef collector
# ---------------------------------------------------------------------------

def collect_crossref(days_back=None):
    """
    Search CrossRef for papers matching configured queries.
    Returns a list of paper dicts.
    """
    if days_back is None:
        days_back = config.DEFAULT_DAYS_BACK

    from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    session = _make_session(config.CROSSREF_EMAIL)
    papers = []

    for query in config.SEARCH_QUERIES:
        logger.info("CrossRef: searching '%s' from %s", query, from_date)
        params = {
            "query": query,
            "filter": f"from-pub-date:{from_date}",
            "rows": min(config.MAX_RESULTS_PER_QUERY, 100),
            "sort": "published",
            "order": "desc",
        }

        try:
            resp = session.get(
                f"{config.CROSSREF_BASE_URL}/works", params=params, timeout=30
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            logger.warning("CrossRef request failed for '%s': %s", query, e)
            time.sleep(config.REQUEST_DELAY)
            continue

        for item in data.get("message", {}).get("items", []):
            title_parts = item.get("title", [])
            title = title_parts[0] if title_parts else ""

            authors = ", ".join(
                f"{a.get('given', '')} {a.get('family', '')}".strip()
                for a in item.get("author", [])
            )

            pub_date = ""
            date_parts = item.get("published-print", item.get("published-online", {}))
            if date_parts and date_parts.get("date-parts"):
                parts = date_parts["date-parts"][0]
                pub_date = "-".join(str(p).zfill(2) for p in parts if p)

            paper = {
                "title": title,
                "authors": authors,
                "abstract": _clean_html(item.get("abstract", "")),
                "doi": item.get("DOI"),
                "url": item.get("URL", ""),
                "published_date": pub_date,
                "source": "CrossRef",
                "query_matched": query,
            }
            papers.append(paper)

        time.sleep(config.REQUEST_DELAY)

    logger.info("CrossRef: found %d papers total", len(papers))
    return papers


def _clean_html(text):
    """Remove simple HTML/JATS tags from abstract text."""
    if not text:
        return ""
    import re
    return re.sub(r"<[^>]+>", "", text).strip()


# ---------------------------------------------------------------------------
# Combined collector
# ---------------------------------------------------------------------------

def collect_all(days_back=None):
    """Run all collectors and return combined results."""
    papers = []
    papers.extend(collect_openalex(days_back))
    papers.extend(collect_crossref(days_back))
    return papers
