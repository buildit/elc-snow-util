from pathlib import Path
from textwrap import dedent

import pytest

from snowboard.config import Configuration


def test_config_init():
    config = Configuration(
        endpoint="https://dev27782.service-now.com/api",  # type: ignore
        username="admin1",
        password="admin$pwd",
        taxonomy="Employee",
    )
    assert config.endpoint == "https://dev27782.service-now.com/api"
    assert config.endpoint.scheme == "https"
    assert config.endpoint.host == "dev27782.service-now.com"
    assert config.endpoint.path == "/api"
    assert config.username == "admin1"
    assert config.password == "admin$pwd"
    assert config.taxonomy == "Employee"


def test_config_default_path():
    path = Configuration.get_default_path()
    assert isinstance(path, Path)


def test_config_load_file_not_found(tmp_path):
    path = tmp_path / "snowman.conf"
    with pytest.raises(FileNotFoundError):
        Configuration.load(path)


def test_config_load_ok(tmp_path):
    path = tmp_path / "snowman.conf"
    path.write_text(
        dedent(
            """
        endpoint: https://skdjksjjs.example.service-now.com/api/
        username: admin
        password: admin
        taxonomy: Production
    """
        )
    )
    config = Configuration.load(path)
    assert config.username == "admin"
    assert config.password == "admin"
    assert config.endpoint == "https://skdjksjjs.example.service-now.com/api"
    assert config.taxonomy == "Production"
