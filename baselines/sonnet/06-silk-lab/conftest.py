import pytest
from zeal import zeal_context


@pytest.fixture(autouse=True)
def use_zeal():
    with zeal_context():
        yield
