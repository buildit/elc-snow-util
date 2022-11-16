from urllib.parse import quote

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

    def get(self, path: str, params: dict):
        url = self.endpoint + path
        return self.session.get(url, params=params, auth=self.auth)


class Prototype(BaseModel):
    namespace: str
    path: str
    version: str

    def get_base_path(self):
        if self.version:
            return f"/api/{self,namespace}/{self.version}/{self.path}"
        else:
            return f"/api/{self.namesapce}/{self.path}"


class AbstractAPI:
    def __init__(self, client: SnowmanClient, prototype: Prototype):
        self.client = client
        self.prototype = prototype
        self.base_path = prototype.get_base_path()

    def get_rel_uri(self, *args):
        return self.base_path + "/".join(args)
