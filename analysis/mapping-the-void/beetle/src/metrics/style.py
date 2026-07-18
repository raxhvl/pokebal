"""Shared look for every beetle chart.

One place for the design system: Inter (bundled, loaded from ./fonts), a white
canvas, no chart junk (no boxes, no top/right spines, faint y-grid only), a
big left-aligned title with a muted subtitle, and a semantic palette that is
constant across charts — red is always a void read, grey is always a read
that found data, green is always time given back by the marker, ink is the
baseline arm.

Import the module and call figure(); rcParams are configured on import.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: no display, just write files
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter

# palette — semantic, keep it religiously consistent across charts
VOID = "#ef4444"        # red: a void read
VOID_TINT = "#fee2e2"   # red wash: badge background
EXISTS = "#d4d4d4"      # grey: a read that found data
SAVED = "#10b981"       # green: reclaimed by the marker
SAVED_TINT = "#d1fae5"  # green wash: badge background
INK = "#0a0a0a"         # near-black: text, baseline arm
MUTED = "#8f8f8f"       # secondary text
FAINT = "#ececec"       # gridlines, hairlines

DPI = 200

for _ttf in (Path(__file__).parent / "fonts").glob("*.ttf"):
    font_manager.fontManager.addfont(str(_ttf))

plt.rcParams.update({
    "font.family": "Inter",
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": FAINT,
    "axes.linewidth": 1.0,
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "text.color": INK,
})


def figure(nrows: int, ncols: int, size: tuple[float, float],
           title: str, subtitle: str, **subplot_kw):
    """Figure with the house header; returns (fig, axes) like plt.subplots."""
    fig, axes = plt.subplots(nrows, ncols, figsize=size, **subplot_kw)
    fig.text(0.02, 0.985, title, ha="left", va="top",
             fontsize=17, fontweight=700, color=INK)
    fig.text(0.02, 0.925, subtitle, ha="left", va="top",
             fontsize=10.5, fontweight=500, color=MUTED)
    return fig, axes


def drop_x_zero(ax) -> None:
    """Blank the x-axis 0 so it doesn't collide with the y-axis 0 at the origin."""
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: "" if v == 0 else f"{v:g}"))


def tidy(ax, *, grid: bool = True) -> None:
    """Strip the box; keep a hairline bottom spine and a faint y-grid."""
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    if grid:
        ax.grid(axis="y", color=FAINT, linewidth=1.0)
        ax.set_axisbelow(True)
    ax.tick_params(length=0)


def badge(ax, x, y, text: str, color: str, tint: str, *,
          fontsize: float = 11.5, **kw) -> None:
    """Pill badge — bold colored text on a soft wash of the same hue."""
    ax.text(x, y, text, ha="center", va="center",
            fontsize=fontsize, fontweight=700, color=color,
            bbox=dict(boxstyle="round,pad=0.55,rounding_size=0.9",
                      facecolor=tint, edgecolor="none"), **kw)


def caption(fig, text: str, *, y: float = 0.02) -> None:
    """Muted one-liner centered along the bottom — replaces boxed legends."""
    fig.text(0.5, y, text, ha="center", va="bottom",
             fontsize=9.5, fontweight=500, color=MUTED)


def save(fig, outdir: Path, name: str) -> Path:
    out = Path(outdir) / name
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="png", dpi=DPI, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    return out
