"""Block execution time with the importer's own noise cut out.

Companion to block_processing, which draws the series exactly as measured.
Two artifacts in that chart are import mechanics, not execution: cold-cache
warmup at the very start of the run, and a burst of slow blocks right after
every 2,500-block import batch handoff, where geth has just decoded the next
slice of the export file. Both sit at predictable positions and hit both
arms identically, so this chart drops the reporter intervals touching those
windows and recomputes the means from what remains. The raw chart stays as
the honest record; this one shows the steady state.

collect() reuses block_processing.collect and filters it; what was dropped
is recorded in the stats json, never silently.
"""

from pathlib import Path

import numpy as np

from metrics import block_processing, style

_WARMUP = 100  # blocks; cold caches at process start
_BATCH = 2500  # geth's importBatchSize (cmd/utils/cmd.go)
_SETTLE = 60   # blocks after a batch handoff before timings recover


def _windows(total: int) -> list[tuple[int, int]]:
    spans = [(0, _WARMUP)]
    for k in range(1, total // _BATCH + 1):
        spans.append((k * _BATCH, k * _BATCH + _SETTLE))
    return spans


def _clean(arm: dict) -> tuple[list[dict], float, int]:
    """Filter one arm's intervals into gap-separated segments.

    Returns (segments, event-weighted mean ms, dropped block count). An
    interval is dropped when the block span it reported overlaps any window.
    """
    windows = _windows(int(arm["blocks"][-1]))
    segments: list[dict] = []
    seg: dict = {"blocks": [], "ms": []}
    kept_ms = kept = dropped = 0
    prev = 0
    for block, ms in zip(arm["blocks"], arm["ms"]):
        lo, hi, prev = prev, block, block
        if any(lo < w_hi and hi > w_lo for w_lo, w_hi in windows):
            dropped += hi - lo
            if seg["blocks"]:
                segments.append(seg)
                seg = {"blocks": [], "ms": []}
            continue
        seg["blocks"].append(block)
        seg["ms"].append(ms)
        kept_ms += ms * (hi - lo)
        kept += hi - lo
    if seg["blocks"]:
        segments.append(seg)
    return segments, kept_ms / kept if kept else 0.0, int(dropped)


def collect(exports: dict[str, Path], endpoint: str) -> dict:
    raw = block_processing.collect(exports, endpoint)
    out: dict = {"dropped_blocks": {}, "total_blocks": {}}
    for arm in ("base", "empty"):
        segments, mean, dropped = _clean(raw[arm])
        out[arm] = {"segments": segments}
        out[f"{arm}_ms"] = mean
        out["dropped_blocks"][arm] = dropped
        out["total_blocks"][arm] = int(raw[arm]["blocks"][-1])
    out["saved_ms"] = out["base_ms"] - out["empty_ms"]
    return out


def render(data: dict, outdir: Path) -> Path:
    base_ms, empty_ms, saved = data["base_ms"], data["empty_ms"], data["saved_ms"]
    total = max(data["total_blocks"].values())
    pct = data["dropped_blocks"]["base"] / data["total_blocks"]["base"]
    frm, to = data["range"]

    fig, ax = style.figure(
        1, 1, (9.5, 5.2),
        "Block execution time — steady state",
        f"mean wall-clock per block, importer noise removed · blocks {frm:,}–{to:,}",
    )

    # shading between the arms, interpolated over each arm's kept points
    joined = {
        arm: (
            np.concatenate([s["blocks"] for s in data[arm]["segments"]]),
            np.concatenate([s["ms"] for s in data[arm]["segments"]]),
        )
        for arm in ("base", "empty")
    }
    grid = np.linspace(1, total, 400)
    base_i = np.interp(grid, *joined["base"])
    empty_i = np.interp(grid, *joined["empty"])
    ax.fill_between(grid, empty_i, base_i, where=base_i >= empty_i,
                    color=style.SAVED, alpha=0.14, linewidth=0)

    # each segment its own line, so the dropped windows read as gaps
    for arm, color in (("base", style.INK), ("empty", style.SAVED)):
        for seg in data[arm]["segments"]:
            ax.plot(seg["blocks"], seg["ms"], color=color, linewidth=1.8)

    for avg, color, label, dy in (
        (base_ms, style.INK, "BAL", 8),
        (empty_ms, style.SAVED, "BAL + void bitmap", -8),
    ):
        ax.axhline(avg, color=color, linewidth=1.0, linestyle=(0, (2, 3)), alpha=0.6)
        ax.annotate(f"{label} · avg {avg:.2f} ms", xy=(1.0, avg),
                    xycoords=("axes fraction", "data"), xytext=(8, dy),
                    textcoords="offset points", va="center",
                    fontsize=10, fontweight=600, color=color)

    style.badge(ax, 0.86, 0.90, f"saves {saved:.2f} ms/block · {saved / base_ms:.1%}",
                style.SAVED, style.SAVED_TINT, fontsize=12.5, transform=ax.transAxes)

    ax.set_ylabel("mean execution time (ms)")
    ax.set_xlim(0, total)
    ax.set_ylim(bottom=0)
    style.tidy(ax)
    style.drop_x_zero(ax)

    fig.subplots_adjust(top=0.80, bottom=0.13, left=0.07, right=0.82)
    style.caption(fig, "warmup and batch handoffs are replay blips a production node "
                       f"never sees; {pct:.1%} of blocks dropped")
    return style.save(fig, outdir, "block-processing-clean.png")
