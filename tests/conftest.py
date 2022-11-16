import pytest
from snowman.config import SnowmanConfig


@pytest.fixture
def test_config():
    return SnowmanConfig(
        endpoint="https://fake.service-now.com/api",
        username="carlsagan",
        password="stars",
    )
