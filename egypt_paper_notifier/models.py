"""論文データモデル"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Paper:
    title: str
    authors: list[str]
    abstract: str
    url: str
    source: str
    published_date: datetime | None = None
    doi: str | None = None

    @property
    def unique_id(self) -> str:
        """論文を一意に識別するID（DOIまたはURL）"""
        return self.doi if self.doi else self.url

    def summary(self, max_abstract_len: int = 200) -> str:
        """通知用の要約テキストを生成する。"""
        abstract_short = self.abstract[:max_abstract_len]
        if len(self.abstract) > max_abstract_len:
            abstract_short += "..."

        authors_str = ", ".join(self.authors[:3])
        if len(self.authors) > 3:
            authors_str += f" 他{len(self.authors) - 3}名"

        date_str = self.published_date.strftime("%Y-%m-%d") if self.published_date else "不明"

        return (
            f"タイトル: {self.title}\n"
            f"著者: {authors_str}\n"
            f"出典: {self.source} ({date_str})\n"
            f"概要: {abstract_short}\n"
            f"URL: {self.url}"
        )
