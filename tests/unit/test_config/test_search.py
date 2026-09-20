import pytest


class TestSearch:
    # region SEARCH_PER_LIMIT
    @pytest.mark.parametrize(
        "v,exp",
        [
            ("0", 3),
            ("1", 3),
            ("5", 5),
            ("-10", 3),
        ],
    )
    def test_tracks_per_limit(self, monkeypatch, v, exp):
        monkeypatch.setenv("SEARCH_PER_LIMIT", v)
        from config import SEARCH_PER_LIMIT

        assert SEARCH_PER_LIMIT is not None
        assert SEARCH_PER_LIMIT == exp

    def test_tracks_per_limit_raises(self, monkeypatch):
        monkeypatch.setenv("SEARCH_PER_LIMIT", "str")
        with pytest.raises(ValueError):
            from config import SEARCH_PER_LIMIT  # noqa: F401

    # endregion

    # region SEARCH_COOLDOWN_SECS
    @pytest.mark.parametrize(
        "v,exp",
        [
            ("0", 20),
            ("1", 20),
            ("50", 50),
            ("-10", 20),
        ],
    )
    def test_query_download_limit(self, monkeypatch, v, exp):
        monkeypatch.setenv("SEARCH_COOLDOWN_SECS", v)
        from config import SEARCH_COOLDOWN_SECS

        assert SEARCH_COOLDOWN_SECS is not None
        assert SEARCH_COOLDOWN_SECS == exp

    def test_query_download_limit_raises(self, monkeypatch):
        monkeypatch.setenv("SEARCH_COOLDOWN_SECS", "f")
        with pytest.raises(ValueError):
            from config import SEARCH_COOLDOWN_SECS  # noqa: F401

    # endregion
