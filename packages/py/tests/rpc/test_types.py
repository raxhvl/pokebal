"""
Tests for RPC type validation using Pydantic models.

Following functional programming paradigm and atomic testing approach.
"""

import pytest
from pydantic import BaseModel, ValidationError, TypeAdapter
import json
from pathlib import Path

from rpc.types import (
    HexString,
    Address,
    Hash,
    AccountState,
    TransactionTrace,
    BlockDebugTraceResult,
)


class TestHexStringValidation:
    """Test suite for hex string type validation."""

    def test_valid_hex_strings(self):
        """Test that valid hex strings are accepted."""
        valid_hex_strings = [
            "0x0",
            "0x1234567890abcdef",
            "0xABCDEF",
            "0x0000000000000000000000000000000000000000000000000000000000000000",
        ]

        for hex_str in valid_hex_strings:
            # Should not raise ValidationError
            class TestModel(BaseModel):
                value: HexString

            model = TestModel(value=hex_str)
            assert model.value == hex_str

    def test_invalid_hex_strings(self):
        """Test that invalid hex strings are rejected."""
        invalid_hex_strings = [
            "1234",  # Missing 0x prefix
            "0x",  # Empty hex
            "0xGHIJ",  # Invalid hex characters
            "0x123g",  # Mixed valid/invalid chars
            "",  # Empty string
            "0X1234",  # Wrong case prefix
        ]

        for hex_str in invalid_hex_strings:
            with pytest.raises(ValidationError):
                # Create a model with HexString field to test validation
                class TestModel(BaseModel):
                    value: HexString

                TestModel(value=hex_str)


class TestAddressValidation:
    """Test suite for Ethereum address validation."""

    def test_valid_addresses(self):
        """Test that valid Ethereum addresses are accepted."""
        valid_addresses = [
            "0x0000000000000000000000000000000000000000",
            "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
            "0x1234567890123456789012345678901234567890",
            "0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF",
        ]

        for address in valid_addresses:

            class TestModel(BaseModel):
                addr: Address

            model = TestModel(addr=address)
            assert model.addr == address

    def test_invalid_addresses(self):
        """Test that invalid addresses are rejected."""
        invalid_addresses = [
            "0x123",  # Too short
            "0x12345678901234567890123456789012345678901",  # Too long
            "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA9604G",  # Invalid character
            "d8dA6BF26964aF9D7eEd9e03E53415D37aA96045",  # Missing 0x
        ]

        for address in invalid_addresses:
            with pytest.raises(ValidationError):

                class TestModel(BaseModel):
                    addr: Address

                TestModel(addr=address)


class TestHashValidation:
    """Test suite for hash validation."""

    def test_valid_hashes(self):
        """Test that valid 32-byte hashes are accepted."""
        valid_hashes = [
            "0x0000000000000000000000000000000000000000000000000000000000000000",
            "0x2c541d6c59e171e4fce71fa28e076f733f21239a7af82441974616344d5b8426",
            "0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF",
        ]

        for hash_val in valid_hashes:

            class TestModel(BaseModel):
                hash: Hash

            model = TestModel(hash=hash_val)
            assert model.hash == hash_val

    def test_invalid_hashes(self):
        """Test that invalid hashes are rejected."""
        invalid_hashes = [
            "0x123",  # Too short
            "0x12345678901234567890123456789012345678901234567890123456789012345",  # Too long
            "0x2c541d6c59e171e4fce71fa28e076f733f21239a7af82441974616344d5b842G",  # Invalid character
        ]

        for hash_val in invalid_hashes:
            with pytest.raises(ValidationError):

                class TestModel(BaseModel):
                    hash: Hash

                TestModel(hash=hash_val)


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


def validate_hex_string(value: str) -> bool:
    """Pure function to validate hex string format."""
    try:

        class TestModel(BaseModel):
            value: HexString

        TestModel(value=value)
        return True
    except ValidationError:
        return False


def validate_address(value: str) -> bool:
    """Pure function to validate Ethereum address format."""
    try:

        class TestModel(BaseModel):
            addr: Address

        TestModel(addr=value)
        return True
    except ValidationError:
        return False


class TestFunctionalValidators:
    """Test functional validation utilities."""

    def test_hex_string_validator_function(self):
        """Test pure hex string validator function."""
        assert validate_hex_string("0x1234") is True
        assert validate_hex_string("invalid") is False

    def test_address_validator_function(self):
        """Test pure address validator function."""
        assert validate_address("0x0000000000000000000000000000000000000000") is True
        assert validate_address("0x123") is False
