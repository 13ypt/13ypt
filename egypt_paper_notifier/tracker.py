"""既読論文の追跡管理モジュール"""

import logging
from pathlib import Path

import yaml

from egypt_paper_notifier.models import Paper

logger = logging.getLogger(__name__)


class SeenTracker:
    """既に通知済みの論文を追跡し、重複通知を防ぐ。"""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._seen_ids: set[str] = set()
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                with open(self.path, encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                self._seen_ids = set(data.get("seen", []))
                logger.debug("既読論文 %d件を読み込みました", len(self._seen_ids))
            except Exception as e:
                logger.error("既読データの読み込みに失敗: %s", e)
                self._seen_ids = set()

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            yaml.dump({"seen": sorted(self._seen_ids)}, f, allow_unicode=True)

    def filter_new(self, papers: list[Paper]) -> list[Paper]:
        """未通知の論文のみをフィルタリングし、通知済みとして記録する。"""
        new_papers = [p for p in papers if p.unique_id not in self._seen_ids]

        if new_papers:
            for p in new_papers:
                self._seen_ids.add(p.unique_id)
            self._save()
            logger.info("新規論文 %d件を検出（既読 %d件）", len(new_papers), len(self._seen_ids))

        return new_papers
