#!/usr/bin/env python3
"""Benchmarking script for different BlockAccessList serialization methods."""

import json
import time
import sys
from pathlib import Path
from typing import Callable, Dict, Any
from statistics import mean, stdev


from pokebal.bal.types import BlockAccessList
from pokebal.bal.serialization_v2 import to_ssz_v2
from pokebal.common.test_utils import normalize_to_bytes


def load_test_data(fixture_path: str) -> BlockAccessList:
    """Load BlockAccessList from JSON fixture."""
    with open(fixture_path, "r") as f:
        data = json.load(f)
        normalized_data = normalize_to_bytes(data)
    return BlockAccessList(**normalized_data)


def benchmark_single_file(fixture_path: Path):
    print(f"\n📁 Processing: {fixture_path.name}")

    try:
        bal = load_test_data(str(fixture_path))

        # Define serializers
        serializers = [
            (lambda b: b.serialize(), "Default (to_ssz)"),
            (lambda b: b.serialize(serializer=to_ssz_v2), "V2 (to_ssz_v2)"),
        ]

        # Single execution timing
        results = []
        for serializer_func, name in serializers:
            try:
                start_time = time.perf_counter()
                result = serializer_func(bal)
                end_time = time.perf_counter()

                execution_time = (end_time - start_time) * 1000  # ms

                metrics = {
                    "fixture": fixture_path.name,
                    "serializer": name,
                    "execution_time_ms": round(execution_time, 4),
                    "output_size_bytes": len(result),
                }
                results.append(metrics)

                print(f"  • {name}: {execution_time:.4f} ms → {len(result):,} bytes")

            except Exception as e:
                print(f"  ❌ Error with {name}: {e}")

        return results

    except Exception as e:
        print(f"❌ Error loading {fixture_path.name}: {e}")
        return []


def print_summary(all_results: list):
    """Print simple average size and time comparison."""
    if not all_results:
        return

    # Group by serializer
    serializer_stats = {}
    for result in all_results:
        serializer = result["serializer"]
        if serializer not in serializer_stats:
            serializer_stats[serializer] = {"sizes": [], "times": []}
        serializer_stats[serializer]["sizes"].append(result["output_size_bytes"])
        serializer_stats[serializer]["times"].append(result["execution_time_ms"])

    print("\n" + "=" * 60)
    print("📊 SERIALIZATION COMPARISON")
    print("=" * 60)
    print(f"{'Serializer':<20} {'Avg Size (KB)':<15} {'Avg Time (ms)':<15}")
    print("-" * 60)

    for serializer, stats in serializer_stats.items():
        avg_size_kb = mean(stats["sizes"]) / 1024
        avg_time_ms = mean(stats["times"])
        print(f"{serializer:<20} {avg_size_kb:<15.2f} {avg_time_ms:<15.4f}")


def main():
    """Run serialization benchmarks on all BAL fixture files."""
    print("🚀 BlockAccessList Serialization Benchmark")
    print("=" * 50)

    # Find all BAL JSON fixture files
    fixtures_dir = Path(__file__).parent.parent / "tests/fixtures/bal"
    fixture_files = list(fixtures_dir.glob("*.json"))

    if not fixture_files:
        print("❌ No BAL JSON fixture files found")
        return 1

    print(f"🔍 Found {len(fixture_files)} BAL fixture file(s)")

    # Process each fixture
    all_results = []
    for fixture_path in sorted(fixture_files):
        results = benchmark_single_file(fixture_path)
        all_results.extend(results)

    # Print simple comparison
    print_summary(all_results)

    return 0


if __name__ == "__main__":
    sys.exit(main())
