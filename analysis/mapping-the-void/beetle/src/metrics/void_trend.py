"""Void vs total accessed across the whole block range, as a stacked area.

Two panels stacked — accounts on top, storage slots below. For each block the
red band is items that were void (non-existent account / zero slot) at block
start and the grey band on top is items that existed; together they reach the
total the block accessed. A dashed line marks the range's average void count,
so bursts (airdrops, mints) stand out against the baseline.

collect() decodes the empty arm's export (the only one carrying the void bits)
into per-block arrays; render() draws them, so the image regenerates from the
stats json alone.
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


def collect(exports: dict[str, Path], endpoint: str) -> dict:
    export = exports.get("empty")
    if export is None:
        raise ValueError("void_trend needs the empty arm's export")
    blocks = sidecar.decode(export)
    return {
        "numbers": [b.number for b in blocks],
        "account_void": [b.void_accounts for b in blocks],
        "account_total": [b.accounts for b in blocks],
        "slot_void": [b.void_slots for b in blocks],
        "slot_total": [b.slots for b in blocks],
    }


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


def render(data: dict, outdir: Path) -> Path:
    nums = data["numbers"]
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    _panel(axes[0], nums, data["account_void"], data["account_total"], "Accounts")
    _panel(axes[1], nums, data["slot_void"], data["slot_total"], "Storage slots")
    axes[1].set_xlabel("block")

    span = f"blocks {nums[0]}–{nums[-1]}"
    fig.suptitle(f"Void vs total accessed — {span}", x=0.02, ha="left",
                 fontsize=14, fontweight="bold")
    fig.legend(
        handles=[Patch(facecolor=_VOID, label="void (skippable read)"),
                 Patch(facecolor=_EXISTS, label="existed (read paid)")],
        loc="lower center", ncol=2, frameon=False, fontsize=10,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))

    out = Path(outdir) / "void-trend.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="png", dpi=_DPI, bbox_inches="tight")
    plt.close(fig)
    return out
