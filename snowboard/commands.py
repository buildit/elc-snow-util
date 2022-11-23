import sys
import time
import unicodedata
from argparse import Namespace
from enum import Enum, unique

import magic
import requests
from progress.bar import Bar
from progress.spinner import Spinner

from . import Configuration, ApiClient
from .apis.table_api import TableApi
from .tables import CATALOG_ITEM_CLASSES, SnowTable
from .elc_utils import (
    ELQueries,
    get_items_dataframe,
    get_connected_content_dataframe,
    extend_items_with_menu_location,
    add_missing_and_mismatch_columns,
    get_topics_dataframe,
    extend_topics_dataframe,
)


@unique
class FileFormat(Enum):
    CSV = "csv"
    XLSX = "xlsx"


def command_config(opts: Namespace):
    print("Not yet implemented")
    return 0


def command_topics(config: Configuration, opts: Namespace):

    # what is the output format
    if opts.output.endswith(".csv"):
        output_format = FileFormat.CSV
    elif opts.output.endswith(".xlsx"):
        output_format = FileFormat.XLSX
    else:
        raise ValueError("only supports CSV and XLSX extensions")

    # create the client
    client = ApiClient(config)
    stime = time.perf_counter()
    if not opts.quiet:
        client.progress = Spinner("API Requests ")

    # go get the data
    topics_df = get_topics_dataframe(client, active=opts.active)
    content_df = get_connected_content_dataframe(client)

    # show performance
    if client.progress:
        client.progress.finish()
        call_count = client.progress.index
        elapsed = time.perf_counter() - stime
        print("{} API Calls in {:.2f} seconds".format(call_count, elapsed))

    # do remaining transformations
    extend_topics_dataframe(topics_df, content_df)
    topics_df.reset_index(inplace=True)

    # save to spreadsheet
    if output_format == FileFormat.CSV:
        topics_df.to_csv(opts.output, index=False)
    else:
        topics_df.to_excel(opts.output, index=False)


def command_catalog(config: Configuration, opts: Namespace):

    # options specific to this command
    drop_missing = opts.drop_missing
    active_items = opts.active_items
    active_topics = opts.active_topics

    # what is the output format
    if opts.output.endswith(".csv"):
        output_format = FileFormat.CSV
    elif opts.output.endswith(".xlsx"):
        output_format = FileFormat.XLSX
    else:
        raise ValueError("only supports CSV and XLSX extensions")

    # create the client
    client = ApiClient(config)
    stime = time.perf_counter()
    if not opts.quiet:
        client.progress = Spinner("API Requests ")

    # go get the data
    items_df = get_items_dataframe(client, active=active_items)
    content_df = get_connected_content_dataframe(client, active=active_topics)

    # show performance
    if client.progress:
        client.progress.finish()
        call_count = client.progress.index
        elapsed = time.perf_counter() - stime
        print("{} API Calls in {:.2f} seconds".format(call_count, elapsed))

    # do remaining transformations

    # NOTE - extend is missing...
    if drop_missing:
        missing_mask = (items_df.all_menu_path == "") & (items_df.home_menu_path == "")
        items_df = items_df[~missing_mask]

    # save to spreadsheet
    if output_format == FileFormat.CSV:
        items_df.to_csv(opts.output, index=False)
    else:
        items_df.sys_class_name = items_df.sys_class_name.apply(
            lambda name: CATALOG_ITEM_CLASSES.get(name, name)
        )

        # more excel friendly names
        column_names = [
            "Item SysID",
            "Class",
            "Item Name",
            "Item Description",
            "Item Active",
            "Item Taxonomy Topic",
            "Catalogs SysID",
            "All Menu Path",
            "Home Menu Path",
        ]
        items_df.columns = column_names  # type: ignore
        items_df.to_excel(opts.output, index=False)
    return 0


def command_topic_icons(config: Configuration, opts: Namespace):
    dir_path = opts.output
    dir_path.mkdir(exist_ok=True)

    # create the client
    client = ApiClient(config)
    stime = time.perf_counter()
    if not opts.quiet:
        client.progress = Spinner("API Requests ")

    # get the topics
    topics_df = get_topics_dataframe(client, active=opts.active)

    # show performance
    if client.progress:
        call_count = client.progress.index
        client.progress.finish()
        elapsed = time.perf_counter() - stime
        print("{} API Calls in {:.2f} seconds".format(call_count, elapsed))

    progress = Bar("Download icons ", max=len(topics_df))
    for topic_id, icon_id in topics_df.icon.items():
        if len(icon_id) > 0:
            # convert topic_id to local path
            topic_path = topics_df.loc[topic_id, "topic_path"]  # type: ignore
            icon_filename = topic_path.replace(" / ", "--").replace(" ", "-")
            icon_path = dir_path / icon_filename

            # determine icon_url
            icon_url = (
                f"{config.endpoint.scheme}://{config.endpoint.host}/{icon_id}.iix"
            )
            with requests.get(icon_url, stream=True, verify=False) as response:
                response.raise_for_status()
                with icon_path.open("wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

            # check file type of icon
            icon_type = magic.from_file(icon_path)
            if icon_type.startswith("JPEG"):
                icon_path.rename(icon_path.with_suffix(".jpg"))
            elif icon_type.startswith("PNG"):
                icon_path.rename(icon_path.with_suffix(".png"))
            elif icon_type.startswith("SVG"):
                icon_path.rename(icon_path.with_suffix(".svg"))
            else:
                print("{icon_path}: image type {type} unknown", file=sys.stderr)
        progress.next()
    progress.finish()

    return 0


def command_sort_content(config: Configuration, opts: Namespace):
    # create the client
    client = ApiClient(config)
    stime = time.perf_counter()
    if not opts.quiet:
        client.progress = Spinner("API Requests ")

    content_api = TableApi(client, SnowTable.CONNECTED_CONTENT.with_fields("order"))

    # get the content connected to active topics
    query = ELQueries.CONNECTED_CONTENT_QUERY + "^topic.active=true"
    content_df = content_api.get_dataframe(query)

    # show performance
    if client.progress:
        call_count = client.progress.index
        client.progress.finish()
        elapsed = time.perf_counter() - stime
        print("{} API Calls in {:.2f} seconds".format(call_count, elapsed))
        client.progress = None

    # within those, mask out those that start with the topic_path
    topic_path_mask = content_df.topic_path.str.startswith(opts.topic_path)
    content_df = content_df[topic_path_mask]
    # make it not a "slice" of the data
    content_df = content_df.loc[:, ["item_name", "order"]]

    # recalculate the order column
    def normalize_string_for_sorting(name: str):
        return unicodedata.normalize("NFKC", name.lower())

    content_df["sorting_item_name"] = content_df.item_name.map(
        normalize_string_for_sorting
    )
    sorted_content = content_df.sort_values("sorting_item_name")  # type: ignore
    sorted_content["new_order"] = range(100, 100 + 10 * sorted_content.shape[0], 10)

    # modify the order of each item
    changed = sorted_content[sorted_content.order != sorted_content.new_order]
    total_count = len(changed)

    progress = Bar("Updating ", max=total_count)
    stime = time.perf_counter()
    for index, row in changed.iterrows():
        # "index" is a pandas "Label" and must be converted to string
        sys_id = str(index)
        r = content_api.update_record(sys_id, {"order": row.new_order})
        r.raise_for_status()
        progress.next()

    progress.finish()
    elapsed = time.perf_counter() - stime
    print("Updated {} records in {:.2f} seconds".format(total_count, elapsed))
    return 0
