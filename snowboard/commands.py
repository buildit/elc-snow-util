from enum import Enum, unique
from . import Configuration, ApiClient
from .tables import CATALOG_ITEM_CLASSES
from .elc_utils import (
    get_active_items_dataframe,
    get_connected_content_dataframe,
    extend_active_items_with_menu_location,
    add_missing_and_mismatch_columns,
    get_topics_dataframe,
    extend_topics_dataframe,
)


@unique
class FileFormat(Enum):
    CSV = "csv"
    XLSX = "xlsx"


def command_config(opts):
    print("Not yet implemented")
    return 0


def command_topics(config: Configuration, opts):

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


def command_catalog(config: Configuration, opts):

    # will we add the extra columns
    extend_flag = opts.extend

    # what is the output format
    if opts.output.endswith(".csv"):
        output_format = FileFormat.CSV
    elif opts.output.endswith(".xlsx"):
        output_format = FileFormat.XLSX
    else:
        raise ValueError("only supports CSV and XLSX extensions")

    client = ApiClient(config)
    items_df = get_active_items_dataframe(client)
    content_df = get_connected_content_dataframe(client)

    extend_active_items_with_menu_location(items_df, content_df)
    if extend_flag:
        add_missing_and_mismatch_columns(items_df)

    if output_format == FileFormat.CSV:
        items_df.to_csv(opts.output, index=False)
    else:
        items_df.sys_class_name = items_df.sys_class_name.apply(
            lambda name: CATALOG_ITEM_CLASSES.get(name, name)
        )

        # more excel friendly names
        column_names = [
            "SysID",
            "Class",
            "Item Name",
            "Item Description",
            "All Menu Path",
            "Home Menu Path",
        ]
        if extend_flag:
            column_names += ["Menu Missing", "Menu Mismatch"]
        items_df.columns = column_names  # type: ignore
        items_df.to_excel(opts.output, index=False)
    return 0
