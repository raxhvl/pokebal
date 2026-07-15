import geth
import snapshot

_EXPORT_BAD = ("missing trie node", "export error", "fatal")
_IMPORT_BAD = ("import error", "invalid block", "fatal")


def _fail_line(output: str, markers: tuple[str, ...]) -> str:
    return next(
        (
            line.strip()
            for line in output.splitlines()
            if any(m in line.lower() for m in markers)
        ),
        "see output above",
    )


def leg(
    arm: str, blocks: tuple[int, int], *, skip_build: bool, keep_export: bool
) -> str:
    frm, to = blocks
    geth_bin = geth.binary(arm) if skip_build else geth.build(arm)
    if not geth_bin.exists():
        raise SystemExit(f"replay {arm}: {geth_bin} not built — drop --skip-build")
    kept = None
    with snapshot.workspace(f"replay-{arm}") as ws:
        datadir = ws / "datadir"
        rlp = ws / f"blocks-{frm}-{to}.rlp"

        export = geth.export_blocks(geth_bin, datadir, rlp, blocks)
        bad_export = (
            export.code != 0
            or not rlp.exists()
            or rlp.stat().st_size == 0
            or any(m in export.output.lower() for m in _EXPORT_BAD)
        )
        if bad_export:
            raise SystemExit(
                f"replay {arm}: export failed, chain untouched — "
                f"{_fail_line(export.output, _EXPORT_BAD)}"
            )

        head = geth.rewind(geth_bin, datadir, frm - 1)
        if head != frm - 1:
            raise SystemExit(f"replay {arm}: rewind landed at {head}, wanted {frm - 1}")

        imported = geth.import_blocks(geth_bin, datadir, rlp)
        if imported.code != 0 or any(m in imported.output.lower() for m in _IMPORT_BAD):
            raise SystemExit(
                f"replay {arm}: import failed, datadir left rewound — "
                f"{_fail_line(imported.output, _IMPORT_BAD)}"
            )

        if keep_export:
            kept = snapshot.WORK / f"replay-{arm}-{frm}-{to}.rlp"
            rlp.rename(kept)
    return f"replayed {frm}..{to}" + (f" · kept {kept}" if kept else "")


def run(
    blocks: tuple[int, int], *, skip_build: bool = False, keep_export: bool = False
) -> None:
    frm, _ = blocks
    if frm < 2:
        raise SystemExit("replay: from must be >= 2 — can't rewind to genesis safely")
    for arm in geth.ARMS:
        print(
            f"OK {arm}: {leg(arm, blocks, skip_build=skip_build, keep_export=keep_export)}"
        )
    print("replay complete for both arms")
