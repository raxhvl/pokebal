"""What the empty-BAL reclaims per block — the gain, in wall-clock.

A block spends real time proving absence: for every empty account/slot it reads,
it walks to disk and comes back empty-handed. This sums that time per block and
shows it before and after the empty-BAL: two stacked bars (no BAL / with BAL),
each split into the account and storage share, with the reclaimed delta called
out. The drop between the bars is the metric that matters to a validator.

Per-read latency comes from the Timer A meters in InfluxDB (tagged host=BAL-base
= un-skipped, host=BAL-empty = skip active); the per-block count comes from the
replayed range in the export filename. Reclaimed/block = skips/block × the drop
in mean read latency — mean is used deliberately: it's the only statistic that
aggregates to a total (count × mean = summed time), which a percentile can't.
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
_ACCOUNT = "#4575b4"  # blue: account-read share
_STORAGE = "#91bfdb"  # light blue: storage-read share
_SAVED = "#1a9850"    # green: the reclaimed delta
_DB = "geth"


def _query(endpoint: str, agg: str, field: str, measurement: str, host: str) -> float:
    q = f'SELECT {agg}("{field}") FROM "geth.{measurement}" WHERE "host"=\'{host}\''
    url = endpoint + "/query?" + urllib.parse.urlencode({"db": _DB, "q": q})
    with urllib.request.urlopen(url, timeout=15) as r:
        series = json.load(r)["results"][0].get("series")
    return (series[0]["values"][0][1] or 0) if series else 0.0


def _blocks(exports: dict[str, Path]) -> int:
    # replay-<arm>-<from>-<to>.rlp -> block count of the replayed range.
    stem = next(iter(exports.values())).stem
    frm, to = (int(x) for x in stem.split("-")[-2:])
    return to - frm + 1


def _per_block_ms(endpoint: str, kind: str, blocks: int) -> tuple[float, float]:
    """(no-BAL, with-BAL) ms/block spent in this kind's empty reads."""
    m = f"state/read/{kind}/empty/duration.timer"
    skips = _query(endpoint, "sum", "count", m, "BAL-base") / blocks
    base = _query(endpoint, "mean", "mean", m, "BAL-base")
    withbal = _query(endpoint, "mean", "mean", m, "BAL-empty")
    return skips * base / 1e6, skips * withbal / 1e6


def render(endpoint: str, blocks: int, out: Path) -> Path:
    acct = _per_block_ms(endpoint, "account", blocks)
    stor = _per_block_ms(endpoint, "storage", blocks)
    no_bal = (acct[0], stor[0])   # (account, storage) with no BAL
    with_bal = (acct[1], stor[1])
    totals = (sum(no_bal), sum(with_bal))

    fig, ax = plt.subplots(figsize=(7, 6))
    x = ["no BAL", "with BAL"]
    account = [no_bal[0], with_bal[0]]
    storage = [no_bal[1], with_bal[1]]
    ax.bar(x, account, color=_ACCOUNT, label="account reads")
    ax.bar(x, storage, bottom=account, color=_STORAGE, label="storage reads")

    for i, total in enumerate(totals):
        ax.text(i, total, f"{total:.2f} ms", ha="center", va="bottom",
                fontsize=11, fontweight="bold")

    # Reclaimed delta, drawn in the gap between the bars so it clips neither label.
    reclaimed = totals[0] - totals[1]
    ax.annotate(
        "", xy=(0.5, totals[1]), xytext=(0.5, totals[0]),
        arrowprops=dict(arrowstyle="<->", color=_SAVED, lw=2),
    )
    ax.text(0.58, (totals[0] + totals[1]) / 2, f"−{reclaimed:.2f} ms/block\nreclaimed",
            color=_SAVED, fontsize=11, fontweight="bold", va="center")

    ax.set_title(f"Block processing — time spent proving absence  ({blocks} blocks)",
                 loc="left", fontsize=12, fontweight="bold")
    ax.set_ylabel("empty-read time per block (ms)")
    ax.margins(y=0.15)
    ax.set_ylim(bottom=0)
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="png", dpi=_DPI, bbox_inches="tight")
    plt.close(fig)
    return out


def run(exports: dict[str, Path], outdir: Path) -> Path:
    endpoint = config.require("INFLUX_ENDPOINT")
    return render(endpoint, _blocks(exports), Path(outdir) / "block-processing.png")
