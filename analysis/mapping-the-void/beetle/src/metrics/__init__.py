"""Metrics run over a completed replay's exports.

Each metric is a module exposing `run(exports, outdir) -> Path`, where `exports`
maps arm name ("base"/"empty") to its kept export file. Register it below; the
replay tail calls `run_all`, which runs every metric and returns their artifacts.
"""

from pathlib import Path

from . import void_heatmap, void_trend

REGISTRY = {
    "void_heatmap": void_heatmap.run,
    "void_trend": void_trend.run,
}


def run_all(exports: dict[str, Path], outdir: Path) -> list[Path]:
    artifacts = []
    for name, run in REGISTRY.items():
        try:
            artifact = run(exports, Path(outdir))
        except Exception as exc:  # one bad metric shouldn't sink the rest
            print(f"metric {name}: FAILED — {exc}")
            continue
        print(f"metric {name}: wrote {artifact}")
        artifacts.append(artifact)
    return artifacts
