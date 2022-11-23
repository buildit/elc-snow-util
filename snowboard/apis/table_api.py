import time
from typing import Optional, List

import pandas as pd
from ..client import ApiClient, Prototype, AbstractAPI
from ..tables import SnowTable, SnowTableData


class TableApi(AbstractAPI):
    def __init__(self, client: ApiClient, table: SnowTable | SnowTableData):
        prototype = Prototype(namespace="now", path="table", version="v2")
        super().__init__(client, prototype)
        if isinstance(table, SnowTable):
            table = table.data
        if not isinstance(table, SnowTableData):
            raise TypeError("must be SnowTable enum member or SnowTableData")
        self.table = table

    def get_record(
        self,
        sys_id: str,
        display_value: Optional[bool] = None,
        links: bool = False,
        fields: Optional[List[str]] = None,
    ):
        params = {
            "sysparm_exclude_reference_link": not links,
        }
        if display_value is not None:
            params["sysparm_display_value"] = display_value
        if fields is None:
            fields = self.table.default_fields
        if fields and len(fields) > 0:
            params["sysparm_fields"] = ",".join(fields)  # type: ignore
        rel_uri = self.get_rel_uri(self.table.name, sys_id)
        return self.client.get(rel_uri, params)

    def update_record(
        self,
        sys_id: str,
        body: dict,
        display_value: Optional[bool] = None,
        links: bool = False,
        fields: Optional[List[str]] = None,
    ):
        params = {
            "sysparm_exclude_reference_link": not links,
        }
        if display_value is not None:
            params["sysparm_display_value"] = display_value
        if fields is None:
            fields = self.table.default_fields
        if fields and len(fields) > 0:
            params["sysparm_fields"] = ",".join(fields)  # type: ignore
        rel_uri = self.get_rel_uri(self.table.name, sys_id)
        return self.client.put(rel_uri, body, params)

    def get_records(
        self,
        query: Optional[str] = None,
        display_value: Optional[bool] = None,
        links: bool = False,
        pagination: bool = False,
        fields: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0,
    ):
        params = {
            "sysparm_exclude_reference_link": not links,
            "sysparm_suppress_pagination_header": not pagination,
            "sysparm_limit": limit,
            "sysparm_offset": offset,
        }
        if query is not None:
            params["sysparm_query"] = query
        if display_value is not None:
            params["sysparm_display_value"] = display_value
        if fields is None:
            fields = self.table.default_fields
        if fields and len(fields) > 0:
            params["sysparm_fields"] = ",".join(fields)
        rel_uri = self.get_rel_uri(self.table.name)
        return self.client.get(rel_uri, params)

    def yield_records(
        self,
        query: Optional[str] = None,
        display_value: Optional[bool] = None,
        links: bool = False,
        fields: Optional[List[str]] = None,
    ):
        limit = 100
        offset = 0
        r = self.get_records(
            query=query,
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
                query=query,
                display_value=display_value,
                links=links,
                fields=fields,
                limit=limit,
                offset=offset,
            )
            r.raise_for_status()

    def get_dataframe(
        self,
        query: Optional[str] = None,
        links: bool = False,
        fields: Optional[List[str]] = None,
    ):
        rows = list(
            self.yield_records(
                query=query, display_value=False, links=links, fields=fields
            )
        )
        for row in rows:
            if "active" in row:
                row["active"] = True if row["active"] == "true" else False
            if "order" in row:
                row["order"] = int(row["order"]) if row["order"] else None

            if self.table.field_mapping is not None:
                for old_name, new_name in self.table.field_mapping.items():
                    if old_name in row:
                        row[new_name] = row.pop(old_name)
        df = pd.DataFrame(rows)  # noqa:
        return df.set_index("sys_id")
