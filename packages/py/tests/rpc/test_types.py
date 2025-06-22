"""
Tests for RPC type validation using Pydantic models.

Following functional programming paradigm and atomic testing approach.
"""

import pytest
from pydantic import ValidationError, TypeAdapter
import json
from pathlib import Path

from rpc.types import (
    AccountState,
    TransactionTrace,
    BlockDebugTraceResult,
)


class TestAccountState:
    """Test suite for AccountState model."""

    def test_valid_account_state_full(self):
        """Test AccountState with all fields populated."""
        account_data = {
            "balance": "0x9c9b5507ba47e103",
            "code": "0x60806040523661001357610011610017565b005b6100115b61001f6101b7565b",
            "nonce": 1,
            "storage": {
                "0x0000000000000000000000000000000000000000000000000000000000000001": "0x0000000000000000000000000000000000000000000000009c9b5507ba47e102"
            },
        }

        account = AccountState.model_validate(account_data)
        assert account.balance == "0x9c9b5507ba47e103"
        assert account.nonce == 1
        assert len(account.storage) == 1

    def test_valid_account_state_partial(self):
        """Test AccountState with only some fields populated."""
        account_data = {"balance": "0x73d0cdd7b8f91dc3"}

        account = AccountState.model_validate(account_data)
        assert account.balance == "0x73d0cdd7b8f91dc3"
        assert account.code is None
        assert account.nonce is None
        assert account.storage is None

    def test_invalid_account_state(self):
        """Test AccountState validation with invalid data."""
        invalid_data = {
            "balance": "invalid_hex",  # Invalid hex string
            "nonce": "0x1",
        }

        with pytest.raises(ValidationError):
            AccountState.model_validate(invalid_data)


class TestTransactionTrace:
    """Test suite for TransactionTrace model using sample data."""

    @pytest.fixture
    def sample_trace_data(self):
        """Load sample trace data from fixtures."""
        fixtures_path = (
            Path(__file__).parent.parent / "fixtures" / "trace_22739638.json"
        )
        with open(fixtures_path) as f:
            data = json.load(f)
        return data[0]  # Get first transaction trace

    def test_valid_transaction_trace(self, sample_trace_data):
        """Test TransactionTrace validation with real sample data."""
        trace = TransactionTrace.model_validate(sample_trace_data)

        # Verify structure
        assert hasattr(trace, "result")
        assert hasattr(trace, "txHash")
        assert hasattr(trace.result, "pre")
        assert hasattr(trace.result, "post")

        # Verify transaction hash format
        assert trace.txHash.startswith("0x")
        assert len(trace.txHash) == 66  # 0x + 64 hex chars

        # Verify account states are properly parsed
        assert isinstance(trace.result.pre, dict)
        assert isinstance(trace.result.post, dict)

        # Check that addresses are valid
        for address in trace.result.pre.keys():
            assert address.startswith("0x")
            assert len(address) == 42  # 0x + 40 hex chars

    def test_invalid_transaction_trace(self):
        """Test TransactionTrace validation with invalid data."""
        invalid_data = {
            "result": {"pre": {}, "post": {}},
            "txHash": "invalid_hash",  # Invalid hash format
        }

        with pytest.raises(ValidationError):
            TransactionTrace.model_validate(invalid_data)


class TestBlockDebugTraceResult:
    """Test suite for complete block trace result."""

    @pytest.fixture
    def sample_block_data(self):
        """Load complete sample block data."""
        fixtures_path = (
            Path(__file__).parent.parent / "fixtures" / "trace_22739638.json"
        )
        with open(fixtures_path) as f:
            return json.load(f)

    def test_valid_block_trace_result(self, sample_block_data):
        """Test validation of complete block trace result."""
        adapter = TypeAdapter(BlockDebugTraceResult)
        block_trace = adapter.validate_python(sample_block_data)

        # Verify it's a list of transaction traces
        assert isinstance(block_trace, list)
        assert len(block_trace) > 0

        # Verify each item is a valid TransactionTrace
        for trace in block_trace:
            assert isinstance(trace, TransactionTrace)
            assert hasattr(trace, "result")
            assert hasattr(trace, "txHash")
