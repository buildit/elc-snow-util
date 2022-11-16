import requests
from snowman.client import SnowmanClient, Prototype, AbstractAPI


def test_make_client(test_config):
    client = SnowmanClient(test_config)
    assert client.endpoint == "https://fake.service-now.com/api"
    assert client.auth == ("carlsagan", "stars")
    assert client.accept == "application/json"
    assert isinstance(client.session, requests.Session)


def test_prototype_latest():
    prototype = Prototype(namespace="now", path="table/topic")
    assert prototype.get_base_path() == "/now/table/topic"


def test_prototype_v2():
    prototype = Prototype(namespace="now", path="table/topic", version="v2")
    assert prototype.get_base_path() == "/now/v2/table/topic"


def test_get_rel_uri(test_config):
    client = SnowmanClient(test_config)
    api = AbstractAPI(client, Prototype(namespace="now", path="table"))
    assert api.get_rel_uri() == "/now/table"


def test_get_rel_uri_with_args(test_config):
    client = SnowmanClient(test_config)
    api = AbstractAPI(client, Prototype(namespace="now", path="table"))
    assert api.get_rel_uri("topic", "again") == "/now/table/topic/again"
