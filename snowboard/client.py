import json
from typing import Optional, Dict

import requests
from progress import Infinite
from pydantic import BaseModel

from .config import Configuration


class ApiClient:
    def __init__(self, config: Configuration):
        self.config = config
        self.session = requests.Session()
        self.accept = "application/json"
        self._progress = None

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, progress: Infinite | None):
        self._progress = progress

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
        if self._progress:
            self._progress.next()
        return self.session.get(
            url, params=params, headers=headers, auth=self.auth, verify=False
        )

    def put(
        self,
        path: str,
        body: Dict[str, object],
        params: Optional[dict] = None,
        accept: Optional[str] = None,
    ):
        url = self.endpoint + path
        if accept is None:
            accept = self.accept
        headers = {"Accept": accept, "Content-Type": "application/json"}
        data = json.dumps(body)
        if self._progress:
            self._progress.next()
        return self.session.put(
            url, params=params, headers=headers, auth=self.auth, verify=False, data=data
        )


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
    def __init__(self, client: ApiClient, prototype: Prototype):
        if not isinstance(client, ApiClient):
            raise TypeError("should be snowboard.client.ApiClient")
        if not isinstance(prototype, Prototype):
            raise TypeError("should be snowboard.client.Prototype")
        self.client = client
        self.prototype = prototype
        self.base_path = prototype.get_base_path()

    def get_rel_uri(self, *args):
        more_path = "/" + "/".join(args) if len(args) > 0 else ""
        return self.base_path + more_path
