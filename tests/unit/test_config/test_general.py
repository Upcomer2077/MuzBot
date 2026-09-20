import os

import pytest


class TestGeneral:
    # region BACKUP_EVERY_N_DAYS
    @pytest.mark.parametrize(
        "v,exp",
        [
            ("0", 1),
            ("1", 1),
            ("50", 50),
            ("-10", 1),
        ],
    )
    def test_backup_interval(self, monkeypatch, v, exp):
        monkeypatch.setenv("BACKUP_EVERY_N_DAYS", v)
        from config import BACKUP_EVERY_N_DAYS

        assert BACKUP_EVERY_N_DAYS is not None
        assert type(BACKUP_EVERY_N_DAYS) is int
        assert BACKUP_EVERY_N_DAYS == exp

    def test_backup_interval_raises(self, monkeypatch):
        monkeypatch.setenv("BACKUP_EVERY_N_DAYS", "str")
        with pytest.raises((ValueError, TypeError)):
            from config import CHANNEL_STORAGE_ID  # noqa: F401

    def test_backup_interval_default(self, monkeypatch):
        monkeypatch.setattr("dotenv.load_dotenv", lambda *_: None)
        monkeypatch.delenv("BACKUP_EVERY_N_DAYS", raising=False)
        from config import BACKUP_EVERY_N_DAYS

        assert BACKUP_EVERY_N_DAYS == 2

    # endregion

    # region LOKI_URL
    def test_loki_url(self, monkeypatch):
        monkeypatch.setenv("LOKI_URL", "myEnv")
        from config import LOKI_URL

        assert LOKI_URL is not None
        assert LOKI_URL == "myEnv"
        assert type(LOKI_URL) is str

    def test_loki_url_is_none(self, monkeypatch):
        monkeypatch.setattr("dotenv.load_dotenv", lambda *_: None)
        monkeypatch.delenv("LOKI_URL", raising=False)
        from config import LOKI_URL

        assert LOKI_URL is None

    # endregion

    # region CPU_COUNT
    @pytest.mark.parametrize(
        "v,exp",
        [
            ("0", os.cpu_count() or 1),
            ("1", 1),
            ("50", 50),
            ("-10", os.cpu_count() or 1),
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

    # endregion

    # region DB_NAME
    @pytest.mark.parametrize("v,exp", [("", "db2"), ("2", "2")])
    def test_db_name(self, monkeypatch, v, exp):
        monkeypatch.setenv("DB_NAME", v)
        from config import DB_NAME

        assert DB_NAME is not None
        assert type(DB_NAME) is str
        assert DB_NAME == exp

    def test_db_name_none(self, monkeypatch):
        monkeypatch.setattr("dotenv.load_dotenv", lambda *_: None)
        monkeypatch.delenv("DB_NAME", raising=False)
        from config import DB_NAME

        assert DB_NAME == "db2"

    # endregion

    # region EXPERIMENTAL and DEBUG
    @pytest.mark.parametrize("env", ["EXPERIMENTAL", "DEBUG"])
    @pytest.mark.parametrize(
        "v,exp",
        [
            ("21", True),
            ("1", True),
            ("0", False),
            ("-1", True),
        ],
    )
    def test_experimental_debug(self, monkeypatch, v, exp, env):
        monkeypatch.setenv(env, v)
        import config

        var = getattr(config, env, None)

        assert var is not None
        assert type(var) is bool
        assert var == exp

    @pytest.mark.parametrize("env", ["EXPERIMENTAL", "DEBUG"])
    def test_experimental_debug_none(self, monkeypatch, env):
        monkeypatch.setattr("dotenv.load_dotenv", lambda *_: None)
        monkeypatch.delenv(env, raising=False)
        import config

        var = getattr(config, env, None)

        assert var is False

    @pytest.mark.parametrize("env", ["EXPERIMENTAL", "DEBUG"])
    @pytest.mark.parametrize(
        "v",
        [
            ("[]"),
            ("Fk"),
            ("1.43"),
            ("False"),
        ],
    )
    def test_experimental_debug_raises(self, monkeypatch, v, env):
        monkeypatch.setenv(env, v)
        with pytest.raises(ValueError):
            import config

            getattr(config, env, None)

    # endregion

    # region WORKER_CORES_COUNT
    @pytest.mark.parametrize(
        "v,exp", [("1", 1), ("5", 4), ("0", max(1, (os.cpu_count() or 1) - 1))]
    )
    def test_worker_cores(self, monkeypatch, v, exp):
        monkeypatch.setenv("CPU_COUNT", v)
        from config import WORKER_CORES_COUNT

        assert WORKER_CORES_COUNT == exp

    # ===============
    # region DATABASE_PATH
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

    # endregion

    # region CACHE_ROOT_DIR
    def test_CACHE_ROOT_DIR(self, monkeypatch):
        from config import CACHE_ROOT_DIR

        assert CACHE_ROOT_DIR is not None
        assert CACHE_ROOT_DIR == "./.cache"

    # endregion
