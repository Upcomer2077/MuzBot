import pytest


class TestRequired:
    # ============ Required ===============
    def test_bot_token(self, monkeypatch):
        monkeypatch.setenv("BOT_TOKEN", "-137")
        from config import BOT_TOKEN

        assert BOT_TOKEN is not None
        assert type(BOT_TOKEN) is str
        assert BOT_TOKEN == "-137"

    def test_bot_token_raises(self, monkeypatch):
        monkeypatch.setattr("dotenv.load_dotenv", lambda *_: None)
        monkeypatch.delenv("BOT_TOKEN", raising=False)
        with pytest.raises(KeyError):
            from config import BOT_TOKEN  # noqa: F401

    def test_channel_id(self, monkeypatch):
        monkeypatch.setenv("CHANNEL_STORAGE_ID", "-137")
        from config import CHANNEL_STORAGE_ID

        assert CHANNEL_STORAGE_ID is not None
        assert type(CHANNEL_STORAGE_ID) is int
        assert CHANNEL_STORAGE_ID == -137

    def test_channel_id_raises(self, monkeypatch):
        monkeypatch.setattr("dotenv.load_dotenv", lambda *_: None)
        monkeypatch.delenv("CHANNEL_STORAGE_ID", raising=False)
        with pytest.raises(KeyError):
            from config import CHANNEL_STORAGE_ID  # noqa: F401

    def test_channel_id_raises2(self, monkeypatch):
        monkeypatch.setenv("CHANNEL_STORAGE_ID", "str")
        with pytest.raises(ValueError):
            from config import CHANNEL_STORAGE_ID  # noqa: F401
