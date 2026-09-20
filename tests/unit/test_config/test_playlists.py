import pytest


class TestPlaylists:
    # region PLAYLIST_DOWNLOAD_COOLDOWN_SECS
    @pytest.mark.parametrize(
        "v,exp",
        [
            ("0", 20),
            ("1", 20),
            ("50", 50),
            ("-10", 20),
        ],
    )
    def test_playlist_download_limit(self, monkeypatch, v, exp):
        monkeypatch.setenv("PLAYLIST_DOWNLOAD_COOLDOWN_SECS", v)
        from config import PLAYLIST_DOWNLOAD_COOLDOWN_SECS

        assert PLAYLIST_DOWNLOAD_COOLDOWN_SECS is not None
        assert PLAYLIST_DOWNLOAD_COOLDOWN_SECS == exp

    def test_playlist_download_limit_raises(self, monkeypatch):
        monkeypatch.setenv("PLAYLIST_DOWNLOAD_COOLDOWN_SECS", "f")
        with pytest.raises(ValueError):
            from config import PLAYLIST_DOWNLOAD_COOLDOWN_SECS  # noqa: F401

    # endregion

    # region PLAYLISTS_LIMIT
    @pytest.mark.parametrize(
        "v,exp",
        [
            ("0", 1),
            ("1", 1),
            ("5", 5),
            ("-10", 1),
        ],
    )
    def test_playlists_per_limit(self, monkeypatch, v, exp):
        monkeypatch.setenv("PLAYLISTS_LIMIT", v)
        from config import PLAYLISTS_LIMIT

        assert PLAYLISTS_LIMIT is not None
        assert PLAYLISTS_LIMIT == exp

    def test_playlists_per_limit_raises(self, monkeypatch):
        monkeypatch.setenv("PLAYLISTS_LIMIT", "str")
        with pytest.raises(ValueError):
            from config import PLAYLISTS_LIMIT  # noqa: F401

    # endregion

    # region PLAYLIST_MAX_TRACKS
    @pytest.mark.parametrize(
        "v,exp",
        [
            ("0", 0),
            ("1", 1),
            ("50", 50),
            ("-10", 0),
        ],
    )
    def test_playlist_playlist_max_tracks(self, monkeypatch, v, exp):
        monkeypatch.setenv("PLAYLIST_MAX_TRACKS", v)
        from config import PLAYLIST_MAX_TRACKS

        assert PLAYLIST_MAX_TRACKS is not None
        assert PLAYLIST_MAX_TRACKS == exp

    def test_playlist_playlist_max_tracks_raises(self, monkeypatch):
        monkeypatch.setenv("PLAYLIST_MAX_TRACKS", "f")
        with pytest.raises(ValueError):
            from config import PLAYLIST_MAX_TRACKS  # noqa: F401

    # endregion
