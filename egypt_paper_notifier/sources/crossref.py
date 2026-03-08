"""CrossRef API 論文検索モジュール"""

import logging
from datetime import datetime

import requests

from egypt_paper_notifier.models import Paper

logger = logging.getLogger(__name__)

CROSSREF_API_URL = "https://api.crossref.org/works"


def search(keywords: list[str], max_results: int = 20) -> list[Paper]:
    """CrossRef APIでキーワード検索し、論文リストを返す。"""
    ascii_keywords = [kw for kw in keywords if kw.isascii()]
    if not ascii_keywords:
        return []

    query = " OR ".join(ascii_keywords)

    params = {
        "query": query,
        "rows": max_results,
        "sort": "published",
        "order": "desc",
        "filter": "type:journal-article",
    }

    headers = {
        "User-Agent": "EgyptPaperNotifier/1.0 (https://github.com/egypt-paper-notifier; mailto:user@example.com)",
    }

    try:
        resp = requests.get(CROSSREF_API_URL, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error("CrossRef API request failed: %s", e)
        return []

    return _parse_response(resp.json())


def _parse_response(data: dict) -> list[Paper]:
    """CrossRef JSONレスポンスをパースする。"""
    papers = []
    items = data.get("message", {}).get("items", [])

    for item in items:
        title_list = item.get("title", [])
        title = title_list[0] if title_list else ""
        if not title:
            continue

        authors = []
        for author in item.get("author", []):
            given = author.get("given", "")
            family = author.get("family", "")
            name = f"{given} {family}".strip()
            if name:
                authors.append(name)

        abstract = item.get("abstract", "")
        # CrossRefの抄録にはHTMLタグが含まれる場合がある
        if abstract:
            import re
            abstract = re.sub(r"<[^>]+>", "", abstract).strip()

        doi = item.get("DOI", "")
        url = item.get("URL", f"https://doi.org/{doi}" if doi else "")

        published_date = None
        date_parts = item.get("published", {}).get("date-parts", [[]])
        if date_parts and date_parts[0]:
            parts = date_parts[0]
            try:
                year = parts[0]
                month = parts[1] if len(parts) > 1 else 1
                day = parts[2] if len(parts) > 2 else 1
                published_date = datetime(year, month, day)
            except (ValueError, IndexError):
                pass

        papers.append(
            Paper(
                title=title,
                authors=authors,
                abstract=abstract,
                url=url,
                source="CrossRef",
                published_date=published_date,
                doi=doi if doi else None,
            )
        )

    return papers
