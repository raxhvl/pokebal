"""Void vs total accessed across the whole block range.

Two panels — accounts on top, storage slots below. Per block, the red band is
items that were void at block start, the grey band on top is items that
existed; both are smoothed with a rolling mean so the shape reads instead of
the noise (a faint line traces the raw per-block total). Each band carries its
own average count and share of reads, labelled in place — a share line was
tried and dropped: totals are near-constant, so it just re-traced the stack
boundary. The flatness of the bands is the point: the void is a constant
feature of the workload, not bursts.

collect() streams the empty arm's export (the only one carrying the void bits)
into per-block arrays; render() draws them, so the image regenerates from the
stats json alone.
"""

from pathlib import Path

import numpy as np

import sidecar
from metrics import style

_WINDOW = 25  # blocks; ~2.5% of the range


def collect(exports: dict[str, Path], endpoint: str) -> dict:
    export = exports.get("empty")
    if export is None:
        raise ValueError("void_trend needs the empty arm's export")
    blocks = sidecar.scan(export)
    return {
        "numbers": [b.number for b in blocks],
        "account_void": [b.void_accounts for b in blocks],
        "account_total": [b.accounts for b in blocks],
        "slot_void": [b.void_slots for b in blocks],
        "slot_total": [b.slots for b in blocks],
    }


def _smooth(values) -> np.ndarray:
    kernel = np.ones(_WINDOW) / _WINDOW
    return np.convolve(values, kernel, mode="valid")


def _panel(ax, nums, void, total, title):
    nums, void, total = np.asarray(nums), np.asarray(void), np.asarray(total)
    mid = nums[_WINDOW // 2 : -(_WINDOW // 2)]  # x for the rolling window
    void_s, total_s = _smooth(void), _smooth(total)

    ax.stackplot(mid, void_s, total_s - void_s,
                 colors=[style.VOID, style.EXISTS], edgecolor="none")
    ax.plot(nums, total, color=style.MUTED, linewidth=0.6, alpha=0.45)

    # each band labelled in place: average count plus its share of reads
    center = nums[0] + (nums[-1] - nums[0]) / 2
    void_avg, exist_avg = void.mean(), (total - void).mean()
    pct = void.sum() / total.sum()
    ax.text(center, void_avg / 2,
            f"void — avg {void_avg:.0f}/block · {pct:.0%} of reads",
            ha="center", va="center", fontsize=11, fontweight=700, color="white")
    if exist_avg > void_avg / 3:  # label the grey band only if it can hold text
        ax.text(center, void_avg + exist_avg / 2,
                f"present — avg {exist_avg:.0f}/block · {1 - pct:.0%}",
                ha="center", va="center", fontsize=10, fontweight=600,
                color=style.INK)

    ax.set_title(title, loc="left", fontsize=12, fontweight=600, color=style.INK)
    ax.set_ylabel("items / block")
    ax.set_xlim(nums[0], nums[-1])
    ax.set_ylim(bottom=0)
    style.tidy(ax)


def render(data: dict, outdir: Path) -> Path:
    nums = data["numbers"]
    fig, axes = style.figure(
        2, 1, (10, 6.6),
        "Void vs total accessed",
        f"per-block reads, {_WINDOW}-block rolling mean · blocks {nums[0]}–{nums[-1]}",
        sharex=True,
    )
    _panel(axes[0], nums, data["account_void"], data["account_total"], "Accounts")
    _panel(axes[1], nums, data["slot_void"], data["slot_total"], "Storage slots")

    fig.subplots_adjust(top=0.83, bottom=0.15, left=0.07, right=0.97, hspace=0.42)
    style.caption(fig, "the void is a steady share of every block, not occasional bursts")
    return style.save(fig, outdir, "void-trend.png")
