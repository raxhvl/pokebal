from pathlib import Path

import geth
import snapshot

_BAD = ("missing trie node", "export error", "fatal")


def _human(size: int) -> str:
    value = float(size)
    for unit in ("B", "KiB", "MiB"):
        if value < 1024:
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} GiB"


def resolves(
    geth_bin: Path, datadir: Path, blocks: tuple[int, int], out: Path
) -> tuple[bool, str]:
    frm, to = blocks
    out.unlink(missing_ok=True)
    result = geth.export_blocks(geth_bin, datadir, out, blocks)
    lower = result.output.lower()
    healthy = result.code == 0 and out.exists() and out.stat().st_size > 0
    if healthy and not any(marker in lower for marker in _BAD):
        return (
            True,
            f"blocks {frm}..{to} resolved · {_human(out.stat().st_size)} export",
        )
    reason = next(
        (
            line
            for line in result.output.splitlines()
            if any(m in line.lower() for m in _BAD)
        ),
        "see output above",
    )
    return False, reason


def run(blocks: tuple[int, int]) -> None:
    results = {}
    for arm in geth.ARMS:
        geth_bin = geth.build(arm)
        with snapshot.workspace(f"verify-{arm}") as ws:
            results[arm] = resolves(geth_bin, ws / "datadir", blocks, ws / "export.rlp")

    for arm, (ok, detail) in results.items():
        print(f"{'PASS' if ok else 'FAIL'} {arm}: {detail}")
    if not all(ok for ok, _ in results.values()):
        raise SystemExit(1)
    frm, to = blocks
    print(f"verification successful — snapshot serves blocks {frm}..{to} for both arms")
