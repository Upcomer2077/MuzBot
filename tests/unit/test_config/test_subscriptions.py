import pytest


class TestSubscriptions:
    # region SUBSCRIPTION_COOLDOWN_SECS
    @pytest.mark.parametrize(
        "v,exp",
        [
            ("0", 20),
            ("1", 20),
            ("50", 50),
            ("-10", 20),
        ],
    )
    def test_subs_limit(self, monkeypatch, v, exp):
        monkeypatch.setenv("SUBSCRIPTION_COOLDOWN_SECS", v)
        from config import SUBSCRIPTION_COOLDOWN_SECS

        assert SUBSCRIPTION_COOLDOWN_SECS is not None
        assert SUBSCRIPTION_COOLDOWN_SECS == exp

    def test_subs_raises(self, monkeypatch):
        monkeypatch.setenv("SUBSCRIPTION_COOLDOWN_SECS", "f")
        with pytest.raises(ValueError):
            from config import SUBSCRIPTION_COOLDOWN_SECS  # noqa: F401

    # endregion
    # region SUBSCRIPTIONS_PER_LIMIT
    @pytest.mark.parametrize(
        "v,exp",
        [
            ("0", 4),
            ("1", 4),
            ("5", 5),
            ("-10", 4),
        ],
    )
    def test_subs_per_limit(self, monkeypatch, v, exp):
        monkeypatch.setenv("SUBSCRIPTIONS_PER_LIMIT", v)
        from config import SUBSCRIPTIONS_PER_LIMIT

        assert SUBSCRIPTIONS_PER_LIMIT is not None
        assert SUBSCRIPTIONS_PER_LIMIT == exp

    def test_subs_per_limit_raises(self, monkeypatch):
        monkeypatch.setenv("SUBSCRIPTIONS_PER_LIMIT", "str")
        with pytest.raises(ValueError):
            from config import SUBSCRIPTIONS_PER_LIMIT  # noqa: F401

    # endregion
