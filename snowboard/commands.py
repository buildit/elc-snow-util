import sys
from argparse import Namespace
from enum import Enum, unique

import magic
import requests

from . import Configuration, ApiClient
from .tables import CATALOG_ITEM_CLASSES
from .elc_utils import (
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

    # go get the data
    client = ApiClient(config)
    topics_df = get_topics_dataframe(client, active=opts.active)
    content_df = get_connected_content_dataframe(client)
    extend_topics_dataframe(topics_df, content_df)
    topics_df.reset_index(inplace=True)

    if output_format == FileFormat.CSV:
        topics_df.to_csv(opts.output, index=False)
    else:
        topics_df.to_excel(opts.output, index=False)


def command_catalog(config: Configuration, opts: Namespace):

    # will we add the extra columns
    extend_flag = opts.extend
    drop_missing = opts.drop_missing

    # what is the output format
    if opts.output.endswith(".csv"):
        output_format = FileFormat.CSV
    elif opts.output.endswith(".xlsx"):
        output_format = FileFormat.XLSX
    else:
        raise ValueError("only supports CSV and XLSX extensions")

    client = ApiClient(config)
    items_df = get_items_dataframe(client)
    content_df = get_connected_content_dataframe(client)

    extend_items_with_menu_location(items_df, content_df)
    if extend_flag:
        add_missing_and_mismatch_columns(items_df)

    if drop_missing:
        missing_mask = (items_df.all_menu_path == "") & (items_df.home_menu_path == "")
        items_df = items_df[~missing_mask]

        if extend_flag:
            items_df.drop(columns="menu_missing", inplace=True)

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
        if extend_flag:
            if drop_missing:
                column_names += ["Menu Missing", "Menu Mismatch"]
            else:
                column_names += ["Menu Mismatch"]
        items_df.columns = column_names  # type: ignore
        items_df.to_excel(opts.output, index=False)
    return 0


def command_topic_icons(config: Configuration, opts: Namespace):
    dir_path = opts.output
    dir_path.mkdir(exist_ok=True)

    client = ApiClient(config)
    topics_df = get_topics_dataframe(client, active=opts.active)

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

    return 0


def command_sort_content(config: Configuration, opts: Namespace):
    print("sort-content: Not yet implemented", file=sys.stderr)
    return 1
