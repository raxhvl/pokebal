"""Void bitmap of a single, representative block, drawn.

Two panels — accounts and storage slots. One cell per item the block accessed,
in BAL order; the cell is red if that item was void at block start (a
non-existent account / a zero slot — a disk read the BAL could skip) and grey
if it existed. This is the block's void bitmap made visible.

The block shown is the median by total items accessed — a typical-sized block,
not a cherry-picked spike. Reads the empty arm's export (the only one carrying
the void bits).
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: no display, just write files
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

import sidecar

_DPI = 200
_EXISTS = "#d9d9d9"  # grey: item existed — read still paid
_VOID = "#d73027"    # red: item was void — the skippable read
_CMAP = ListedColormap([_EXISTS, _VOID])


def _median_block(blocks: list[sidecar.BlockVoid]) -> sidecar.BlockVoid:
    ordered = sorted(blocks, key=lambda b: b.accounts + b.slots)
    return ordered[len(ordered) // 2]


def _grid(flags: list[bool]) -> np.ndarray:
    """Near-square grid of 0/1, NaN-padded to fill the rectangle."""
    cols = max(int(len(flags) ** 0.5 + 0.5), 1)
    rows = (len(flags) + cols - 1) // cols
    grid = np.full(rows * cols, np.nan)
    grid[: len(flags)] = flags
    return grid.reshape(rows, cols)


def _draw(ax, flags: list[bool], label: str):
    grid = _grid(flags)
    ax.pcolormesh(grid, cmap=_CMAP, vmin=0, vmax=1, edgecolors="white", linewidth=1.0)
    void = sum(flags)
    ax.set_title(
        f"{label} — {void} of {len(flags)} void ({void / len(flags):.0%})",
        loc="left", fontsize=11, fontweight="bold",
    )
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def render(block: sidecar.BlockVoid, out: Path) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(11, 6))
    _draw(axes[0], block.account_void, "Accounts")
    _draw(axes[1], block.slot_void, "Storage slots")

    fig.suptitle(f"The void — block {block.number}", x=0.02, ha="left",
                 fontsize=14, fontweight="bold")
    fig.legend(
        handles=[Patch(facecolor=_VOID, label="void (skippable read)"),
                 Patch(facecolor=_EXISTS, label="existed (read paid)")],
        loc="lower center", ncol=2, frameon=False, fontsize=10,
    )
    fig.subplots_adjust(bottom=0.12)

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="png", dpi=_DPI, bbox_inches="tight")
    plt.close(fig)
    return out


def run(exports: dict[str, Path], outdir: Path) -> Path:
    export = exports.get("empty")
    if export is None:
        raise ValueError("void_heatmap needs the empty arm's export")
    blocks = sidecar.decode(export)
    return render(_median_block(blocks), Path(outdir) / "void-heatmap.png")
