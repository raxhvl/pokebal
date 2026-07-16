"""The cost of a void read — proving absence is slower than finding data.

Two panels, accounts and storage. Each compares the mean latency of a read
that found data with one that proved absence — the ×N badge is the price of
descending the full trie to confirm nothing is there. What the marker does
about it is a separate chart (void_skip); this one only establishes the cost.

collect() pulls the Timer A means from InfluxDB (state/read/.../duration) on
the base arm (host=BAL-base), where nothing is skipped.
"""

from pathlib import Path

from metrics import influx, style


def collect(exports: dict[str, Path], endpoint: str) -> dict:
    def bars(kind: str) -> dict:
        m = f"state/read/{kind}/{{}}/duration.timer"
        return {
            "exist_us": influx.mean_ns(endpoint, m.format("exist"), "BAL-base") / 1e3,
            "void_us": influx.mean_ns(endpoint, m.format("empty"), "BAL-base") / 1e3,
        }

    return {"account": bars("account"), "storage": bars("storage")}


def _us(v: float) -> str:
    return f"{v:.2f} µs" if v < 1 else f"{v:.1f} µs"


def _panel(ax, title: str, d: dict) -> None:
    exist, void = d["exist_us"], d["void_us"]
    ax.bar([0, 1], [exist, void], width=0.62,
           color=[style.EXISTS, style.VOID], edgecolor="none")
    for x, v in ((0, exist), (1, void)):
        ax.text(x, v + void * 0.02, _us(v), ha="center", va="bottom",
                fontsize=11, fontweight=600, color=style.INK)

    # anchor line at the exist level; the gap above it is the price of absence
    ax.axhline(exist, color=style.MUTED, linewidth=1.0, linestyle=(0, (2, 3)))
    style.badge(ax, 1, void * 1.22, f"{void / exist:.1f}× slower",
                style.VOID, style.VOID_TINT)

    ax.set_title(title, loc="left", fontsize=12, fontweight=600, color=style.INK)
    ax.set_xticks([0, 1], ["exist", "void"])
    ax.tick_params(axis="x", labelsize=11)
    for tick in ax.get_xticklabels():
        tick.set_color(style.INK)
        tick.set_fontweight(500)
    ax.set_ylabel("mean read latency (µs)")
    ax.set_ylim(0, void * 1.38)
    ax.margins(x=0.14)
    style.tidy(ax)


def render(data: dict, outdir: Path) -> Path:
    fig, axes = style.figure(
        1, 2, (9.5, 5.2),
        "The cost of a void read",
        "mean state-read latency by outcome — a void read walks the whole trie to prove absence",
    )
    _panel(axes[0], "Account", data["account"])
    _panel(axes[1], "Storage slot", data["storage"])
    fig.subplots_adjust(top=0.78, bottom=0.16, left=0.08, right=0.97, wspace=0.28)
    style.caption(fig, "exist — the read found data   ·   "
                       "void — nothing there, and proving it costs the full descent")
    return style.save(fig, outdir, "cost-of-void.png")
