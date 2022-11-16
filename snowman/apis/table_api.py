from typing import Optional, List

import pandas as pd

from ..client import SnowmanClient, Prototype, AbstractAPI


class TableApi(AbstractAPI):
    def __init__(
        self, client: SnowmanClient, table_name: str, fields: Optional[List[str]] = None
    ):
        prototype = Prototype(namespace="now", path="table", version="v2")
        super().__init__(client, prototype)
        self.table_name = table_name
        self.default_fields = fields

    def get_records(
        self,
        query: str,
        display_value: bool = False,
        links: bool = False,
        pagination: bool = False,
        fields: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0,
    ):
        params = {
            "sysparm_query": query,
            "sysparm_display_value": display_value,
            "sysparm_exclude_reference_link": not links,
            "sysparm_suppress_pagination_header": not pagination,
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
        links: bool = False,
        fields: Optional[List[str]] = None,
    ):
        limit = 100
        offset = 0
        r = self.get_records(
            query,
            display_value=display_value,
            links=links,
            fields=fields,
            limit=limit,
            offset=offset,
        )
        r.raise_for_status()
        total = int(r.headers["X-Total-Count"])

        while offset < total:
            rows = r.json()["result"]
            for row in rows:
                yield row
            offset += len(rows)

            r = self.get_records(
                query,
                display_value=display_value,
                links=links,
                fields=fields,
                limit=limit,
                offset=offset,
            )
            r.raise_for_status()

    def get_dataframe(
        self,
        query: str,
        display_value: bool = False,
        links: bool = False,
        fields: Optional[List[str]] = None,
    ):
        rows = list(
            self.yield_records(
                query=query, display_value=display_value, links=links, fields=fields
            )
        )
        for row in rows:
            if "active" in row:
                row["active"] = True if row["active"] == "true" else False
            if "order" in row:
                row["order"] = int(row["order"]) if row["order"] else None
        df = pd.DataFrame(rows)
        return df.set_index("sys_id")
