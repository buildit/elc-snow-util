from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel


class SnowTableData(BaseModel):
    name: str
    default_fields: Optional[List[str]] = None
    field_mapping: Optional[Dict[str, str]] = None


class SnowTable(Enum):
    TOPICS = (
        "topic",
        [
            "parent_topic",
            "icon",
            "description",
            "sys_id",
            "sys_name",
            "order",
            "active",
            "topic_path",
            "name",
        ],
        None,
    )

    CONNECTED_CONTENT = (
        "m2m_connected_content",
        [
            "sys_id",
            "catalog_item",
            "catalog_item.sys_class_name",
            "topic",
            "topic.topic_path",
        ],
        {
            "catalog_item.sys_class_name": "sys_class_name",
            "topic.topic_path": "topic_path",
        },
    )

    # For some reason, querying fewer that all ciolumns of sc_cat_item produces errors
    CATALOG_ITEMS = ("sc_cat_item", None, None)

    def __init__(
        self,
        table_name: str,
        default_fields: Optional[List[str]] = None,
        field_mapping: Optional[Dict[str, str]] = None,
    ):
        self.sys_name = table_name
        self.data = SnowTableData(
            name=table_name, default_fields=default_fields, field_mapping=field_mapping
        )


CATALOG_ITEM_LEAST_FIELDS = [
    "sys_id",
    "sys_class_name",
    "name",
    "short_description",
    "active",
]

CATALOG_ITEM_CLASSES = {
    "sc_cat_item": "Catalog Item",
    "sc_cat_item_guide": "Order Guide",
    "sc_cat_item_content": "Content Item",
    "sc_cat_item_producer": "Record Producer",
}
