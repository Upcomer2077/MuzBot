import sys

import pytest


@pytest.fixture(autouse=True)
def cleanup_config():
    sys.modules.pop("config", None)
    yield
    sys.modules.pop("config", None)
