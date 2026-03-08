"""設定管理モジュール"""

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

DEFAULT_CONFIG_PATH = Path.home() / ".egypt_paper_notifier" / "config.yaml"
DEFAULT_SEEN_PATH = Path.home() / ".egypt_paper_notifier" / "seen_papers.yaml"

# 古代エジプトの動物崇拝に関連する検索キーワード
DEFAULT_KEYWORDS = [
    "ancient Egypt animal worship",
    "ancient Egypt animal cult",
    "Egyptian animal mummy",
    "Egyptian sacred animals",
    "ancient Egypt zoology religion",
    "Egyptian Apis bull",
    "Egyptian cat goddess Bastet",
    "Egyptian ibis Thoth",
    "Egyptian crocodile Sobek",
    "Egyptian falcon Horus",
    "Egyptian scarab beetle",
    "ancient Egypt theriomorphic",
    "古代エジプト 動物崇拝",
    "古代エジプト 動物ミイラ",
]


@dataclass
class EmailConfig:
    enabled: bool = False
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    username: str = ""
    password: str = ""
    to_address: str = ""


@dataclass
class NotificationConfig:
    desktop: bool = True
    email: EmailConfig = field(default_factory=EmailConfig)


@dataclass
class Config:
    keywords: list[str] = field(default_factory=lambda: list(DEFAULT_KEYWORDS))
    check_interval_hours: int = 24
    notification: NotificationConfig = field(default_factory=NotificationConfig)
    seen_papers_path: str = str(DEFAULT_SEEN_PATH)
    sources: dict[str, bool] = field(
        default_factory=lambda: {
            "arxiv": True,
            "crossref": True,
            "pubmed": True,
        }
    )


def load_config(path: str | Path | None = None) -> Config:
    """YAMLファイルから設定を読み込む。ファイルがなければデフォルト設定を返す。"""
    config_path = Path(path) if path else DEFAULT_CONFIG_PATH

    if not config_path.exists():
        return Config()

    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    email_data = data.get("notification", {}).get("email", {})
    email_config = EmailConfig(**email_data) if email_data else EmailConfig()

    notif_data = data.get("notification", {})
    notification = NotificationConfig(
        desktop=notif_data.get("desktop", True),
        email=email_config,
    )

    return Config(
        keywords=data.get("keywords", list(DEFAULT_KEYWORDS)),
        check_interval_hours=data.get("check_interval_hours", 24),
        notification=notification,
        seen_papers_path=data.get("seen_papers_path", str(DEFAULT_SEEN_PATH)),
        sources=data.get("sources", {"arxiv": True, "crossref": True, "pubmed": True}),
    )


def save_default_config(path: str | Path | None = None) -> Path:
    """デフォルト設定ファイルを生成する。"""
    config_path = Path(path) if path else DEFAULT_CONFIG_PATH
    config_path.parent.mkdir(parents=True, exist_ok=True)

    default = {
        "keywords": list(DEFAULT_KEYWORDS),
        "check_interval_hours": 24,
        "sources": {"arxiv": True, "crossref": True, "pubmed": True},
        "notification": {
            "desktop": True,
            "email": {
                "enabled": False,
                "smtp_host": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "to_address": "",
            },
        },
    }

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(default, f, allow_unicode=True, default_flow_style=False)

    return config_path
