"""The cost of a void read — slower than a real read, and erased by the empty-BAL.

Two panels, accounts and storage. Each shows three read latencies side by side:
a read that found data, a read that proved absence with no BAL, and that same
void read once the empty-BAL lets the client answer it from a bitmap instead of
walking to disk. The first gap is the price of proving absence; the second is
what the marker reclaims.

Unlike the void_* metrics, latency isn't in the export — it comes from the
Timer A meters in InfluxDB (state/read/.../duration), tagged per arm
(host=BAL-base = un-skipped truth, host=BAL-empty = skip active).
"""

import json
import urllib.parse
import urllib.request
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: no display, just write files
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

import config

_DPI = 200
_EXIST = "#d9d9d9"  # grey: read found data
_VOID = "#d73027"   # red: read proved absence, all the way to disk
_SAVED = "#1a9850"  # green: void answered from the BAL, no disk trip
_DB = "geth"


def _mean_us(endpoint: str, measurement: str, host: str) -> float:
    q = f'SELECT mean("mean") FROM "geth.{measurement}" WHERE "host"=\'{host}\''
    url = endpoint + "/query?" + urllib.parse.urlencode({"db": _DB, "q": q})
    with urllib.request.urlopen(url, timeout=15) as r:
        series = json.load(r)["results"][0].get("series")
    ns = series[0]["values"][0][1] if series else None
    return (ns or 0) / 1000.0


def _bars(endpoint: str, kind: str) -> list[float]:
    exist = _mean_us(endpoint, f"state/read/{kind}/exist/duration.timer", "BAL-base")
    void = _mean_us(endpoint, f"state/read/{kind}/empty/duration.timer", "BAL-base")
    saved = _mean_us(endpoint, f"state/read/{kind}/empty/duration.timer", "BAL-empty")
    return [exist, void, saved]


def _panel(ax, kind: str, values: list[float]) -> None:
    bars = ax.bar(["exist", "void", "void + BAL"], values,
                  color=[_EXIST, _VOID, _SAVED], edgecolor="none")
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v, f"{v:.1f} µs",
                ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax.set_title(kind.capitalize(), loc="left", fontsize=11, fontweight="bold")
    ax.set_ylabel("read latency (µs)")
    ax.margins(y=0.18)
    ax.set_ylim(bottom=0)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def render(endpoint: str, out: Path) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(9, 5))
    _panel(axes[0], "account", _bars(endpoint, "account"))
    _panel(axes[1], "storage", _bars(endpoint, "storage"))

    fig.suptitle("The cost of a void read", x=0.02, ha="left",
                 fontsize=14, fontweight="bold")
    fig.legend(
        handles=[
            Patch(facecolor=_EXIST, label="exist — found data"),
            Patch(facecolor=_VOID, label="void — proved absence (hits disk)"),
            Patch(facecolor=_SAVED, label="void + BAL — skipped"),
        ],
        loc="lower center", ncol=3, frameon=False, fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="png", dpi=_DPI, bbox_inches="tight")
    plt.close(fig)
    return out


def run(exports: dict[str, Path], outdir: Path) -> Path:
    # exports unused: latency lives in InfluxDB, not the void bitmaps.
    endpoint = config.require("INFLUX_ENDPOINT")
    return render(endpoint, Path(outdir) / "cost-of-void.png")
