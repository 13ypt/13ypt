"""PubMed (NCBI E-utilities) 論文検索モジュール"""

import logging
from datetime import datetime

import requests

from egypt_paper_notifier.models import Paper

logger = logging.getLogger(__name__)

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
PUBMED_BASE_URL = "https://pubmed.ncbi.nlm.nih.gov"


def search(keywords: list[str], max_results: int = 20) -> list[Paper]:
    """PubMed APIでキーワード検索し、論文リストを返す。"""
    ascii_keywords = [kw for kw in keywords if kw.isascii()]
    if not ascii_keywords:
        return []

    query = " OR ".join(f'"{kw}"' for kw in ascii_keywords)

    # Step 1: IDを検索
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "sort": "date",
        "retmode": "json",
    }

    try:
        resp = requests.get(ESEARCH_URL, params=search_params, timeout=30)
        resp.raise_for_status()
        id_list = resp.json().get("esearchresult", {}).get("idlist", [])
    except (requests.RequestException, ValueError, KeyError) as e:
        logger.error("PubMed search failed: %s", e)
        return []

    if not id_list:
        return []

    # Step 2: 詳細を取得
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(id_list),
        "retmode": "xml",
    }

    try:
        resp = requests.get(EFETCH_URL, params=fetch_params, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error("PubMed fetch failed: %s", e)
        return []

    return _parse_xml(resp.text)


def _parse_xml(xml_text: str) -> list[Paper]:
    """PubMed XMLレスポンスをパースする。"""
    import xml.etree.ElementTree as ET

    papers = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        logger.error("Failed to parse PubMed XML: %s", e)
        return []

    for article in root.findall(".//PubmedArticle"):
        medline = article.find(".//MedlineCitation")
        if medline is None:
            continue

        article_el = medline.find(".//Article")
        if article_el is None:
            continue

        title_el = article_el.find(".//ArticleTitle")
        title = _get_text(title_el)
        if not title:
            continue

        abstract_el = article_el.find(".//Abstract/AbstractText")
        abstract = _get_text(abstract_el)

        authors = []
        for author_el in article_el.findall(".//AuthorList/Author"):
            last = _get_text(author_el.find("LastName"))
            first = _get_text(author_el.find("ForeName"))
            name = f"{first} {last}".strip()
            if name:
                authors.append(name)

        pmid_el = medline.find(".//PMID")
        pmid = _get_text(pmid_el)
        url = f"{PUBMED_BASE_URL}/{pmid}/" if pmid else ""

        # DOI
        doi = None
        for id_el in article.findall(".//PubmedData/ArticleIdList/ArticleId"):
            if id_el.get("IdType") == "doi":
                doi = id_el.text
                break

        # 出版日
        published_date = None
        pub_date = article_el.find(".//Journal/JournalIssue/PubDate")
        if pub_date is not None:
            year = _get_text(pub_date.find("Year"))
            month = _get_text(pub_date.find("Month"))
            day = _get_text(pub_date.find("Day"))
            if year:
                try:
                    month_num = _parse_month(month) if month else 1
                    day_num = int(day) if day else 1
                    published_date = datetime(int(year), month_num, day_num)
                except ValueError:
                    pass

        papers.append(
            Paper(
                title=title,
                authors=authors,
                abstract=abstract,
                url=url,
                source="PubMed",
                published_date=published_date,
                doi=doi,
            )
        )

    return papers


def _get_text(el) -> str:
    if el is None:
        return ""
    # ElementTreeのitertext()で子要素テキストも含めて取得
    return "".join(el.itertext()).strip()


def _parse_month(month_str: str) -> int:
    """月の文字列（'Jan', '1', etc.）を数値に変換する。"""
    try:
        return int(month_str)
    except ValueError:
        pass
    months = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4,
        "may": 5, "jun": 6, "jul": 7, "aug": 8,
        "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }
    return months.get(month_str.lower()[:3], 1)
