"""Metrics over a completed replay: query -> stats json -> images.

Each metric module exposes `collect(exports, endpoint) -> dict` (query influx or
decode an export into plain data points) and, optionally, `render(data, outdir)
-> Path` (draw an image from that data). A module with no `render` is
json-only (its numbers live in the stats file, e.g. bal_size).

`run_all` collects every metric into `stats-<from>-<to>.json`, then renders each
image *from that json*. With `skip_query=True` it skips the query and renders
from an existing stats file — for iterating on the images, or rendering locally
from a stats file pulled off a server, with neither influx nor the exports.
"""

import json
from pathlib import Path

import config

from . import (
    bal_size,
    block_processing,
    block_processing_clean,
    cost_of_void,
    void_heatmap,
    void_skip,
    void_trend,
)

REGISTRY = {
    "cost_of_void": cost_of_void,
    "void_skip": void_skip,
    "block_processing": block_processing,
    "block_processing_clean": block_processing_clean,
    "bal_size": bal_size,
    "void_heatmap": void_heatmap,
    "void_trend": void_trend,
}


def run_all(
    exports: dict[str, Path], outdir: Path, blocks: tuple[int, int], *, skip_query: bool = False
) -> list[Path]:
    frm, to = blocks
    outdir = Path(outdir) / f"{frm}-{to}"  # scope by range so ranges don't clobber
    stats_path = outdir / "stats.json"

    if skip_query:
        if not stats_path.exists():
            raise SystemExit(f"{stats_path} not found — drop --skip-query")
        stats = json.loads(stats_path.read_text())
        print(f"metrics: loaded {stats_path}")
    else:
        endpoint = config.require("INFLUX_ENDPOINT")
        stats = {"range": list(blocks)}
        for name, mod in REGISTRY.items():
            try:
                stats[name] = mod.collect(exports, endpoint)
            except Exception as exc:  # one bad metric shouldn't sink the rest
                print(f"collect {name}: FAILED — {exc}")
                stats[name] = None
        outdir.mkdir(parents=True, exist_ok=True)
        stats_path.write_text(json.dumps(stats, indent=2))
        print(f"metrics: wrote {stats_path}")

    artifacts = [stats_path]
    for name, mod in REGISTRY.items():
        if not hasattr(mod, "render"):
            continue
        data = stats.get(name)
        if data is None:
            print(f"render {name}: skipped (no data)")
            continue
        if isinstance(data, dict):
            data.setdefault("range", stats["range"])
        try:
            artifact = mod.render(data, outdir)
        except Exception as exc:
            print(f"render {name}: FAILED — {exc}")
            continue
        print(f"metric {name}: wrote {artifact}")
        artifacts.append(artifact)
    return artifacts
