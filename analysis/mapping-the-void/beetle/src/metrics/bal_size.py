"""What void-marking costs on the wire — average BAL size, both arms.

The baseline arm ships the BAL; the void-marked arm ships the same BAL with
two void bitmaps appended, so its every block is a little larger. This metric
prices that, raw and snappy-compressed, as the mean bytes a block's BAL costs
on each arm and the increase the bitmaps add over the baseline.

The bytes are measured exactly as geth meters them during `export --with-bal`:
the raw figure is the BAL RLP payload length (`chain/bal/size`), the compressed
figure is its snappy block-format size (`chain/bal/size/compressed`) — so the
numbers here cross-check geth's own `avg BAL size` stdout line. Both arms are
read straight off their exports; nothing is queried.

render() lays it out as a small table
"""

from pathlib import Path

import sidecar
from metrics import style


def _arm(export: Path) -> dict:
    blocks = sidecar.sizes(export)
    n = len(blocks)
    raw = sum(b.raw for b in blocks) / n
    comp = sum(b.compressed for b in blocks) / n
    return {"blocks": n, "raw": raw, "compressed": comp, "ratio": raw / comp}


def collect(exports: dict[str, Path], endpoint: str) -> dict:
    base, empty = exports.get("base"), exports.get("empty")
    if base is None or empty is None:
        raise ValueError("bal_size needs both the base and empty arm exports")
    b, e = _arm(base), _arm(empty)
    return {
        "base": b,
        "empty": e,
        "delta": {
            "raw": e["raw"] - b["raw"],
            "raw_pct": (e["raw"] - b["raw"]) / b["raw"],
            "compressed": e["compressed"] - b["compressed"],
            "compressed_pct": (e["compressed"] - b["compressed"]) / b["compressed"],
        },
    }


def _kib(b: float) -> str:
    return f"{b / 1024:.2f} KiB"


def render(data: dict, outdir: Path) -> Path:
    base, empty, delta = data["base"], data["empty"], data["delta"]
    rows = [
        ("raw", base["raw"], empty["raw"], delta["raw"], delta["raw_pct"]),
        (
            "snappy",
            base["compressed"],
            empty["compressed"],
            delta["compressed"],
            delta["compressed_pct"],
        ),
    ]
    headers = ["", "baseline", "void-marked", "increase"]

    fig, ax = style.figure(
        1,
        1,
        (8.5, 3.2),
        "Size of void marked BAL",
        "",
    )
    ax.axis("off")

    xs = [0.02, 0.40, 0.64, 0.90]  # column anchors: label left, figures right
    y_head = 0.80
    for x, head, align in zip(xs, headers, ("left", "right", "right", "right")):
        ax.text(
            x,
            y_head,
            head,
            ha=align,
            va="center",
            transform=ax.transAxes,
            fontsize=11,
            fontweight=600,
            color=style.MUTED,
        )
    ax.plot(
        [0.02, 0.90],
        [0.70, 0.70],
        transform=ax.transAxes,
        color=style.FAINT,
        linewidth=1.2,
    )

    for i, (label, b, e, incr, pct) in enumerate(rows):
        y = 0.52 - i * 0.20
        ax.text(
            xs[0],
            y,
            label,
            ha="left",
            va="center",
            transform=ax.transAxes,
            fontsize=12,
            fontweight=600,
            color=style.INK,
        )
        ax.text(
            xs[1],
            y,
            _kib(b),
            ha="right",
            va="center",
            transform=ax.transAxes,
            fontsize=12,
            color=style.INK,
        )
        ax.text(
            xs[2],
            y,
            _kib(e),
            ha="right",
            va="center",
            transform=ax.transAxes,
            fontsize=12,
            color=style.INK,
        )
        ax.text(
            xs[3],
            y,
            f"+{pct:.1%} ({incr:.0f} B)",
            ha="right",
            va="center",
            transform=ax.transAxes,
            fontsize=12,
            fontweight=600,
            color=style.VOID,
        )

    fig.subplots_adjust(top=0.82, bottom=0.05, left=0.04, right=0.97)
    return style.save(fig, outdir, "bal-size.png")
