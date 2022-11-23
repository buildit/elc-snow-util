import pytest
from pydantic import AnyHttpUrl
from snowboard.config import Configuration


@pytest.fixture
def test_config():
    return Configuration(
        endpoint="https://fake.service-now.com/api",  # type: ignore
        username="carlsagan",
        password="stars",
        taxonomy="StarClassification",
    )
