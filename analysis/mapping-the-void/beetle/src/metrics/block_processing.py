"""Block execution wall-clock, with the empty-BAL and without.

Two bars — mean per-block EVM execution on the base arm (no skip) and the empty
arm (BAL skips the void reads) — and the time the marker shaves off. This is
geth's own chain/execution timer, i.e. real wall-clock: it cannot exceed the
block's actual processing time, unlike a sum of per-read latencies (which
overcounts because the BAL executor reads in parallel).

collect() reads it from InfluxDB, tagged host=BAL-base / host=BAL-empty.
"""

import json
import urllib.parse
import urllib.request
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: no display, just write files
import matplotlib.pyplot as plt

_DPI = 200
_NO_BAL = "#4575b4"  # blue: base arm, no skip
_WITH_BAL = "#1a9850"  # green: empty arm, void reads skipped
_DB = "geth"


def _exec_ms(endpoint: str, host: str) -> float:
    q = f'SELECT mean("mean") FROM "geth.chain/execution.timer" WHERE "host"=\'{host}\''
    url = endpoint + "/query?" + urllib.parse.urlencode({"db": _DB, "q": q})
    with urllib.request.urlopen(url, timeout=15) as r:
        series = json.load(r)["results"][0].get("series")
    ns = series[0]["values"][0][1] if series else None
    return (ns or 0) / 1e6


def collect(exports: dict[str, Path], endpoint: str) -> dict:
    base = _exec_ms(endpoint, "BAL-base")
    empty = _exec_ms(endpoint, "BAL-empty")
    return {"base_ms": base, "empty_ms": empty, "saved_ms": base - empty}


def render(data: dict, outdir: Path) -> Path:
    base, empty, saved = data["base_ms"], data["empty_ms"], data["saved_ms"]

    fig, ax = plt.subplots(figsize=(7, 6))
    bars = ax.bar(["no BAL", "with BAL"], [base, empty],
                  color=[_NO_BAL, _WITH_BAL], edgecolor="none")
    for bar, v in zip(bars, (base, empty)):
        ax.text(bar.get_x() + bar.get_width() / 2, v, f"{v:.2f} ms",
                ha="center", va="bottom", fontsize=11, fontweight="bold")

    ax.annotate(
        "", xy=(0.5, empty), xytext=(0.5, base),
        arrowprops=dict(arrowstyle="<->", color=_WITH_BAL, lw=2),
    )
    ax.text(0.58, (base + empty) / 2, f"−{saved:.2f} ms/block\nsaved",
            color=_WITH_BAL, fontsize=11, fontweight="bold", va="center")

    ax.set_title("Block execution time — wall-clock per block",
                 loc="left", fontsize=12, fontweight="bold")
    ax.set_ylabel("execution time per block (ms)")
    ax.margins(y=0.15)
    ax.set_ylim(bottom=0)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()

    out = Path(outdir) / "block-processing.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="png", dpi=_DPI, bbox_inches="tight")
    plt.close(fig)
    return out
