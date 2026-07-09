import shutil
import subprocess
from pathlib import Path


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
