import shutil
import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import config

WORK = Path(__file__).resolve().parent.parent / "work"


def reflink_copy(src: Path, dst: Path) -> Path:
    remove(dst)
    result = subprocess.run(
        ["cp", "--reflink=always", "-a", str(src), str(dst)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        remove(dst)
        raise SystemExit(
            "reflink copy failed — the filesystem must support CoW; refusing to "
            f"full-copy a snapshot:\n{result.stderr.strip()}"
        )
    return dst


def remove(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)


def _overlay_mount(lower: Path, merged: Path, root: Path) -> None:
    upper, work = root / "upper", root / "ovl"
    for d in (merged, upper, work):
        d.mkdir()
    opts = f"lowerdir={lower},upperdir={upper},workdir={work}"
    result = subprocess.run(
        ["mount", "-t", "overlay", "overlay", "-o", opts, str(merged)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(f"overlay mount failed (needs root):\n{result.stderr.strip()}")


@contextmanager
def workspace(name: str) -> Iterator[Path]:
    root = WORK / name
    remove(root)
    root.mkdir(parents=True)
    datadir = root / "datadir"
    lower = Path(config.require("SNAPSHOT_DIR"))
    mode = config.require("SNAPSHOT_MODE")
    match mode:
        case "reflink":
            reflink_copy(lower, datadir)
        case "overlay":
            _overlay_mount(lower, datadir, root)
        case other:
            raise SystemExit(f"SNAPSHOT_MODE must be 'reflink' or 'overlay', not {other!r}")
    try:
        yield root
    finally:
        if mode == "overlay":
            subprocess.run(["umount", str(datadir)], capture_output=True, text=True)
        remove(root)
