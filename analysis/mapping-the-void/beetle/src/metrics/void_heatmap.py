"""Void bitmap of a single, representative block, drawn.

Two panels — accounts and storage slots. One cell per item the block accessed,
in BAL order, read left to right, top to bottom; the cell is red if that item
was void at block start (a non-existent account / a zero slot — a disk read
the BAL could skip) and grey if it existed. This is the block's void bitmap
made visible.

The block shown is the median by total items accessed — a typical-sized block,
not a cherry-picked spike. collect() decodes the empty arm's export and keeps
that one block's bitmaps; render() draws them from the stats json.
"""

from pathlib import Path

import numpy as np
from matplotlib.colors import ListedColormap

import sidecar
from metrics import style

_CMAP = ListedColormap([style.EXISTS, style.VOID])


def collect(exports: dict[str, Path], endpoint: str) -> dict:
    export = exports.get("empty")
    if export is None:
        raise ValueError("void_heatmap needs the empty arm's export")
    blocks = sidecar.decode(export)
    ordered = sorted(blocks, key=lambda b: b.accounts + b.slots)
    median = ordered[len(ordered) // 2]
    return {
        "number": median.number,
        "account_void": median.account_void,
        "slot_void": median.slot_void,
    }


def _grid(flags: list[bool]) -> np.ndarray:
    """Near-square grid of 0/1, NaN-padded to fill the rectangle."""
    cols = max(int(len(flags) ** 0.5 + 0.5), 1)
    rows = (len(flags) + cols - 1) // cols
    grid = np.full(rows * cols, np.nan)
    grid[: len(flags)] = flags
    return grid.reshape(rows, cols)


def _draw(ax, flags: list[bool], label: str):
    grid = _grid(flags)
    ax.pcolormesh(grid, cmap=_CMAP, vmin=0, vmax=1,
                  edgecolors="white", linewidth=1.4)
    void = sum(flags)
    ax.set_title(label, loc="left", fontsize=12, fontweight=600, color=style.INK)
    ax.set_title(f"{void} of {len(flags)} void · {void / len(flags):.0%}",
                 loc="right", fontsize=10, fontweight=500, color=style.MUTED)
    ax.set_aspect("equal")
    ax.set_anchor("N")  # hang both grids from the same top line
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines[:].set_visible(False)


def render(data: dict, outdir: Path) -> Path:
    acct, slots = data["account_void"], data["slot_void"]
    fig, axes = style.figure(
        1, 2, (10, 6),
        f"The void — block {data['number']}",
        "one cell per item the block accessed, in BAL order, read left to right",
        width_ratios=[_grid(acct).shape[1], _grid(slots).shape[1]],
    )
    _draw(axes[0], acct, "Accounts")
    _draw(axes[1], slots, "Storage slots")

    fig.subplots_adjust(top=0.80, bottom=0.10, left=0.04, right=0.96, wspace=0.14)
    style.caption(fig, "red — void (skippable read)   ·   grey — existed (read paid)")
    return style.save(fig, outdir, "void-heatmap.png")
