"""CLIエントリーポイント"""

import argparse
import logging
import sys
import time

import schedule

from egypt_paper_notifier.config import Config, load_config, save_default_config
from egypt_paper_notifier.notifiers import desktop, email
from egypt_paper_notifier.searcher import search_all_sources
from egypt_paper_notifier.tracker import SeenTracker

logger = logging.getLogger("egypt_paper_notifier")


def run_check(config: Config, tracker: SeenTracker) -> None:
    """論文検索と通知を1回実行する。"""
    logger.info("論文チェックを開始します...")

    papers = search_all_sources(config)
    new_papers = tracker.filter_new(papers)

    if not new_papers:
        logger.info("新しい論文はありません。")
        return

    logger.info("新規論文 %d件を検出しました！", len(new_papers))

    for paper in new_papers:
        print(f"\n{'=' * 60}")
        print(paper.summary())

    if config.notification.desktop:
        desktop.notify(new_papers)

    if config.notification.email.enabled:
        email.notify(new_papers, config.notification.email)


def cmd_check(args: argparse.Namespace) -> None:
    """単発チェックコマンド"""
    config = load_config(args.config)
    tracker = SeenTracker(config.seen_papers_path)
    run_check(config, tracker)


def cmd_watch(args: argparse.Namespace) -> None:
    """定期監視コマンド"""
    config = load_config(args.config)
    tracker = SeenTracker(config.seen_papers_path)

    interval = config.check_interval_hours
    logger.info("定期監視を開始します（間隔: %d時間）", interval)

    # 起動時に1回実行
    run_check(config, tracker)

    schedule.every(interval).hours.do(run_check, config=config, tracker=tracker)

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("監視を停止しました。")


def cmd_init(args: argparse.Namespace) -> None:
    """設定ファイル初期化コマンド"""
    path = save_default_config(args.config)
    print(f"設定ファイルを作成しました: {path}")
    print("エディタで開いてメール設定等をカスタマイズしてください。")


def main() -> None:
    """メインエントリーポイント"""
    parser = argparse.ArgumentParser(
        prog="egypt-notify",
        description="古代エジプトの動物崇拝に関する論文通知アプリ",
    )
    parser.add_argument(
        "-c", "--config",
        help="設定ファイルのパス",
        default=None,
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="詳細ログを表示",
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("check", help="論文を1回チェックする")
    subparsers.add_parser("watch", help="定期的に論文をチェックする")
    subparsers.add_parser("init", help="設定ファイルを初期化する")

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    commands = {
        "check": cmd_check,
        "watch": cmd_watch,
        "init": cmd_init,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
