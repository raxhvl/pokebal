# beetle

Supporting tool for the ["mapping the void"](../README.md) analysis. Given a geth
repo and a snapshot, it builds two BAL arms and replays a block range to compare
them.

## Setup

Copy `.env.example` to `.env` and fill in:

- `SNAPSHOT_DIR` — the geth snapshot (datadir) to replay
- `GETH_REPO_PATH` — the geth repo the two arms are built from

## Usage

```sh
uv run beetle verify --range <from..to>   # precheck: snapshot serves historical state
uv run beetle replay --range <from..to>   # build arms, replay the range on each
```

Run `verify` once as a precheck before `replay` — `replay` skips the historical-state
check to avoid re-doing that work every run.
