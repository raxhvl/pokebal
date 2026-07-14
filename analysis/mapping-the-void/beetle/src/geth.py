import contextlib
import json
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import config

WITH_BAL = "--with-bal"

ARMS = {
    "base": "lab/baseline-bal-replay",
    "empty": "lab/bal-with-empty",
}

# Offline node booted only to issue debug_setHead, then torn down.
_RPC = "http://127.0.0.1:8545"
_HTTP_PORT = "8545"
_AUTHRPC_PORT = "8551"
_STARTUP_SECS = 20


@dataclass
class Result:
    code: int
    output: str


def repo() -> Path:
    return Path(config.require("GETH_REPO_PATH"))


def binary(arm: str) -> Path:
    return repo() / "build" / "bin" / f"geth-{arm}"


def build(arm: str) -> Path:
    path = binary(arm)
    branch = ARMS[arm]
    subprocess.run(["git", "-C", str(repo()), "checkout", branch], check=True)
    subprocess.run(["make", "geth"], cwd=repo(), check=True)
    (repo() / "build" / "bin" / "geth").rename(path)
    if not has_with_bal(path):
        raise SystemExit(f"{path} lacks --with-bal — is {branch!r} the right branch?")
    return path


def flags(datadir: Path) -> list[str]:
    return ["--datadir", str(datadir), "--state.scheme", "path"]


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
    heal(geth_bin, datadir)
    return run(
        geth_bin, *flags(datadir), "export", WITH_BAL, str(out), str(frm), str(to)
    )


def import_blocks(geth_bin: Path, datadir: Path, blocks_file: Path) -> Result:
    return run(geth_bin, *flags(datadir), "import", WITH_BAL, str(blocks_file))


def _rpc(method: str, *params: str) -> dict:
    body = json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": method, "params": list(params)}
    ).encode()
    req = urllib.request.Request(
        _RPC, data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)


@contextlib.contextmanager
def _offline_node(geth_bin: Path, datadir: Path):
    node = subprocess.Popen(
        [
            str(geth_bin),
            *flags(datadir),
            "--http",
            "--http.port",
            _HTTP_PORT,
            "--http.api",
            "eth,debug",
            "--authrpc.port",
            _AUTHRPC_PORT,
            "--nodiscover",
            "--maxpeers",
            "0",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(_STARTUP_SECS):
            try:
                if "result" in _rpc("eth_blockNumber"):
                    break
            except (OSError, ValueError):
                pass
            time.sleep(1)
        else:
            raise SystemExit("offline node never answered within startup window")
        yield
    finally:
        node.terminate()
        try:
            node.wait(timeout=30)
        except subprocess.TimeoutExpired:
            node.kill()
        time.sleep(1)


def heal(geth_bin: Path, datadir: Path) -> None:
    """Boot read-write once so the freezer creates any table the snapshot
    predates (a read-only export can't). No chain mutation."""
    with _offline_node(geth_bin, datadir):
        pass


def rewind(geth_bin: Path, datadir: Path, to_block: int) -> int:
    with _offline_node(geth_bin, datadir):
        _rpc("debug_setHead", hex(to_block))
        return int(_rpc("eth_blockNumber")["result"], 16)


def has_with_bal(geth_bin: Path) -> bool:
    help_text = subprocess.run(
        [str(geth_bin), "export", "--help"], capture_output=True, text=True
    ).stdout
    return WITH_BAL in help_text
