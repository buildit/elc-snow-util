from pathlib import Path
from textwrap import dedent

import pytest

from snowman.config import SnowmanConfig


def test_config_default_path():
    path = SnowmanConfig.get_default_path()
    assert isinstance(path, Path)


def test_config_path_no(tmp_path):
    path = tmp_path / "snowman.conf"
    with pytest.raises(FileNotFoundError):
        SnowmanConfig.load(path)


def test_config_all(tmp_path):
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
