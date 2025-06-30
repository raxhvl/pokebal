# PokeBAL

A Python implementation of [EIP-7928](https://eips.ethereum.org/EIPS/eip-7928) to help test client implementations.

> [!Note]
> EIP-7928 version: [35732ba](https://github.com/ethereum/EIPs/blob/35732baa14cfea785d9c58d5f18033392b7ed886/EIPS/eip-7928.md)

## Quick Start

```python
from bal.builder import from_execution_trace
from rpc.client import RPCClient
from rpc.methods import EthereumMethods
from rpc.transport import HTTPTransport

# Connect to Ethereum node
client = RPCClient(transport=HTTPTransport("http://localhost:8545"))
eth = EthereumMethods(client)

# Get trace data for a block
trace_data = eth.debug_traceBlockByNumber(22_739_638, diff_mode=True)

# Generate block access list
block_access_list = from_execution_trace(trace_data)

# Get what you need
balance_changes = block_access_list.balance_diffs
storage_accesses = block_access_list.account_accesses
```

## Architecture 🏗️

The package follows functional programming principles. Data flows through pure functions that transform inputs without side effects.

```sh
rpc/         # Input types (what you get from debug_traceBlock)
├── types.py # TransactionTrace, AccountState, etc.

bal/         # Core logic (what this package does)
├── types.py # BlockAccessList, balance diffs, storage accesses
├── utils.py # Pure functions for encoding/validation
└── builder.py # Main entry point

tests/       # Comprehensive test suite
├── utils.py # Test constants and data-driven test framework
└── bal/     # Tests for each component
```

## How It Works

1. **Parse** execution traces into structured data
2. **Compare** pre/post states to find what changed
3. **Encode** changes according to EIP-7928 spec
4. **Return** a complete `BlockAccessList`

## Tools We Use 🛠️

- **Pydantic** for type safety and validation
- **pytest** for comprehensive testing
- **uv** for fast package management
- **Data-driven tests** for maintainable test suites

## Design Principles

**Types everywhere.** Pydantic models catch errors at the boundary. If it compiles, it probably works.

**Test with data.** Each test case is just input/output pairs. Adding new tests should be easy.

## Running Tests

```bash
uv run pytest             # All tests
uv run pytest tests/bal/  # Just the core logic
```

Tests are fast because they're just data transformation - no network calls or external dependencies.

## Implementation Status

- ✅ Balance tracking (done)
- 🚧 Storage access tracking (planned)
- 🚧 Code change tracking (planned)
- 🚧 Nonce change tracking (planned)
