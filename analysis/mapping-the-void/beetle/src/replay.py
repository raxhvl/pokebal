import urllib.parse
import urllib.request

import config
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


def _export(geth_bin, datadir, out, blocks: tuple[int, int]) -> None:
    snapshot.EXPORTS.mkdir(parents=True, exist_ok=True)
    out.unlink(missing_ok=True)
    export = geth.export_blocks(geth_bin, datadir, out, blocks)
    bad = (
        export.code != 0
        or not out.exists()
        or out.stat().st_size == 0
        or any(m in export.output.lower() for m in _EXPORT_BAD)
    )
    if bad:
        out.unlink(missing_ok=True)
        raise SystemExit(
            f"export failed, chain untouched — {_fail_line(export.output, _EXPORT_BAD)}"
        )


def leg(
    arm: str, blocks: tuple[int, int], *, skip_build: bool, skip_export: bool
) -> str:
    frm, to = blocks
    geth_bin = geth.binary(arm) if skip_build else geth.build(arm)
    if not geth_bin.exists():
        raise SystemExit(f"replay {arm}: {geth_bin} not built — drop --skip-build")
    export = snapshot.EXPORTS / f"{arm}-{frm}-{to}.rlp"
    with snapshot.workspace(f"replay-{arm}") as ws:
        datadir = ws / "datadir"

        if skip_export:
            if not (export.exists() and export.stat().st_size > 0):
                raise SystemExit(f"replay {arm}: {export} not exported — drop --skip-export")
            print(f"reusing export {export}")
        else:
            _export(geth_bin, datadir, export, blocks)

        head = geth.rewind(geth_bin, datadir, frm - 1)
        if head != frm - 1:
            raise SystemExit(f"replay {arm}: rewind landed at {head}, wanted {frm - 1}")

        imported = geth.import_blocks(geth_bin, datadir, export, arm)
        if imported.code != 0 or any(m in imported.output.lower() for m in _IMPORT_BAD):
            raise SystemExit(
                f"replay {arm}: import failed, datadir left rewound — "
                f"{_fail_line(imported.output, _IMPORT_BAD)}"
            )
    return f"replayed {frm}..{to} · export {export}"


def _reset_metrics() -> None:
    endpoint = config.require("INFLUX_ENDPOINT")
    for q in ("DROP DATABASE geth", "CREATE DATABASE geth"):
        req = urllib.request.Request(
            f"{endpoint}/query", data=urllib.parse.urlencode({"q": q}).encode(), method="POST"
        )
        try:
            urllib.request.urlopen(req, timeout=15).read()
        except OSError as e:
            raise SystemExit(f"influx reset failed on {q!r}: {e}")
    print("influx: reset database 'geth' — fresh metrics for this run")


def run(
    blocks: tuple[int, int], *, skip_build: bool = False, skip_export: bool = False
) -> None:
    frm, _ = blocks
    if frm < 2:
        raise SystemExit("replay: from must be >= 2 — can't rewind to genesis safely")
    _reset_metrics()
    for arm in geth.ARMS:
        print(
            f"OK {arm}: {leg(arm, blocks, skip_build=skip_build, skip_export=skip_export)}"
        )
    print("replay complete for both arms")
