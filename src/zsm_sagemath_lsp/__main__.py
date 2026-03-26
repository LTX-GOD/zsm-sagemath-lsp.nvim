from __future__ import annotations

import argparse
import logging
import sys

from .server import server


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="zsm-sagemath-lsp server")
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument("--version", action="store_true")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.version:
        from . import __version__

        print(__version__)
        return

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    server.start_io()


if __name__ == "__main__":
    main()
