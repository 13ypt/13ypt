"""統合論文検索モジュール"""

import logging

from egypt_paper_notifier.config import Config
from egypt_paper_notifier.models import Paper

logger = logging.getLogger(__name__)


def search_all_sources(config: Config) -> list[Paper]:
    """有効な全ソースから論文を検索し、統合リストを返す。"""
    all_papers: list[Paper] = []

    if config.sources.get("arxiv", True):
        logger.info("arXiv を検索中...")
        from egypt_paper_notifier.sources import arxiv
        papers = arxiv.search(config.keywords)
        logger.info("arXiv: %d件", len(papers))
        all_papers.extend(papers)

    if config.sources.get("crossref", True):
        logger.info("CrossRef を検索中...")
        from egypt_paper_notifier.sources import crossref
        papers = crossref.search(config.keywords)
        logger.info("CrossRef: %d件", len(papers))
        all_papers.extend(papers)

    if config.sources.get("pubmed", True):
        logger.info("PubMed を検索中...")
        from egypt_paper_notifier.sources import pubmed
        papers = pubmed.search(config.keywords)
        logger.info("PubMed: %d件", len(papers))
        all_papers.extend(papers)

    # DOIによる重複排除
    seen_ids: set[str] = set()
    unique_papers: list[Paper] = []
    for paper in all_papers:
        uid = paper.unique_id
        if uid not in seen_ids:
            seen_ids.add(uid)
            unique_papers.append(paper)

    logger.info("合計: %d件（重複排除後）", len(unique_papers))
    return unique_papers
