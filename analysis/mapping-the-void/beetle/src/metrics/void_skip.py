"""What the marker reclaims — the same void read, answered from the BAL.

Companion to cost_of_void: that chart prices the void read, this one shows the
price collapsing once the BAL carries the void bit and the reader skips the
disk descent entirely. Two panels, accounts and storage; the ×N badge is how
much cheaper the answered-from-bitmap read is.

collect() pulls the Timer A means from InfluxDB (state/read/.../duration) for
void reads on both arms: host=BAL-base pays the descent, host=BAL-empty skips.
"""

from pathlib import Path

from metrics import influx, style


def collect(exports: dict[str, Path], endpoint: str) -> dict:
    def bars(kind: str) -> dict:
        m = f"state/read/{kind}/empty/duration.timer"
        return {
            "void_us": influx.mean_ns(endpoint, m, "BAL-base") / 1e3,
            "skip_us": influx.mean_ns(endpoint, m, "BAL-empty") / 1e3,
        }

    return {"account": bars("account"), "storage": bars("storage")}


def _us(v: float) -> str:
    return f"{v:.2f} µs" if v < 1 else f"{v:.1f} µs"


def _panel(ax, title: str, d: dict) -> None:
    void, skip = d["void_us"], d["skip_us"]
    ax.bar([0, 1], [void, skip], width=0.62,
           color=[style.VOID, style.SAVED], edgecolor="none")
    for x, v in ((0, void), (1, skip)):
        ax.text(x, v + void * 0.02, _us(v), ha="center", va="bottom",
                fontsize=11, fontweight=600, color=style.INK)

    style.badge(ax, 1, void * 0.57, f"{void / skip:.0f}× cheaper",
                style.SAVED, style.SAVED_TINT)

    ax.set_title(title, loc="left", fontsize=12, fontweight=600, color=style.INK)
    ax.set_xticks([0, 1], ["BAL", "BAL + void bitmap"])
    ax.tick_params(axis="x", labelsize=11)
    for tick in ax.get_xticklabels():
        tick.set_color(style.INK)
        tick.set_fontweight(500)
    ax.set_ylabel("mean read latency (µs)")
    ax.set_ylim(0, void * 1.22)
    ax.margins(x=0.14)
    style.tidy(ax)


def render(data: dict, outdir: Path) -> Path:
    frm, to = data["range"]
    fig, axes = style.figure(
        1, 2, (9.5, 5.2),
        "Skipping the void",
        f"void-read latency, with and without the void bitmap · blocks {frm}–{to}",
    )
    _panel(axes[0], "Account", data["account"])
    _panel(axes[1], "Storage slot", data["storage"])
    fig.subplots_adjust(top=0.78, bottom=0.16, left=0.08, right=0.97, wspace=0.28)
    style.caption(fig, "The void bitmap avoids the costly disk read entirely.")
    return style.save(fig, outdir, "void-skip.png")
