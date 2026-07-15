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

# Offline node booted for heal / debug_setHead, then torn down.
_RPC = "http://127.0.0.1:8545"
_HTTP_PORT = "8545"
_AUTHRPC_PORT = "8551"
_STARTUP_SECS = 120


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
    print(f"\n===== EXPORT {geth_bin.name}: blocks {frm}..{to} (+BAL) =====")
    # Archive mode constructs the state-history indexer, without which geth
    # refuses to serve the historical parent states the BAL recompute reads.
    # `beetle index` must have built the index on the snapshot beforehand.
    return run(
        geth_bin,
        *flags(datadir),
        "--gcmode",
        "archive",
        "export",
        WITH_BAL,
        str(out),
        str(frm),
        str(to),
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
def _offline_node(geth_bin: Path, datadir: Path, *extra: str):
    # No stdout/stderr redirect: geth's log inherits the terminal and streams
    # live, so a failed boot is visible right where it happens.
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
            *extra,
        ],
    )
    try:
        for _ in range(_STARTUP_SECS):
            try:
                if "result" in _rpc("eth_blockNumber"):
                    break
            except OSError, ValueError:
                pass
            time.sleep(1)
        else:
            raise SystemExit(
                f"offline node never answered within {_STARTUP_SECS}s (see geth log above)"
            )
        yield node
    finally:
        node.terminate()
        try:
            node.wait(timeout=30)
        except subprocess.TimeoutExpired:
            node.kill()
        time.sleep(1)


_ZERO_ADDRESS = "0x" + "00" * 20
_PROBE_DEPTH = 80_000  # comfortably inside the 90k-block state-history retention
_INDEX_POLL_SECS = 15


def index_history(geth_bin: Path, datadir: Path) -> None:
    """Boot archive mode on the datadir and wait until the state-history
    indexer can serve historical state, then shut down cleanly. The index
    lands in the key-value store, so copies of the datadir inherit it. The
    boot also repairs an unclean tip and creates freezer tables the snapshot
    predates (what the old heal phase did)."""
    with _offline_node(geth_bin, datadir, "--gcmode", "archive") as node:
        head = int(_rpc("eth_blockNumber")["result"], 16)
        probe = max(head - _PROBE_DEPTH, 1)
        start = time.monotonic()
        while True:
            reply = _rpc("eth_getBalance", _ZERO_ADDRESS, hex(probe))
            if "result" in reply:
                print(f"index ready — historical state at block {probe} resolves")
                return
            if node.poll() is not None:
                raise SystemExit("geth exited while indexing (see log above)")
            error = reply.get("error", {}).get("message", "no error given")
            print(f"[{int(time.monotonic() - start)}s] block {probe}: {error}")
            time.sleep(_INDEX_POLL_SECS)


_REWIND_POLL_SECS = 10
_REWIND_DEADLINE_SECS = 3600


def rewind(geth_bin: Path, datadir: Path, to_block: int) -> int:
    # debug_setHead applies one reverse diff per rewound block before it
    # returns, so any fixed HTTP timeout loses on big ranges: fire the call,
    # shrug off the client-side timeout, and poll the head instead. The
    # tx-history flag pins the retention to "keep all" so the boot doesn't
    # spend the whole rewind background-unindexing the fully indexed base.
    with _offline_node(geth_bin, datadir, "--history.transactions", "0") as node:
        try:
            reply = _rpc("debug_setHead", hex(to_block))
            if "error" in reply:
                raise SystemExit(f"debug_setHead failed: {reply['error']}")
        except TimeoutError:
            print(f"setHead still running after the RPC timeout; polling the head")
        deadline = time.monotonic() + _REWIND_DEADLINE_SECS
        while True:
            try:
                head = int(_rpc("eth_blockNumber")["result"], 16)
            except OSError, ValueError:
                head = None
            if head == to_block:
                return head
            if node.poll() is not None:
                raise SystemExit("geth exited during rewind (see log above)")
            if time.monotonic() > deadline:
                raise SystemExit(
                    f"rewind to {to_block} still at {head} after {_REWIND_DEADLINE_SECS}s"
                )
            print(f"rewinding... head at {head}, target {to_block}")
            time.sleep(_REWIND_POLL_SECS)


def has_with_bal(geth_bin: Path) -> bool:
    help_text = subprocess.run(
        [str(geth_bin), "export", "--help"], capture_output=True, text=True
    ).stdout
    return WITH_BAL in help_text
