import sys

from . import TableApi
from .tables import SnowTable, CATALOG_ITEM_LEAST_FIELDS, CATALOG_ITEM_CLASSES


class ELQueries:
    CONNECTED_CONTENT_QUERY = "topic.taxonomy.name={}"
    TOPIC_QUERY = "taxonomy.name={}"
    TAXONOMY_QUERY = "name={}"


def verify_taxonomy(client):
    query = ELQueries.TAXONOMY_QUERY.format(client.config.taxonomy)
    taxonomy_api = TableApi(client, SnowTable.TAXONOMY)
    r = taxonomy_api.get_records(query)
    r.raise_for_status()
    results = r.json()["result"]
    num_found = len(results)
    if num_found == 0:
        print(f"Taxonomy {client.config.taxonomy}: not found", file=sys.stderr)
        return False
    elif num_found > 1:
        print(f"Taxonomy {client.config.taxonomy}: too many found", file=sys.stderr)
        return False
    return True


def get_items_dataframe(client, active=False, desired_fields=None):
    # determine the fields we need
    if desired_fields is None:
        desired_fields = CATALOG_ITEM_LEAST_FIELDS

    items_api = TableApi(client, SnowTable.CATALOG_ITEMS)
    items = items_api.get_dataframe()
    items.reset_index(inplace=True)
    items = items.loc[:, desired_fields]
    items = items.set_index("sys_id")

    if active:
        items = items[items.active]
        items = items.drop(columns=["active"])
    return items


def get_connected_content_dataframe(client, fields=None, active=False):
    query = ELQueries.CONNECTED_CONTENT_QUERY.format(client.config.taxonomy)
    if active:
        query += "^topic.active=true"
    connected_content_api = TableApi(client, SnowTable.CONNECTED_CONTENT)
    return connected_content_api.get_dataframe(query, fields=fields)


def extend_items_with_menu_location(items_df, content_df):
    def menu_path(sys_id):
        df = content_df[content_df.catalog_item == sys_id]
        return "\r\n".join(sorted(df.topic_path))

    items_df.reset_index(inplace=True)
    items_df["topic_path"] = items_df.sys_id.apply(menu_path)


def get_topics_dataframe(client, active=False):
    topics_api = TableApi(client, SnowTable.TOPICS)

    query = ELQueries.TOPIC_QUERY.format(client.config.taxonomy)
    topics_df = topics_api.get_dataframe(query)

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
