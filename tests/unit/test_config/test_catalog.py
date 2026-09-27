import pytest


class TestCatalog:
    # region CATALOG_COOLDOWN_SECS
    @pytest.mark.parametrize(
        "v,exp",
        [
            ("0", 20),
            ("1", 20),
            ("50", 50),
            ("-10", 20),
        ],
    )
    def test_catalog_limit(self, monkeypatch, v, exp):
        monkeypatch.setenv("CATALOG_COOLDOWN_SECS", v)
        from config import CATALOG_COOLDOWN_SECS

        assert CATALOG_COOLDOWN_SECS is not None
        assert CATALOG_COOLDOWN_SECS == exp

    def test_catalog_limit_raises(self, monkeypatch):
        monkeypatch.setenv("CATALOG_COOLDOWN_SECS", "f")
        with pytest.raises(ValueError):
            from config import CATALOG_COOLDOWN_SECS  # noqa: F401

    # endregion

    # region CATALOG_PER_LIMIT
    @pytest.mark.parametrize(
        "v,exp",
        [
            ("0", 5),
            ("1", 5),
            ("8", 8),
            ("-10", 5),
        ],
    )
    def test_playlists_per_limit(self, monkeypatch, v, exp):
        monkeypatch.setenv("CATALOG_PER_LIMIT", v)
        from config import CATALOG_PER_LIMIT

        assert CATALOG_PER_LIMIT is not None
        assert CATALOG_PER_LIMIT == exp

    def test_playlists_per_limit_raises(self, monkeypatch):
        monkeypatch.setenv("CATALOG_PER_LIMIT", "str")
        with pytest.raises(ValueError):
            from config import CATALOG_PER_LIMIT  # noqa: F401

    # endregion
