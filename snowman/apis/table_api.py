from typing import Optional, List
from ..client import SnowmanClient, Prototype, AbstractAPI


class TableApi(AbstractAPI):
    def __init__(
        self, client: SnowmanClient, table_name: str, fields: Optional[List[str]]
    ):
        prototype = Prototype("now", f"table", "v2")
        super().__init__(client, prototype)
        self.table_name = table_name
        self.default_fields = fields

    def get_records(
        self,
        query: str,
        display_value: bool = False,
        exclude_links: bool = True,
        fields: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0,
    ):
        params = {
            "sysparm_query": query,
            "sysparm_display_value": display_value,
            "sysparm_exclude_reference_link": exclude_links,
            "sysparm_limit": limit,
            "sysparm_offset": offset,
        }
        if fields is None:
            fields = self.default_fields
        if fields and len(fields) > 0:
            params["sysparm_fields"] = ",".join(fields)
        rel_uri = self.get_rel_uri(self.table_name)
        return self.client.get(rel_uri, params)

    def yield_records(
        self,
        query: str,
        display_value: bool = False,
        exclude_links: bool = True,
        fields: Optional[List[str]] = None,
    ):
        limit = 100
        offset = 0
        r = self.get_records(
            query,
            display_value=display_value,
            exclude_links=exclude_links,
            fields=fields,
        )
        return r.json()
