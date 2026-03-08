"""設定モジュールのテスト"""

import tempfile
from pathlib import Path

from egypt_paper_notifier.config import Config, load_config, save_default_config


def test_default_config():
    config = Config()
    assert len(config.keywords) > 0
    assert config.check_interval_hours == 24
    assert config.notification.desktop is True
    assert config.notification.email.enabled is False


def test_load_nonexistent_config():
    config = load_config("/nonexistent/path/config.yaml")
    assert isinstance(config, Config)
    assert len(config.keywords) > 0


def test_save_and_load_config():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "config.yaml"
        save_default_config(path)
        assert path.exists()

        config = load_config(path)
        assert len(config.keywords) > 0
        assert config.sources["arxiv"] is True
