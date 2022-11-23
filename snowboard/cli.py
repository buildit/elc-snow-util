import sys
from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path
from warnings import filterwarnings

from urllib3.exceptions import InsecureRequestWarning

from .config import Configuration
from .commands import (
    command_catalog,
    # command_config,
    command_sort_content,
    command_topics,
    command_topic_icons,
)

# ------------------------------------------------------------------------------
# TYPES
# ------------------------------------------------------------------------------


def pathlib_path(value: str):
    return Path(value)


# ------------------------------------------------------------------------------
# PARSER
# ------------------------------------------------------------------------------


def create_parser(prog_name="snowman"):

    parent = ArgumentParser(add_help=False)
    parent.add_argument(
        "--config",
        "-c",
        metavar="PATH",
        default=Configuration.get_default_path(),
        type=pathlib_path,
        help="Path to a configuration file for this software",
    )
    parent.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        default=False,
        help="Suppress progress report",
    )
    parser = ArgumentParser(prog=prog_name, description="Utility for ServiceNow")
    sp = parser.add_subparsers(dest="command")

    # command to create configuration
    # scmd = sp.add_parser("config", help="Creates the configuration file")
    # scmd.add_argument(
    #     "path",
    #     metavar="PATH",
    #     default=Configuration.get_default_path(),
    #     type=pathlib_path,
    #     help="Creates configuration file",
    # )

    # command to analyze catalog items
    scmd = sp.add_parser(
        "catalog-report", parents=[parent], help="Reads sc_cat_items to a CSV or Excel"
    )
    scmd.add_argument("output", metavar="PATH", help="Path to CSV or Excel")
    scmd.add_argument(
        "--extend",
        "-e",
        action="store_true",
        default=False,
        help="Add columns for missing meuns and mismatch",
    )
    scmd.add_argument(
        "--drop-missing",
        action="store_true",
        default=False,
        help="Drop items missing from both menus",
    )
    scmd.set_defaults(func=command_catalog)

    # command to sort items in a major topic
    scmd = sp.add_parser(
        "sort-content",
        parents=[parent],
        help="Sorts catalog items connected to a topic",
    )
    scmd.add_argument("topic_path", metavar="TOPIC_PATH", help="Which topic to reorder")
    scmd.set_defaults(func=command_sort_content)

    # command to analyze topics
    scmd = sp.add_parser(
        "topics-report", parents=[parent], help="Reads topic table to a CSV or Excel"
    )
    scmd.add_argument("output", metavar="PATH", help="Path to CSV or Excel")
    scmd.add_argument(
        "--active",
        "-a",
        action="store_true",
        default=False,
        help="Retrieve only active topics",
    )
    scmd.set_defaults(func=command_topics)

    # command to download topic images
    scmd = sp.add_parser(
        "topic-icons", parents=[parent], help="Download topic icons and classify"
    )
    scmd.add_argument(
        "output", metavar="PATH", type=pathlib_path, help="Path to a directory"
    )
    scmd.add_argument(
        "--active",
        "-a",
        action="store_true",
        default=False,
        help="Retrieve icons only for active topics",
    )
    scmd.set_defaults(func=command_topic_icons)

    return parser


# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------


def main(args=None):
    # because of Zscaler, we need to not verify requests
    filterwarnings("ignore", category=InsecureRequestWarning)

    # parse arguments
    if args is None:
        args = sys.argv
    parser = create_parser(args[0])
    opts = parser.parse_args(args[1:])

    # must be a sub-command
    if not hasattr(opts, "func"):
        parser.print_help()
        return 1

    # if opts.command == "config":
    #     return command_config(opts)
    if not opts.config.exists():
        print("{}: configuration file not found".format(opts.config), file=sys.stderr)
        return 1

    config = Configuration.load(opts.config)
    return (opts.func)(config, opts)


if __name__ == "__main__":
    rv = main()
    if rv != 0:
        raise SystemExit(rv)
