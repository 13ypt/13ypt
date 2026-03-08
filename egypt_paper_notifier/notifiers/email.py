"""メール通知モジュール"""

import logging
import smtplib
from email.mime.text import MIMEText

from egypt_paper_notifier.config import EmailConfig
from egypt_paper_notifier.models import Paper

logger = logging.getLogger(__name__)


def notify(papers: list[Paper], config: EmailConfig) -> None:
    """メール通知を送信する。"""
    if not papers:
        return

    if not config.enabled:
        return

    if not config.username or not config.password or not config.to_address:
        logger.warning("メール設定が不完全です。config.yamlを確認してください。")
        return

    subject = f"【論文通知】古代エジプト動物崇拝 - 新規 {len(papers)}件"

    body_parts = [
        "古代エジプトの動物崇拝に関する新しい論文が見つかりました。\n",
        f"検出数: {len(papers)}件\n",
        "=" * 60,
    ]

    for i, paper in enumerate(papers, 1):
        body_parts.append(f"\n[{i}] {paper.summary()}")
        body_parts.append("-" * 40)

    body_parts.append(
        "\n---\nこのメールは Egypt Paper Notifier により自動送信されました。"
    )

    body = "\n".join(body_parts)

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = config.username
    msg["To"] = config.to_address

    try:
        with smtplib.SMTP(config.smtp_host, config.smtp_port) as server:
            server.starttls()
            server.login(config.username, config.password)
            server.send_message(msg)
        logger.info("メール通知を送信しました (%d件) → %s", len(papers), config.to_address)
    except smtplib.SMTPException as e:
        logger.error("メール送信に失敗: %s", e)
