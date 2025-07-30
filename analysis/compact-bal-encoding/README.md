# Compact BAL Encoding Analysis

This repository contains analysis of a compact Block Access List (BAL) encoding scheme that reduces size overhead by eliminating duplicate transaction indices and null field overhead.

## Overview

The analysis demonstrates how a structured approach to encoding block access lists can achieve significant size reductions while maintaining full information fidelity. See [summary.md](./summary.md) for detailed findings.

## Project Structure

```
├── src/
│   ├── benchmark.ts          # Main analysis script
│   ├── data/baseline/        # SSZ-encoded baseline BAL files
│   └── schemas/baseline.ts   # SSZ schema definitions
├── summary.md                # Detailed analysis results
└── package.json             # Dependencies and scripts
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

## Running the Benchmark

Execute the analysis on the provided dataset:

```bash
npm run benchmark
```

This will:
- Process all `.ssz` files in `src/data/baseline/`
- Analyze transaction access coverage patterns
- Generate statistics on field usage across transactions
- Output results showing the distribution of fields touched per transaction

## Dataset

The analysis uses 50 Ethereum blocks from range `20615532` to `20616032` (interval of 10), encoded as SSZ baseline Block Access Lists.

## Requirements

- Node.js (v16 or higher)
- TypeScript support via tsx