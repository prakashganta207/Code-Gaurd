"""``codeguard`` command line. Parses input, calls the pipeline, prints output. No logic here."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from codeguard import __version__
from codeguard.config import load_settings


def _not_yet(phase: str) -> int:
    print(f"Not implemented yet (arrives in {phase}).")
    return 2


def _show_config(_: argparse.Namespace) -> int:
    print(load_settings().model_dump_json(indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="codeguard",
        description="Detect and repair security vulnerabilities in LLM-generated Python code.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    scan = sub.add_parser("scan", help="scan a Python file for vulnerabilities")
    scan.add_argument("file", help="path to a .py file")
    scan.set_defaults(func=lambda _: _not_yet("Phase 2"))

    gen = sub.add_parser("generate", help="generate code from a prompt, then scan and repair it")
    gen.add_argument("prompt", help="coding prompt for the LLM")
    gen.set_defaults(func=lambda _: _not_yet("Phase 2"))

    rep = sub.add_parser("repair", help="scan a Python file and repair what is found")
    rep.add_argument("file", help="path to a .py file")
    rep.set_defaults(func=lambda _: _not_yet("Phase 2"))

    cfg = sub.add_parser("config", help="print the effective settings")
    cfg.set_defaults(func=_show_config)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``codeguard`` console script."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
