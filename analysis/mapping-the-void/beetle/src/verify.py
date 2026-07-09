from pathlib import Path

import config
import geth
import snapshot

WORK = Path(__file__).resolve().parent.parent / "work"

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
    snapshot_dir = Path(config.require("SNAPSHOT_DIR"))
    WORK.mkdir(exist_ok=True)

    results = {}
    for arm in geth.ARMS:
        geth_bin = geth.ensure_arm(arm)
        copy = snapshot.reflink_copy(snapshot_dir, WORK / f"verify-{arm}")
        try:
            results[arm] = resolves(geth_bin, copy, blocks, WORK / f"verify-{arm}.rlp")
        finally:
            snapshot.remove(copy)
            (WORK / f"verify-{arm}.rlp").unlink(missing_ok=True)

    for arm, (ok, detail) in results.items():
        print(f"{'PASS' if ok else 'FAIL'} {arm}: {detail}")
    if not all(ok for ok, _ in results.values()):
        raise SystemExit(1)
    frm, to = blocks
    print(f"verification successful — snapshot serves blocks {frm}..{to} for both arms")
