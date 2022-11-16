from typing import Optional

import requests
from pydantic import BaseModel

from .config import SnowmanConfig


class SnowmanClient:
    def __init__(self, config: SnowmanConfig):
        self.config = config
        self.session = requests.Session()
        self.accept = "application/json"

    @property
    def endpoint(self):
        return self.config.endpoint

    @property
    def auth(self):
        return (
            self.config.username,
            self.config.password,
        )

    def get(
        self, path: str, params: Optional[dict] = None, accept: Optional[str] = None
    ):
        url = self.endpoint + path
        if accept is None:
            accept = self.accept
        headers = {"Accept": accept}
        return self.session.get(url, params=params, headers=headers, auth=self.auth)


class Prototype(BaseModel):
    namespace: str
    path: str
    version: Optional[str] = None

    def get_base_path(self):
        if self.version:
            return f"/{self.namespace}/{self.version}/{self.path}"
        else:
            return f"/{self.namespace}/{self.path}"


class AbstractAPI:
    def __init__(self, client: SnowmanClient, prototype: Prototype):
        self.client = client
        self.prototype = prototype
        self.base_path = prototype.get_base_path()

    def get_rel_uri(self, *args):
        more_path = "/" + "/".join(args) if len(args) > 0 else ""
        return self.base_path + more_path
