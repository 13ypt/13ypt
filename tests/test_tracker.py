"""既読追跡のテスト"""

import tempfile
from pathlib import Path

from egypt_paper_notifier.models import Paper
from egypt_paper_notifier.tracker import SeenTracker


def _make_paper(title: str, url: str, doi: str | None = None) -> Paper:
    return Paper(
        title=title, authors=["Author"], abstract="Abstract",
        url=url, source="test", doi=doi,
    )


def test_filter_new_papers():
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker = SeenTracker(Path(tmpdir) / "seen.yaml")

        papers = [
            _make_paper("Paper 1", "https://example.com/1", "10.1234/1"),
            _make_paper("Paper 2", "https://example.com/2", "10.1234/2"),
        ]

        # 初回はすべて新規
        new = tracker.filter_new(papers)
        assert len(new) == 2

        # 2回目は既読
        new = tracker.filter_new(papers)
        assert len(new) == 0


def test_filter_mixed_new_and_seen():
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker = SeenTracker(Path(tmpdir) / "seen.yaml")

        papers1 = [_make_paper("Paper 1", "https://example.com/1")]
        tracker.filter_new(papers1)

        papers2 = [
            _make_paper("Paper 1", "https://example.com/1"),
            _make_paper("Paper 3", "https://example.com/3"),
        ]
        new = tracker.filter_new(papers2)
        assert len(new) == 1
        assert new[0].title == "Paper 3"


def test_persistence():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "seen.yaml"

        tracker1 = SeenTracker(path)
        tracker1.filter_new([_make_paper("P1", "https://example.com/1")])

        # 新しいインスタンスで読み込み
        tracker2 = SeenTracker(path)
        new = tracker2.filter_new([_make_paper("P1", "https://example.com/1")])
        assert len(new) == 0
