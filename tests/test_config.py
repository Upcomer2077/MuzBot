import os
import sys

import pytest


@pytest.fixture(autouse=True)
def cleanup_config():
    sys.modules.pop("config", None)
    yield
    sys.modules.pop("config", None)


class TestConfig:
    def test_db_path(self, monkeypatch):
        monkeypatch.setenv("DB_NAME", "MyENV")
        from config import DATABASE_PATH

        assert DATABASE_PATH is not None
        assert type(DATABASE_PATH) is str
        assert DATABASE_PATH == f"{os.getcwd()}/data/{'MyENV'}.db"

    def test_db_path_default(self, monkeypatch):
        from config import DATABASE_PATH

        assert DATABASE_PATH is not None
        assert type(DATABASE_PATH) is str
        assert DATABASE_PATH == f"{os.getcwd()}/data/db2.db"

    def test_bot_token(self, monkeypatch):
        monkeypatch.setenv("BOT_TOKEN", "MyENV")
        from config import BOT_TOKEN

        assert BOT_TOKEN is not None
        assert type(BOT_TOKEN) is str
        assert BOT_TOKEN == "MyENV"

    @pytest.mark.parametrize(
        "v,exp",
        [
            ("0", 2),
            ("1", 2),
            ("5", 5),
            ("-10", 2),
        ],
    )
    def test_tracks_per_limit(self, monkeypatch, v, exp):
        monkeypatch.setenv("TRACKS_PER_LIMIT", v)
        from config import TRACKS_PER_LIMIT

        assert TRACKS_PER_LIMIT is not None
        assert TRACKS_PER_LIMIT == exp

    def test_tracks_per_limit_raises(self, monkeypatch):
        monkeypatch.setenv("TRACKS_PER_LIMIT", "str")
        with pytest.raises(ValueError):
            from config import TRACKS_PER_LIMIT  # noqa: F401

    @pytest.mark.parametrize(
        "v,exp",
        [
            ("0", 30),
            ("1", 30),
            ("50", 50),
            ("-10", 30),
        ],
    )
    def test_query_download_limit(self, monkeypatch, v, exp):
        monkeypatch.setenv("QUERY_DOWNLOAD_LIMIT_SECS", v)
        from config import QUERY_DOWNLOAD_LIMIT_SECS

        assert QUERY_DOWNLOAD_LIMIT_SECS is not None
        assert QUERY_DOWNLOAD_LIMIT_SECS == exp

    def test_query_download_limit_raises(self, monkeypatch):
        monkeypatch.setenv("QUERY_DOWNLOAD_LIMIT_SECS", "f")
        with pytest.raises(ValueError):
            from config import QUERY_DOWNLOAD_LIMIT_SECS  # noqa: F401

    def test_CACHE_ROOT_DIR(self, monkeypatch):
        from config import CACHE_ROOT_DIR

        assert CACHE_ROOT_DIR is not None
        assert CACHE_ROOT_DIR == "./.cache"

    @pytest.mark.parametrize(
        "v,exp",
        [
            ("0", os.cpu_count() or 1),
            ("1", 1),
            ("50", 50),
            ("-10", -10),
        ],
    )
    def test_cpu_count(self, monkeypatch, v, exp):
        monkeypatch.setenv("CPU_COUNT", v)
        from config import CPU_COUNT

        assert CPU_COUNT is not None
        assert CPU_COUNT == exp

    def test_cpu_count_raises(self, monkeypatch):
        monkeypatch.setenv("CPU_COUNT", "f")
        with pytest.raises(ValueError):
            from config import CPU_COUNT  # noqa: F401

    def test_loki_url(self, monkeypatch):
        monkeypatch.setenv("LOKI_URL", "myEnv")
        from config import LOKI_URL

        assert LOKI_URL is not None
        assert LOKI_URL == "myEnv"
        assert type(LOKI_URL) is str
