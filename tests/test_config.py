from pathlib import Path
from textwrap import dedent

import pytest

from snowman.config import SnowmanConfig


def test_config_init():
    config = SnowmanConfig(
        endpoint="https://dev27782.service-now.com/api",
        username="admin1",
        password="admin$pwd",
    )
    assert config.endpoint == "https://dev27782.service-now.com/api"
    assert config.endpoint.scheme == "https"
    assert config.endpoint.host == "dev27782.service-now.com"
    assert config.endpoint.path == "/api"
    assert config.username == "admin1"
    assert config.password == "admin$pwd"


def test_config_default_path():
    path = SnowmanConfig.get_default_path()
    assert isinstance(path, Path)


def test_config_load_file_not_found(tmp_path):
    path = tmp_path / "snowman.conf"
    with pytest.raises(FileNotFoundError):
        SnowmanConfig.load(path)


def test_config_load_ok(tmp_path):
    path = tmp_path / "snowman.conf"
    path.write_text(
        dedent(
            """
        endpoint: https://skdjksjjs.example.service-now.com/api/
        username: admin
        password: admin
    """
        )
    )
    config = SnowmanConfig.load(path)
    assert config.username == "admin"
    assert config.password == "admin"
    assert config.endpoint == "https://skdjksjjs.example.service-now.com/api"
