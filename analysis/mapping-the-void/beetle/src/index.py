from pathlib import Path

import config
import geth


def run(*, skip_build: bool = False) -> None:
    geth_bin = geth.binary("base") if skip_build else geth.build("base")
    if not geth_bin.exists():
        raise SystemExit(f"index: {geth_bin} not built — drop --skip-build")
    datadir = Path(config.require("SNAPSHOT_DIR"))
    print(f"indexing state history in place on {datadir} (one-time, mutates the snapshot)")
    geth.index_history(geth_bin, datadir)
    print("snapshot indexed — verify/replay working copies will inherit the index")
