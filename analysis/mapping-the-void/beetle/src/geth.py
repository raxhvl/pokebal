import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import config

WITH_BAL = "--with-bal"

ARMS = {
    "base": "lab/baseline-bal-replay",
    "empty": "lab/bal-with-empty",
}


@dataclass
class Result:
    code: int
    output: str


def repo() -> Path:
    return Path(config.require("GETH_REPO_PATH"))


def binary(arm: str) -> Path:
    return repo() / "build" / "bin" / f"geth-{arm}"


def ensure_arm(arm: str) -> Path:
    path = binary(arm)
    if path.exists():
        return path
    branch = ARMS[arm]
    subprocess.run(["git", "-C", str(repo()), "checkout", branch], check=True)
    subprocess.run(["make", "geth"], cwd=repo(), check=True)
    (repo() / "build" / "bin" / "geth").rename(path)
    if not has_with_bal(path):
        raise SystemExit(f"{path} lacks --with-bal — is {branch!r} the right branch?")
    return path


def flags(datadir: Path) -> list[str]:
    return ["--datadir", str(datadir)]


def run(geth_bin: Path, *args: str) -> Result:
    proc = subprocess.Popen(
        [str(geth_bin), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    captured = []
    for line in proc.stdout:
        sys.stdout.write(line)
        captured.append(line)
    proc.wait()
    return Result(proc.returncode, "".join(captured))


def export_blocks(
    geth_bin: Path, datadir: Path, out: Path, blocks: tuple[int, int]
) -> Result:
    frm, to = blocks
    return run(
        geth_bin, *flags(datadir), "export", WITH_BAL, str(out), str(frm), str(to)
    )


def import_blocks(geth_bin: Path, datadir: Path, blocks_file: Path) -> Result:
    return run(geth_bin, *flags(datadir), "import", WITH_BAL, str(blocks_file))


def has_with_bal(geth_bin: Path) -> bool:
    help_text = subprocess.run(
        [str(geth_bin), "export", "--help"], capture_output=True, text=True
    ).stdout
    return WITH_BAL in help_text
