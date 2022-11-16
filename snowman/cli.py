import sys
from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path

from .config import SnowmanConfig
from .commands import command_catalog, command_config

# ------------------------------------------------------------------------------
# TYPES
# ------------------------------------------------------------------------------


def pathlib_path(value: str):
    return Path(value)


def existing_pathlib_path(value: str):
    path = Path(value)
    if not path.exists():
        raise ArgumentTypeError("path does not exist")
    return path


# ------------------------------------------------------------------------------
# PARSER
# ------------------------------------------------------------------------------


def create_parser(prog_name="snowman"):

    parent = ArgumentParser(add_help=False)
    parent.add_argument(
        "--config",
        "-c",
        metavar="PATH",
        default=SnowmanConfig.get_default_path(),
        type=existing_pathlib_path,
        help="Path to a configuration file for this software",
    )
    parser = ArgumentParser(prog=prog_name, description="Utility for ServiceNow")
    sp = parser.add_subparsers(dest="command")

    # command to create configuration
    scmd = sp.add_parser("config", help="Creates the configuration file")
    scmd.add_argument(
        "path",
        metavar="PATH",
        default=SnowmanConfig.get_default_path(),
        type=pathlib_path,
        help="Creates configuration file",
    )

    # command to analyze catalog items
    scmd = sp.add_parser(
        "catalog", parents=[parent], help="Reads sc_cat_items to a CSV or Excel"
    )
    scmd.add_argument("output", metavar="PATH", help="Path to CSV or Excel output")
    scmd.set_defaults(func=command_catalog)

    return parser


# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------


def main(args=None):
    if args is None:
        args = sys.argv
    parser = create_parser(args[0])
    opts = parser.parse_args(args[1:])

    if not hasattr(opts, "func"):
        parser.print_help()
        return 1

    if opts.command == "config":
        return command_config(opts)

    config = SnowmanConfig.load(opts.config)
    return (opts.func)(config, opts)


if __name__ == "__main__":
    rv = main()
    if rv != 0:
        raise SystemExit(rv)
