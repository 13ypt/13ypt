"""
SQLite database for storing collected papers.
収集した論文を保存するデータベースモジュール
"""

import sqlite3
import os
from datetime import datetime


class PaperDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS papers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    authors TEXT,
                    abstract TEXT,
                    doi TEXT UNIQUE,
                    url TEXT,
                    published_date TEXT,
                    source TEXT,
                    query_matched TEXT,
                    collected_at TEXT NOT NULL,
                    notified INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_doi ON papers(doi)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_collected_at ON papers(collected_at)
            """)

    def paper_exists(self, doi):
        """Check if a paper with this DOI already exists."""
        if not doi:
            return False
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT 1 FROM papers WHERE doi = ?", (doi,)
            ).fetchone()
            return row is not None

    def add_paper(self, paper):
        """
        Add a paper to the database. Returns True if newly added, False if duplicate.
        paper: dict with keys title, authors, abstract, doi, url,
               published_date, source, query_matched
        """
        if paper.get("doi") and self.paper_exists(paper["doi"]):
            return False

        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute(
                    """INSERT INTO papers
                       (title, authors, abstract, doi, url,
                        published_date, source, query_matched, collected_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        paper.get("title", ""),
                        paper.get("authors", ""),
                        paper.get("abstract", ""),
                        paper.get("doi"),
                        paper.get("url", ""),
                        paper.get("published_date", ""),
                        paper.get("source", ""),
                        paper.get("query_matched", ""),
                        datetime.utcnow().isoformat(),
                    ),
                )
                return True
            except sqlite3.IntegrityError:
                return False

    def get_new_papers(self, since=None):
        """Get papers collected since a given datetime string."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if since:
                rows = conn.execute(
                    "SELECT * FROM papers WHERE collected_at >= ? ORDER BY collected_at DESC",
                    (since,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM papers ORDER BY collected_at DESC"
                ).fetchall()
            return [dict(r) for r in rows]

    def get_paper_count(self):
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0]

    def mark_notified(self, paper_ids):
        """Mark papers as notified."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                "UPDATE papers SET notified = 1 WHERE id = ?",
                [(pid,) for pid in paper_ids],
            )
