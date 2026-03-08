#!/usr/bin/env python3
"""
Main entry point for the Egypt Animal Cult Paper Collector.
古代エジプト動物崇拝 論文自動収集アプリ

Usage:
  # Run once (collect papers from the last 7 days):
  python -m paper_collector.run

  # Specify how many days back to search:
  python -m paper_collector.run --days 30

  # Run in scheduled mode (repeats every N hours):
  python -m paper_collector.run --schedule 24

  # Output as JSON:
  python -m paper_collector.run --format json

  # Save report to file:
  python -m paper_collector.run --save
"""

import argparse
import logging
import os
import sys
import time

from .collectors import collect_all
from .database import PaperDatabase
from .reporter import generate_text_report, generate_json_report
from . import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def run_collection(days_back, db, output_format="text", save=False):
    """Run a single collection cycle."""
    logger.info("Starting paper collection (last %d days)...", days_back)

    papers = collect_all(days_back)
    new_count = 0
    new_papers = []

    for paper in papers:
        if db.add_paper(paper):
            new_count += 1
            new_papers.append(paper)

    logger.info(
        "Collection complete: %d papers found, %d new (total in DB: %d)",
        len(papers),
        new_count,
        db.get_paper_count(),
    )

    if new_papers:
        output_dir = os.path.join(
            os.path.dirname(os.path.abspath(db.db_path)), config.OUTPUT_DIR
        ) if save else None

        if output_format == "json":
            result = generate_json_report(new_papers, output_dir)
        else:
            result = generate_text_report(new_papers, output_dir)

        if save and isinstance(result, str) and os.path.isfile(result):
            logger.info("Report saved to: %s", result)
        else:
            print(result)
    else:
        print("No new papers found.")

    return new_count


def main():
    parser = argparse.ArgumentParser(
        description="古代エジプト動物崇拝 論文自動収集アプリ / Egypt Animal Cult Paper Collector"
    )
    parser.add_argument(
        "--days", type=int, default=config.DEFAULT_DAYS_BACK,
        help=f"How many days back to search (default: {config.DEFAULT_DAYS_BACK})"
    )
    parser.add_argument(
        "--schedule", type=float, default=None,
        help="Run repeatedly every N hours (e.g. 24 for daily)"
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--save", action="store_true",
        help="Save report to file instead of printing"
    )
    parser.add_argument(
        "--db", default=config.DB_FILE,
        help=f"Database file path (default: {config.DB_FILE})"
    )

    args = parser.parse_args()
    db = PaperDatabase(args.db)

    if args.schedule:
        logger.info("Scheduled mode: running every %.1f hours", args.schedule)
        interval_seconds = args.schedule * 3600
        while True:
            try:
                run_collection(args.days, db, args.format, args.save)
            except KeyboardInterrupt:
                logger.info("Stopped by user.")
                break
            except Exception:
                logger.exception("Error during collection cycle")
            logger.info("Next run in %.1f hours...", args.schedule)
            time.sleep(interval_seconds)
    else:
        run_collection(args.days, db, args.format, args.save)


if __name__ == "__main__":
    main()
