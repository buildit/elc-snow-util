from .config import SnowmanConfig

CATALOG_QUERY = "type!=bundle^sys_class_name!=sc_cat_item_guide^type!=package^sys_class_name!=sc_cat_item_content^published_refISEMPTY"

CATALOG_ITEMS_FIELDS = []

CONNECTED_CONTENT_FIELDS = []

TOPIC_QUERY = "taxonomy.name=ELC_Employee_Center"

TOPIC_FIELDS = [
    "parent_topic",
    "icon",
    "description",
    "sys_id",
    "sys_name",
    "banner_image",
    "order",
    "active",
    "topic_path",
    "name",
]


def command_config(opts):
    print("Not yet implemented")
    return 0


def command_catalog(config: SnowmanConfig, opts):
    print("not yet implemnented")
    return 0
