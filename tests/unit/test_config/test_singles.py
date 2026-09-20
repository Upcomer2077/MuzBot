import pytest


class TestSingles:
    # region TRACKS_PER_LIMIT
    @pytest.mark.parametrize(
        "v,exp",
        [
            ("0", 5),
            ("1", 5),
            ("5", 5),
            ("15", 15),
            ("-10", 5),
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

    # endregion

    # region QUERY_DOWNLOAD_LIMIT_SECS
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

    # endregion
