"""モデルのテスト"""

from datetime import datetime

from egypt_paper_notifier.models import Paper


def test_paper_unique_id_with_doi():
    paper = Paper(
        title="Test", authors=["A"], abstract="...",
        url="https://example.com", source="test", doi="10.1234/test",
    )
    assert paper.unique_id == "10.1234/test"


def test_paper_unique_id_without_doi():
    paper = Paper(
        title="Test", authors=["A"], abstract="...",
        url="https://example.com/paper", source="test",
    )
    assert paper.unique_id == "https://example.com/paper"


def test_paper_summary():
    paper = Paper(
        title="Animal Worship in Ancient Egypt",
        authors=["Alice Smith", "Bob Jones", "Carol White", "Dave Brown"],
        abstract="This paper examines the role of animal cults in ancient Egyptian religion.",
        url="https://example.com/paper",
        source="arXiv",
        published_date=datetime(2025, 6, 15),
    )
    summary = paper.summary()
    assert "Animal Worship in Ancient Egypt" in summary
    assert "Alice Smith" in summary
    assert "他1名" in summary
    assert "arXiv" in summary
    assert "2025-06-15" in summary


def test_paper_summary_truncation():
    paper = Paper(
        title="Test",
        authors=["A"],
        abstract="x" * 300,
        url="https://example.com",
        source="test",
    )
    summary = paper.summary(max_abstract_len=100)
    assert "..." in summary
