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
    replay.run(args.blocks, skip_build=args.skip_build, keep_export=args.keep_export)


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
    replay_cmd.add_argument(
        "--skip-build", action="store_true", help="reuse the built arm binaries"
    )
    replay_cmd.add_argument(
        "--keep-export",
        action="store_true",
        help="keep the exported blocks after the run",
    )
    replay_cmd.set_defaults(func=cmd_replay)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)
