import argparse

import replay
import verify


def block_range(text: str) -> tuple[int, int]:
    lo, _, hi = text.partition("..")
    if not hi:
        raise argparse.ArgumentTypeError("range must look like FROM..TO")
    return int(lo), int(hi)


def cmd_verify(args: argparse.Namespace) -> None:
    verify.run(args.blocks)


def cmd_replay(args: argparse.Namespace) -> None:
    replay.run(args.blocks)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="beetle")
    sub = parser.add_subparsers(required=True)

    verify_cmd = sub.add_parser(
        "verify", help="check the snapshot can serve historical state"
    )
    verify_cmd.add_argument("--range", dest="blocks", type=block_range, required=True)
    verify_cmd.set_defaults(func=cmd_verify)

    replay_cmd = sub.add_parser(
        "replay", help="build both arms, then replay the range on each"
    )
    replay_cmd.add_argument("--range", dest="blocks", type=block_range, required=True)
    replay_cmd.set_defaults(func=cmd_replay)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)
