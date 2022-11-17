import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, HttpUrl
from yaml import safe_load


class Configuration(BaseModel):
    endpoint: HttpUrl
    username: str
    password: str

    @staticmethod
    def get_default_path() -> Path:
        if "USERPROFILE" in os.environ and "APPDATA" in os.environ:
            return Path(os.environ["APPDATA"]) / "snowman.ini"
        else:
            return Path(os.environ["HOME"]) / ".config" / "snowman.conf"

    @classmethod
    def load(cls, path: Optional[Path] = None):
        if path is None:
            path = cls.get_default_path()
        with path.open() as f:
            config = safe_load(f)
            if set(config.keys()) != {"endpoint", "username", "password"}:
                raise ValueError(
                    "configuration keys are endpoint, username, and password"
                )
            endpoint = config["endpoint"]
            if endpoint.endswith("/"):
                endpoint = endpoint[:-1]
            return cls(
                endpoint=endpoint,
                username=config["username"],
                password=config["password"],
            )
