import argparse

import geth
import index
import replay
import snapshot
import verify


def block_range(text: str) -> tuple[int, int]:
    lo, _, hi = text.partition("..")
    if not hi:
        raise argparse.ArgumentTypeError("range must look like FROM..TO")
    return int(lo), int(hi)


def cmd_index(args: argparse.Namespace) -> None:
    index.run(skip_build=args.skip_build)


def cmd_verify(args: argparse.Namespace) -> None:
    verify.run(args.blocks)


def cmd_replay(args: argparse.Namespace) -> None:
    replay.run(args.blocks, skip_build=args.skip_build, skip_export=args.skip_export)


def cmd_metrics(args: argparse.Namespace) -> None:
    import metrics  # lazy: pulls in matplotlib, unwanted for replay/verify

    frm, to = args.blocks
    exports = {
        arm: path
        for arm in geth.ARMS
        if (path := snapshot.EXPORTS / f"{arm}-{frm}-{to}.rlp").exists()
    }
    if not exports:
        raise SystemExit(
            f"no exports for {frm}..{to} in {snapshot.EXPORTS} — "
            "run `beetle replay --range …` first"
        )
    metrics.run_all(exports, snapshot.WORK / "metrics")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="beetle")
    sub = parser.add_subparsers(required=True)

    index_cmd = sub.add_parser(
        "index",
        help="one-time: build the state-history index on the snapshot itself",
    )
    index_cmd.add_argument(
        "--skip-build", action="store_true", help="reuse the built arm binaries"
    )
    index_cmd.set_defaults(func=cmd_index)

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
        "--skip-export", action="store_true", help="reuse cached exports in work/exports/"
    )
    replay_cmd.set_defaults(func=cmd_replay)

    metrics_cmd = sub.add_parser(
        "metrics", help="run all metrics over a range's kept exports -> work/metrics/"
    )
    metrics_cmd.add_argument("--range", dest="blocks", type=block_range, required=True)
    metrics_cmd.set_defaults(func=cmd_metrics)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)
