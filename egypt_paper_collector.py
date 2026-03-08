#!/usr/bin/env python3
"""
Egypt Paper Collector
=====================
Automatically collects academic papers related to ancient Egyptian animal cults
and the Ptolemaic dynasty from multiple open-access APIs.

Sources:
  - OpenAlex (https://openalex.org/) — free, no API key required
  - CrossRef (https://api.crossref.org/) — free, no API key required
  - CORE (https://core.ac.uk/) — optional, API key recommended for higher rate limits

Usage:
  python egypt_paper_collector.py                  # default search
  python egypt_paper_collector.py --max-results 50 # limit results
  python egypt_paper_collector.py --output results.csv --format csv
  python egypt_paper_collector.py --custom-query "Ptolemaic temple ritual"
"""

import argparse
import csv
import json
import logging
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Paper:
    title: str
    authors: list[str] = field(default_factory=list)
    year: Optional[int] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    abstract: Optional[str] = None
    source_api: str = ""
    journal: Optional[str] = None

    @property
    def dedup_key(self) -> str:
        """Key used for deduplication."""
        if self.doi:
            return self.doi.lower().strip()
        return self.title.lower().strip()


# ---------------------------------------------------------------------------
# Predefined search queries
# ---------------------------------------------------------------------------

QUERIES = [
    "ancient Egypt animal cult",
    "Ptolemaic Egypt animal worship",
    "Egyptian animal mummy",
    "sacred animal Ptolemaic",
    "crocodile worship Egypt",
    "ibis cult Egypt",
    "falcon catacomb Saqqara",
    "animal catacomb Egypt",
    "Ptolemaic temple animal",
    "Serapeum Saqqara",
    "Tuna el-Gebel animal",
    "Bucheum Armant",
]

# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------

_USER_AGENT = "EgyptPaperCollector/1.0 (academic research; mailto:example@example.com)"


def _http_get(url: str, headers: Optional[dict] = None, retries: int = 3) -> dict:
    """Perform a GET request and return parsed JSON."""
    hdrs = {"User-Agent": _USER_AGENT, "Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, headers=hdrs)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            wait = 2 ** (attempt + 1)
            logger.warning("Request failed (%s), retrying in %ds…", exc, wait)
            time.sleep(wait)
    logger.error("Failed after %d retries: %s", retries, url)
    return {}


# ---------------------------------------------------------------------------
# OpenAlex client
# ---------------------------------------------------------------------------

class OpenAlexClient:
    """Search papers via the OpenAlex API (free, no key required)."""

    BASE = "https://api.openalex.org/works"

    def search(self, query: str, per_page: int = 25) -> list[Paper]:
        params = urllib.parse.urlencode({
            "search": query,
            "per_page": min(per_page, 200),
            "sort": "relevance_score:desc",
        })
        url = f"{self.BASE}?{params}"
        data = _http_get(url)
        results: list[Paper] = []
        for item in data.get("results", []):
            authors = []
            for authorship in item.get("authorships", []):
                name = authorship.get("author", {}).get("display_name")
                if name:
                    authors.append(name)
            paper = Paper(
                title=item.get("title") or "(no title)",
                authors=authors,
                year=item.get("publication_year"),
                doi=item.get("doi"),
                url=item.get("id"),
                abstract=self._reconstruct_abstract(item.get("abstract_inverted_index")),
                source_api="OpenAlex",
                journal=(item.get("primary_location") or {}).get("source", {}).get("display_name") if item.get("primary_location") else None,
            )
            results.append(paper)
        return results

    @staticmethod
    def _reconstruct_abstract(inverted_index: Optional[dict]) -> Optional[str]:
        if not inverted_index:
            return None
        word_positions: list[tuple[int, str]] = []
        for word, positions in inverted_index.items():
            for pos in positions:
                word_positions.append((pos, word))
        word_positions.sort()
        return " ".join(w for _, w in word_positions)


# ---------------------------------------------------------------------------
# CrossRef client
# ---------------------------------------------------------------------------

class CrossRefClient:
    """Search papers via the CrossRef API (free, no key required)."""

    BASE = "https://api.crossref.org/works"

    def search(self, query: str, rows: int = 25) -> list[Paper]:
        params = urllib.parse.urlencode({
            "query": query,
            "rows": min(rows, 1000),
            "sort": "relevance",
            "order": "desc",
        })
        url = f"{self.BASE}?{params}"
        data = _http_get(url)
        results: list[Paper] = []
        for item in data.get("message", {}).get("items", []):
            authors = []
            for author in item.get("author", []):
                given = author.get("given", "")
                family = author.get("family", "")
                name = f"{given} {family}".strip()
                if name:
                    authors.append(name)
            title_parts = item.get("title", [])
            title = title_parts[0] if title_parts else "(no title)"
            year = None
            date_parts = (item.get("published-print") or item.get("published-online") or {}).get("date-parts", [[]])
            if date_parts and date_parts[0]:
                year = date_parts[0][0]
            journal_titles = item.get("container-title", [])
            paper = Paper(
                title=title,
                authors=authors,
                year=year,
                doi=item.get("DOI"),
                url=item.get("URL"),
                abstract=item.get("abstract"),
                source_api="CrossRef",
                journal=journal_titles[0] if journal_titles else None,
            )
            results.append(paper)
        return results


# ---------------------------------------------------------------------------
# CORE client (optional)
# ---------------------------------------------------------------------------

class COREClient:
    """Search papers via the CORE API. API key is optional but recommended."""

    BASE = "https://api.core.ac.uk/v3/search/works"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def search(self, query: str, limit: int = 25) -> list[Paper]:
        if not self.api_key:
            logger.info("CORE API key not set — skipping CORE search.")
            return []
        params = urllib.parse.urlencode({
            "q": query,
            "limit": min(limit, 100),
        })
        url = f"{self.BASE}?{params}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = _http_get(url, headers=headers)
        results: list[Paper] = []
        for item in data.get("results", []):
            authors = [a.get("name", "") for a in item.get("authors", []) if a.get("name")]
            paper = Paper(
                title=item.get("title") or "(no title)",
                authors=authors,
                year=item.get("yearPublished"),
                doi=item.get("doi"),
                url=item.get("downloadUrl") or item.get("sourceFulltextUrls", [None])[0] if item.get("sourceFulltextUrls") else None,
                abstract=item.get("abstract"),
                source_api="CORE",
                journal=item.get("publisher"),
            )
            results.append(paper)
        return results


# ---------------------------------------------------------------------------
# Collector (orchestrates all sources)
# ---------------------------------------------------------------------------

class PaperCollector:
    def __init__(self, core_api_key: Optional[str] = None):
        self.openalex = OpenAlexClient()
        self.crossref = CrossRefClient()
        self.core = COREClient(api_key=core_api_key)

    def collect(
        self,
        queries: Optional[list[str]] = None,
        per_source: int = 25,
    ) -> list[Paper]:
        queries = queries or QUERIES
        seen: dict[str, Paper] = {}
        total_queries = len(queries)

        for i, query in enumerate(queries, 1):
            logger.info("[%d/%d] Searching: %s", i, total_queries, query)

            # --- OpenAlex ---
            for paper in self.openalex.search(query, per_page=per_source):
                key = paper.dedup_key
                if key not in seen:
                    seen[key] = paper
            time.sleep(0.5)

            # --- CrossRef ---
            for paper in self.crossref.search(query, rows=per_source):
                key = paper.dedup_key
                if key not in seen:
                    seen[key] = paper
            time.sleep(0.5)

            # --- CORE ---
            for paper in self.core.search(query, limit=per_source):
                key = paper.dedup_key
                if key not in seen:
                    seen[key] = paper
            time.sleep(0.3)

        papers = list(seen.values())
        papers.sort(key=lambda p: (p.year or 0), reverse=True)
        return papers


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def _strip_html(text: Optional[str]) -> Optional[str]:
    """Remove simple HTML/XML tags from text (e.g. CrossRef abstracts)."""
    if not text:
        return text
    import re
    return re.sub(r"<[^>]+>", "", text).strip()


def write_json(papers: list[Paper], path: str) -> None:
    records = []
    for p in papers:
        d = asdict(p)
        d["abstract"] = _strip_html(d.get("abstract"))
        records.append(d)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    logger.info("Wrote %d papers to %s", len(papers), path)


def write_csv(papers: list[Paper], path: str) -> None:
    fieldnames = ["title", "authors", "year", "doi", "url", "journal", "source_api", "abstract"]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in papers:
            d = asdict(p)
            d["authors"] = "; ".join(d["authors"])
            d["abstract"] = _strip_html(d.get("abstract"))
            # Remove the dedup_key helper field
            d.pop("dedup_key", None)
            writer.writerow({k: d[k] for k in fieldnames})
    logger.info("Wrote %d papers to %s", len(papers), path)


def print_summary(papers: list[Paper]) -> None:
    print(f"\n{'='*70}")
    print(f" Collected {len(papers)} unique papers")
    print(f"{'='*70}\n")
    for i, p in enumerate(papers, 1):
        authors_str = "; ".join(p.authors[:3])
        if len(p.authors) > 3:
            authors_str += " et al."
        year_str = str(p.year) if p.year else "n.d."
        print(f"  [{i:3d}] ({year_str}) {p.title}")
        if authors_str:
            print(f"        Authors: {authors_str}")
        if p.journal:
            print(f"        Journal: {p.journal}")
        if p.doi:
            print(f"        DOI: {p.doi}")
        print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Collect academic papers on ancient Egyptian animal cults and the Ptolemaic dynasty.",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file path (default: prints summary to stdout).",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json).",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=25,
        help="Max results per query per source (default: 25).",
    )
    parser.add_argument(
        "--custom-query", "-q",
        action="append",
        default=None,
        help="Add a custom search query (can be used multiple times). "
             "If provided, only custom queries are used.",
    )
    parser.add_argument(
        "--core-api-key",
        default=None,
        help="API key for CORE (optional). Can also be set via CORE_API_KEY env var.",
    )
    args = parser.parse_args()

    import os
    core_key = args.core_api_key or os.environ.get("CORE_API_KEY")
    queries = args.custom_query  # None means use defaults

    collector = PaperCollector(core_api_key=core_key)
    papers = collector.collect(queries=queries, per_source=args.max_results)

    if not papers:
        logger.warning("No papers found.")
        sys.exit(0)

    print_summary(papers)

    if args.output:
        if args.format == "csv":
            write_csv(papers, args.output)
        else:
            write_json(papers, args.output)
    else:
        # Default: write to timestamped JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_path = f"egypt_papers_{timestamp}.json"
        write_json(papers, default_path)


if __name__ == "__main__":
    main()
