"""Void vs total accessed across the whole block range, as a stacked area.

Two panels stacked — accounts on top, storage slots below. For each block the
red band is items that were void (non-existent account / zero slot) at block
start and the grey band on top is items that existed; together they reach the
total the block accessed. A dashed line marks the range's average void count,
so bursts (airdrops, mints) stand out against the baseline.

Reads the empty arm's export (the only one carrying the void bits).
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: no display, just write files
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

import sidecar

_DPI = 200
_VOID = "#d73027"    # red: void — the skippable reads
_EXISTS = "#d9d9d9"  # grey: existed — reads still paid
_MEAN = "#57606a"    # average line


def _panel(ax, nums, void, total, title):
    existing = [t - v for t, v in zip(total, void)]
    ax.stackplot(nums, void, existing, colors=[_VOID, _EXISTS], edgecolor="none")
    avg = sum(void) / len(void)
    ax.axhline(avg, color=_MEAN, linestyle="--", linewidth=1.2)
    ax.text(nums[-1], avg, f" avg {avg:.0f}", color=_MEAN, va="center",
            fontsize=9, fontweight="bold")
    ax.set_title(title, loc="left", fontsize=11, fontweight="bold")
    ax.set_ylabel("items / block")
    ax.margins(x=0.01, y=0)
    ax.set_ylim(bottom=0)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def render(blocks: list[sidecar.BlockVoid], out: Path) -> Path:
    nums = [b.number for b in blocks]
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    _panel(axes[0], nums, [b.void_accounts for b in blocks],
           [b.accounts for b in blocks], "Accounts")
    _panel(axes[1], nums, [b.void_slots for b in blocks],
           [b.slots for b in blocks], "Storage slots")
    axes[1].set_xlabel("block")

    span = f"blocks {blocks[0].number}–{blocks[-1].number}"
    fig.suptitle(f"Void vs total accessed — {span}", x=0.02, ha="left",
                 fontsize=14, fontweight="bold")
    fig.legend(
        handles=[Patch(facecolor=_VOID, label="void (skippable read)"),
                 Patch(facecolor=_EXISTS, label="existed (read paid)")],
        loc="lower center", ncol=2, frameon=False, fontsize=10,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="png", dpi=_DPI, bbox_inches="tight")
    plt.close(fig)
    return out


def run(exports: dict[str, Path], outdir: Path) -> Path:
    export = exports.get("empty")
    if export is None:
        raise ValueError("void_trend needs the empty arm's export")
    blocks = sidecar.decode(export)
    return render(blocks, Path(outdir) / "void-trend.png")
