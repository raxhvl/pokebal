import argparse

import verify


def block_range(text: str) -> tuple[int, int]:
    lo, _, hi = text.partition("..")
    if not hi:
        raise argparse.ArgumentTypeError("range must look like FROM..TO")
    return int(lo), int(hi)


def cmd_verify(args: argparse.Namespace) -> None:
    verify.run(args.blocks)


def cmd_run(args: argparse.Namespace) -> None:
    raise SystemExit("run: not yet implemented")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="beetle")
    sub = parser.add_subparsers(required=True)

    verify_cmd = sub.add_parser(
        "verify", help="check the snapshot can serve historical state"
    )
    verify_cmd.add_argument("--range", dest="blocks", type=block_range, required=True)
    verify_cmd.set_defaults(func=cmd_verify)

    run_cmd = sub.add_parser(
        "run", help="build both arms, verify, then replay the range"
    )
    run_cmd.add_argument("--range", dest="blocks", type=block_range, required=True)
    run_cmd.set_defaults(func=cmd_run)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)
