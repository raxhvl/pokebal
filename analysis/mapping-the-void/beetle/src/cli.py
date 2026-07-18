import argparse

import geth
import index
import replay
import sidecar
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


def _render_metrics(blocks: tuple[int, int], *, skip_query: bool) -> None:
    import metrics  # lazy: pulls in matplotlib, unwanted for replay/verify

    exports: dict[str, object] = {}
    if not skip_query:
        frm, to = blocks
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
    metrics.run_all(exports, snapshot.WORK / "metrics", blocks, skip_query=skip_query)


def cmd_replay(args: argparse.Namespace) -> None:
    replay.run(args.blocks, skip_build=args.skip_build, skip_export=args.skip_export)
    if args.metrics:
        _render_metrics(args.blocks, skip_query=False)


def cmd_metrics(args: argparse.Namespace) -> None:
    _render_metrics(args.blocks, skip_query=args.skip_query)


def cmd_splice(args: argparse.Namespace) -> None:
    frm, to = args.blocks
    end = args.end
    sources = {arm: snapshot.EXPORTS / f"{arm}-{frm}-{to}.rlp" for arm in geth.ARMS}
    for arm, src in sources.items():
        if not src.exists():
            raise SystemExit(f"no export {src} — check --range")
    for arm, src in sources.items():
        dst = snapshot.EXPORTS / f"{arm}-{frm}-{end}.rlp"
        try:
            first, last, count = sidecar.slice_to(src, dst, end)
        except ValueError as exc:
            raise SystemExit(f"splice {arm}: {exc}")
        print(f"{arm}: {count} blocks {first}..{last} -> {dst.name}")
    print("\ntrimmed both arms to the salvageable range — now the regular path:")
    print(f"  uv run beetle replay  --range {frm}..{end} --skip-export")
    print(f"  uv run beetle metrics --range {frm}..{end}")


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
    replay_cmd.add_argument(
        "--metrics", action="store_true", help="render metrics after the replay"
    )
    replay_cmd.set_defaults(func=cmd_replay)

    metrics_cmd = sub.add_parser(
        "metrics", help="query -> stats json -> images in work/metrics/"
    )
    metrics_cmd.add_argument("--range", dest="blocks", type=block_range, required=True)
    metrics_cmd.add_argument(
        "--skip-query",
        action="store_true",
        help="skip influx; render from the existing stats json",
    )
    metrics_cmd.set_defaults(func=cmd_metrics)

    splice_cmd = sub.add_parser(
        "splice", help="trim cached exports to end at --end (salvage a partial run)"
    )
    splice_cmd.add_argument(
        "--range",
        dest="blocks",
        type=block_range,
        required=True,
        help="the source export range, e.g. 25410001..25499000",
    )
    splice_cmd.add_argument(
        "--end",
        type=int,
        required=True,
        help="last block to keep (F-1, where F is the failed block)",
    )
    splice_cmd.set_defaults(func=cmd_splice)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)
