"""デスクトップ通知モジュール"""

import logging

from egypt_paper_notifier.models import Paper

logger = logging.getLogger(__name__)


def notify(papers: list[Paper]) -> None:
    """デスクトップ通知を送信する。"""
    if not papers:
        return

    try:
        from plyer import notification as plyer_notification
    except ImportError:
        logger.warning("plyer がインストールされていません。pip install plyer を実行してください。")
        return

    if len(papers) == 1:
        paper = papers[0]
        title = f"新論文: {paper.title[:60]}"
        message = f"著者: {', '.join(paper.authors[:2])}\n出典: {paper.source}\n{paper.url}"
    else:
        title = f"古代エジプト動物崇拝: 新論文 {len(papers)}件"
        message = "\n".join(f"- {p.title[:50]}" for p in papers[:5])
        if len(papers) > 5:
            message += f"\n...他 {len(papers) - 5}件"

    try:
        plyer_notification.notify(
            title=title,
            message=message[:256],
            app_name="Egypt Paper Notifier",
            timeout=10,
        )
        logger.info("デスクトップ通知を送信しました (%d件)", len(papers))
    except Exception as e:
        logger.error("デスクトップ通知の送信に失敗: %s", e)
