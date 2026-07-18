"""Block execution wall-clock, with and without the void marker.

One panel, two lines — mean per-block EVM execution over the course of the
replay, baseline arm in ink, void-marked arm in green, the gap between them
shaded: that area is the time the marker gives back. Drawn from geth's own
chain/execution timer (real wall-clock, reported once a second, each report
covering the blocks imported in that interval), so unlike a sum of per-read
latencies it cannot overcount parallel reads.

collect() pulls the per-interval series and the range means from InfluxDB,
tagged host=BAL-base / host=BAL-empty.
"""

from pathlib import Path

import numpy as np

from metrics import influx, style


def _arm(endpoint: str, host: str) -> dict:
    rows = influx.series(endpoint, "chain/execution.timer", host, '"count", "mean"')
    counts = [r[1] for r in rows]
    return {
        "blocks": np.cumsum(counts).tolist(),  # blocks replayed by each report
        "ms": [r[2] / 1e6 for r in rows],
    }


def collect(exports: dict[str, Path], endpoint: str) -> dict:
    base_ms = influx.mean_ns(endpoint, "chain/execution.timer", "BAL-base") / 1e6
    empty_ms = influx.mean_ns(endpoint, "chain/execution.timer", "BAL-empty") / 1e6
    return {
        "base": _arm(endpoint, "BAL-base"),
        "empty": _arm(endpoint, "BAL-empty"),
        "base_ms": base_ms,
        "empty_ms": empty_ms,
        "saved_ms": base_ms - empty_ms,
    }


def render(data: dict, outdir: Path) -> Path:
    base, empty = data["base"], data["empty"]
    base_ms, empty_ms, saved = data["base_ms"], data["empty_ms"], data["saved_ms"]
    total = int(max(base["blocks"][-1], empty["blocks"][-1]))
    frm, to = data["range"]

    fig, ax = style.figure(
        1, 1, (9.5, 5.2),
        "Block execution time",
        f"mean wall-clock per block · blocks {frm:,}–{to:,}",
    )

    # common grid so the gap between the arms can be shaded
    grid = np.linspace(1, total, 400)
    base_i = np.interp(grid, base["blocks"], base["ms"])
    empty_i = np.interp(grid, empty["blocks"], empty["ms"])
    ax.fill_between(grid, empty_i, base_i, where=base_i >= empty_i,
                    color=style.SAVED, alpha=0.14, linewidth=0)

    ax.plot(base["blocks"], base["ms"], color=style.INK, linewidth=1.8)
    ax.plot(empty["blocks"], empty["ms"], color=style.SAVED, linewidth=1.8)

    for avg, color, label, dy in (
        (base_ms, style.INK, "BAL", 8),
        (empty_ms, style.SAVED, "BAL + void bitmap", -8),
    ):
        ax.axhline(avg, color=color, linewidth=1.0, linestyle=(0, (2, 3)), alpha=0.6)
        ax.annotate(f"{label} · avg {avg:.2f} ms", xy=(1.0, avg),
                    xycoords=("axes fraction", "data"), xytext=(8, dy),
                    textcoords="offset points", va="center",
                    fontsize=10, fontweight=600, color=color)

    style.badge(ax, 0.88, 0.55, f"saves {saved:.2f} ms/block · {saved / base_ms:.1%}",
                style.SAVED, style.SAVED_TINT, fontsize=12.5, transform=ax.transAxes)

    ax.set_ylabel("mean execution time (ms)")
    ax.set_xlim(0, total)
    ax.set_ylim(bottom=0)
    style.tidy(ax)
    style.drop_x_zero(ax)

    fig.subplots_adjust(top=0.80, bottom=0.13, left=0.07, right=0.82)
    style.caption(fig, "skipping void reads removes a disk descent from each block")
    return style.save(fig, outdir, "block-processing.png")
