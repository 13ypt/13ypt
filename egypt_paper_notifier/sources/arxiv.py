"""arXiv API 論文検索モジュール"""

import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import requests

from egypt_paper_notifier.models import Paper

logger = logging.getLogger(__name__)

ARXIV_API_URL = "https://export.arxiv.org/api/query"
NAMESPACE = {"atom": "http://www.w3.org/2005/Atom"}


def search(keywords: list[str], max_results: int = 20) -> list[Paper]:
    """arXiv APIでキーワード検索し、論文リストを返す。"""
    query = " OR ".join(f'all:"{kw}"' for kw in keywords if kw.isascii())
    if not query:
        return []

    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    try:
        resp = requests.get(ARXIV_API_URL, params=params, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error("arXiv API request failed: %s", e)
        return []

    return _parse_response(resp.text)


def _parse_response(xml_text: str) -> list[Paper]:
    """arXiv Atom XMLレスポンスをパースする。"""
    papers = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        logger.error("Failed to parse arXiv XML: %s", e)
        return []

    for entry in root.findall("atom:entry", NAMESPACE):
        title_el = entry.find("atom:title", NAMESPACE)
        summary_el = entry.find("atom:summary", NAMESPACE)
        published_el = entry.find("atom:published", NAMESPACE)

        title = title_el.text.strip().replace("\n", " ") if title_el is not None and title_el.text else ""
        abstract = summary_el.text.strip().replace("\n", " ") if summary_el is not None and summary_el.text else ""

        authors = []
        for author_el in entry.findall("atom:author", NAMESPACE):
            name_el = author_el.find("atom:name", NAMESPACE)
            if name_el is not None and name_el.text:
                authors.append(name_el.text.strip())

        url = ""
        for link_el in entry.findall("atom:link", NAMESPACE):
            if link_el.get("type") == "text/html":
                url = link_el.get("href", "")
                break
        if not url:
            id_el = entry.find("atom:id", NAMESPACE)
            url = id_el.text.strip() if id_el is not None and id_el.text else ""

        published_date = None
        if published_el is not None and published_el.text:
            try:
                published_date = datetime.fromisoformat(
                    published_el.text.strip().replace("Z", "+00:00")
                )
            except ValueError:
                pass

        doi = None
        for link_el in entry.findall("atom:link", NAMESPACE):
            href = link_el.get("href", "")
            if "doi.org" in href:
                doi = href.split("doi.org/")[-1]
                break

        if title:
            papers.append(
                Paper(
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    url=url,
                    source="arXiv",
                    published_date=published_date,
                    doi=doi,
                )
            )

    return papers
