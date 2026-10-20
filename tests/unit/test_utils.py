import pytest

from helpers.get_hash_tags import get_hash_tags


@pytest.mark.parametrize(
    "v,expected",
    (
        ("lil peep", ["#lil_peep"]),
        ("lil & peep", ["#lil", "#peep"]),
        ("lil peep, eminem", ["#lil_peep", "#eminem"]),
        ("lil&_*/%$@.№:;!#^\"?()=+-'peep, e—-minem", ["#lil", "#__peep", "#e__minem"]),
    ),
)
def test_get_tags(v, expected):
    assert get_hash_tags(v) == expected
