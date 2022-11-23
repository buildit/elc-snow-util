from . import TableApi
from .tables import SnowTable, CATALOG_ITEM_LEAST_FIELDS, CATALOG_ITEM_CLASSES


class ELQueries:
    CONNECTED_CONTENT_QUERY = "topic.taxonomy.name={}"
    TOPIC_QUERY = "taxonomy.name={}"
    ACTIVE_TOPIC_QUERY = "taxonomy.name={}^active=true"


def get_items_dataframe(client, desired_fields=None):
    if desired_fields is None:
        desired_fields = CATALOG_ITEM_LEAST_FIELDS
    items_api = TableApi(client, SnowTable.CATALOG_ITEMS)
    items = items_api.get_dataframe()
    items.reset_index(inplace=True)
    items = items.loc[:, desired_fields]
    items = items.set_index("sys_id")
    return items


def get_connected_content_dataframe(client, fields=None):
    connected_content_api = TableApi(client, SnowTable.CONNECTED_CONTENT)
    return connected_content_api.get_dataframe(
        ELQueries.CONNECTED_CONTENT_QUERY, fields=fields
    )


def extend_items_with_menu_location(items_df, content_df):
    all_mask = content_df.topic_path.str.startswith("All /")
    all_menu_content = content_df[all_mask]
    home_menu_content = content_df[~all_mask]

    def all_menu_path(sys_id):
        df = all_menu_content[all_menu_content.catalog_item == sys_id]
        return "\r\n".join(
            sorted(topic_path.replace("All / ", "") for topic_path in df.topic_path)  # type: ignore
        )

    def home_menu_path(sys_id):
        df = home_menu_content[home_menu_content.catalog_item == sys_id]
        return "\r\n".join(sorted(df.topic_path))

    items_df.reset_index(inplace=True)
    items_df["all_menu_path"] = items_df.sys_id.apply(all_menu_path)
    items_df["home_menu_path"] = items_df.sys_id.apply(home_menu_path)


def add_missing_and_mismatch_columns(df):
    # menu is missing - it cannot be a mismatch
    missing_mask = (df.all_menu_path == "") & (df.home_menu_path == "")
    df["missing_menu"] = missing_mask.apply(lambda t: "Missing" if t else "")

    # mismatch
    mismatch_mask = ~missing_mask & (df.all_menu_path != df.home_menu_path)
    df["menu_mismatch"] = mismatch_mask.apply(lambda t: "Mismatch" if t else "")
    return df


def get_topics_dataframe(client, active=False):
    topics_api = TableApi(client, SnowTable.TOPICS)
    topics_df = topics_api.get_dataframe(ELQueries.TOPIC_QUERY)

    if active:
        topics_df = topics_df[topics_df.active]
        topics_df = topics_df.drop(columns=["active"])
    return topics_df


def extend_topics_dataframe(topics_df, content_df):
    # add leaf column
    topics_df.reset_index(inplace=True)
    parent_topics = set(topics_df.parent_topic)
    parent_topics.remove("")
    topics_df["leaf"] = ~topics_df.sys_id.isin(parent_topics)

    # add count of connected content
    catalog_item_count = content_df.groupby("topic").count().catalog_item
    catalog_item_count.index.names = ["sys_id"]
    topics_df.set_index("sys_id", inplace=True)
    topics_df["catalog_item_count"] = catalog_item_count

    return topics_df
