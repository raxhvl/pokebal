# beetle

Supporting tool for the ["mapping the void"](../README.md) analysis. Given a geth
repo and a snapshot, it builds two BAL arms and replays a block range to compare
them.

## Setup

Copy `.env.example` to `.env` and fill in:

- `SNAPSHOT_DIR` — the geth snapshot (datadir) to replay
- `GETH_REPO_PATH` — the geth repo the two arms are built from
- `SNAPSHOT_MODE` — how each arm gets a private, disposable view of the snapshot
- `INFLUX_ENDPOINT` — influx db instance  
  without touching the pristine one:
  - `reflink` — CoW copy via `cp --reflink` (btrfs / XFS-with-reflink; rootless)
  - `overlay` — overlayfs mount with the snapshot as read-only lower (ext4 and
    other non-CoW filesystems; needs root for `mount`)

## Usage

```sh
uv run beetle verify --range <from..to>   # precheck: snapshot serves historical state
uv run beetle replay --range <from..to>   # build arms, replay the range on each
```

Run `verify` once as a precheck before `replay` — `replay` skips the historical-state
check to avoid re-doing that work every run.

## Tests

```sh
uv run pytest                    # fast suite, synthetic exports only
uv run pytest tests/scale.py -s  # scale bench: 89k-block / ~26 GB synthetic export
```

The scale bench is excluded from the plain run by its filename; it generates
its export into `work/bench/` (deleted again when the run ends) and prints
the resource profile of the metrics pass (heap, mmap cache, stats-json size).
