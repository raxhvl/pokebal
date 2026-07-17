"""Scale bench: the metrics pass over a mainnet-range export.

Not collected by a plain `pytest` run (the filename doesn't match test_*.py);
run it explicitly, from the beetle dir:

    uv run pytest tests/scale.py -s

Generates an 89k-block synthetic export via synth.write_export (~26 GB in
work/bench/, deleted again when the run ends — regenerating costs about a
minute), then runs exactly what the collectors run —
scan for the trend arrays, load for the heatmap's median block — while a
thread samples /proc/self/status. RssAnon is the number that can OOM the box
(Python heap); RssFile is just the kernel's cache of the mmapped export,
reclaimed under pressure, so it is reported but not bounded.
"""

import json
import threading
import time
from pathlib import Path

import pytest

import sidecar
import snapshot
import synth

BLOCKS = 89_000
EXPORT = snapshot.WORK / "bench" / f"synth-{BLOCKS}.rlp"


def _rss() -> tuple[int, int]:
    """(RssAnon, RssFile) in bytes, from /proc/self/status."""
    anon = file = 0
    for line in Path("/proc/self/status").read_text().splitlines():
        if line.startswith("RssAnon"):
            anon = int(line.split()[1]) * 1024
        elif line.startswith("RssFile"):
            file = int(line.split()[1]) * 1024
    return anon, file


class Sampler:
    """Samples anon/file RSS every 100 ms so a spike can't hide between
    before/after snapshots."""

    def __init__(self):
        self.samples: list[tuple[float, int, int]] = []
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        start = time.monotonic()
        while not self._stop.is_set():
            anon, file = _rss()
            self.samples.append((time.monotonic() - start, anon, file))
            self._stop.wait(0.1)

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        self._thread.join()


@pytest.fixture
def export():
    EXPORT.parent.mkdir(parents=True, exist_ok=True)
    print(f"\ngenerating {EXPORT} ({BLOCKS} blocks)...")
    synth.write_export(EXPORT, BLOCKS, progress=print)
    yield EXPORT
    EXPORT.unlink(missing_ok=True)


def test_metrics_pass_stays_flat_at_mainnet_scale(export):
    size = EXPORT.stat().st_size
    anon_before, _ = _rss()

    with Sampler() as sampler:
        started = time.monotonic()
        rows = sidecar.scan(EXPORT)
        scan_secs = time.monotonic() - started

        # what void_trend.collect keeps
        trend = {
            "numbers": [b.number for b in rows],
            "account_void": [b.void_accounts for b in rows],
            "account_total": [b.accounts for b in rows],
            "slot_void": [b.void_slots for b in rows],
            "slot_total": [b.slots for b in rows],
        }
        # what void_heatmap.collect keeps
        ordered = sorted(rows, key=lambda b: b.accounts + b.slots)
        median = sidecar.load(EXPORT, ordered[len(ordered) // 2].offset)
        wall_secs = time.monotonic() - started

    stats_bytes = len(json.dumps({
        "void_trend": trend,
        "void_heatmap": {
            "number": median.number,
            "account_void": median.account_void,
            "slot_void": median.slot_void,
        },
    }))

    peak_anon = max(a for _, a, _ in sampler.samples)
    peak_file = max(f for _, _, f in sampler.samples)
    growth = peak_anon - anon_before
    print(
        f"\n{BLOCKS} blocks / {size / 1e9:.1f} GB: "
        f"scan {scan_secs:.0f}s, total {wall_secs:.0f}s · "
        f"heap (RssAnon) peak {peak_anon / 1e6:.0f} MB (+{growth / 1e6:.0f} MB) · "
        f"mmap cache (RssFile) peak {peak_file / 1e9:.2f} GB · "
        f"stats json {stats_bytes / 1e6:.1f} MB"
    )

    # correctness at scale: every block's tallies match its construction
    assert len(rows) == BLOCKS
    for i, r in enumerate(rows):
        assert (r.accounts, r.void_accounts, r.slots, r.void_slots) == synth.expected(i), i
    assert median.number == ordered[len(ordered) // 2].number

    # the analysis must fit in a fraction of the box however big the file is
    assert growth < 512_000_000, f"heap grew {growth} bytes on a {size}-byte export"
    assert stats_bytes < 32_000_000, f"stats json would be {stats_bytes} bytes"
