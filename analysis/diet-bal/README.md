# Diet BAL Analysis Results

> **⚠️ Experimental Work**: This analysis represents experimental research into Diet BAL optimization. The implementation may contain bugs and results should be validated before production use.

This directory contains the analysis results from converting Block Access Lists (BAL) to Diet BAL format across 50 Ethereum block files.

## Performance Summary

Comparison of BAL vs Diet BAL across 50 Ethereum blocks from the ssz data sourced from [here](https://github.com/nerolation/eth-bal-analysis/tree/ff09e99650d0085e6b8a2846777a26fc0bbdf61d/bal_raw/ssz) :

| Metric           | BAL (Uncompressed) | Diet BAL (Uncompressed) | Savings   |
| ---------------- | ------------------ | ----------------------- | --------- |
| **Average size** | 88.9 KiB           | 50.9 KiB                | **42.8%** |
| **Median size**  | 90.1 KiB           | 52.1 KiB                | **42.2%** |

| Metric           | BAL (Compressed)   | Diet BAL (Compressed)   | Savings   |
| --------         | ------------------ | ----------------------  | --------- |
| **Average size** | 53.0 KiB           | 34.4 KiB                | **35.1%** |
| **Median size**  | 53.7 KiB           | 34.9 KiB                | **35.0%** |

## Files

- `analysis_results_uncompressed.csv` - Comparison of uncompressed BAL vs Diet BAL sizes
- `analysis_results_compressed.csv` - Comparison of compressed BAL vs Diet BAL sizes
- `bal/` - Original BAL files in SSZ format
- `diet-bal/` - Converted Diet BAL files in SSZ format

## Interpreting the Results

### CSV Columns

**Uncompressed Analysis:**

- `File` - Block number SSZ file
- `BAL Size` - Original BAL file size in bytes
- `Diet BAL Size` - Converted Diet BAL file size in bytes
- `Savings` - Absolute size reduction in bytes
- `Savings %` - Percentage reduction in file size

**Compressed Analysis:**

- `BAL Compressed` - Original BAL compressed with Snappy
- `Diet Compressed` - Diet BAL compressed with Snappy
- `Compress Savings` - Absolute size reduction in bytes
- `Compress Savings %` - Percentage reduction in compressed size

## Implementation

See the full specification and background in the [Diet BAL blog post](https://raxhvl.com/ethereum/diet-bal/) and `diet.ts` file for implementation details.
