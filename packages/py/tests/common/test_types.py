"""
Tests for common type validation using Pydantic models.

Following functional programming paradigm and atomic testing approach.
"""

import pytest
from pydantic import BaseModel, ValidationError

from common.types import (
    HexString,
    Address,
    Hash,
    EVMWord,
    StorageKey,
    StorageValue,
    BalanceDelta,
    CodeData,
    TxIndex,
    Nonce,
    BlockNumber,
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
                class TestModel(BaseModel):
                    value: HexString

                TestModel(value=hex_str)


class TestEVMWordValidation:
    """Test suite for EVM word (32-byte) validation."""

    def test_valid_evm_words(self):
        """Test that valid 32-byte EVM words are accepted."""
        valid_words = [
            "0x0000000000000000000000000000000000000000000000000000000000000000",
            "0x2c541d6c59e171e4fce71fa28e076f733f21239a7af82441974616344d5b8426",
            "0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF",
        ]

        for word in valid_words:
            class TestModel(BaseModel):
                value: EVMWord

            model = TestModel(value=word)
            assert model.value == word

    def test_invalid_evm_words(self):
        """Test that invalid EVM words are rejected."""
        invalid_words = [
            "0x123",  # Too short
            "0x12345678901234567890123456789012345678901234567890123456789012345",  # Too long
            "0x2c541d6c59e171e4fce71fa28e076f733f21239a7af82441974616344d5b842G",  # Invalid character
        ]

        for word in invalid_words:
            with pytest.raises(ValidationError):
                class TestModel(BaseModel):
                    value: EVMWord

                TestModel(value=word)


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
    """Test suite for hash validation (alias of EVMWord)."""

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


class TestStorageTypes:
    """Test suite for storage key and value types (aliases of EVMWord)."""

    def test_storage_key_validation(self):
        """Test storage key validation."""
        valid_key = "0x0000000000000000000000000000000000000000000000000000000000000001"
        
        class TestModel(BaseModel):
            key: StorageKey

        model = TestModel(key=valid_key)
        assert model.key == valid_key

    def test_storage_value_validation(self):
        """Test storage value validation."""
        valid_value = "0x0000000000000000000000000000000000000000000000009c9b5507ba47e102"
        
        class TestModel(BaseModel):
            value: StorageValue

        model = TestModel(value=valid_value)
        assert model.value == valid_value


class TestBalanceDeltaValidation:
    """Test suite for balance delta validation (12 bytes)."""

    def test_valid_balance_deltas(self):
        """Test that valid 12-byte balance deltas are accepted."""
        valid_deltas = [
            "0x000000000000000000000000",
            "0x9c9b5507ba47e103ffffff00",
            "0xFFFFFFFFFFFFFFFFFFFFFFFF",
        ]

        for delta in valid_deltas:
            class TestModel(BaseModel):
                delta: BalanceDelta

            model = TestModel(delta=delta)
            assert model.delta == delta

    def test_invalid_balance_deltas(self):
        """Test that invalid balance deltas are rejected."""
        invalid_deltas = [
            "0x123",  # Too short
            "0x000000000000000000000000000000000000000000000000000000000000000000",  # Too long (32 bytes)
            "0x9c9b5507ba47e103ffffg",  # Invalid character
        ]

        for delta in invalid_deltas:
            with pytest.raises(ValidationError):
                class TestModel(BaseModel):
                    delta: BalanceDelta

                TestModel(delta=delta)


class TestCodeDataValidation:
    """Test suite for code data validation."""

    def test_valid_code_data(self):
        """Test that valid code data is accepted."""
        valid_code = [
            "0x60806040523661001357610011610017565b005b6100115b61001f6101b7565b",
            "0x6080604052",
            "0x0",
        ]

        for code in valid_code:
            class TestModel(BaseModel):
                code: CodeData

            model = TestModel(code=code)
            assert model.code == code

    def test_invalid_code_data(self):
        """Test that invalid code data is rejected."""
        invalid_code = [
            "60806040523661001357610011610017565b005b6100115b61001f6101b7565b",  # Missing 0x
            "0xGHIJ",  # Invalid hex characters
        ]

        for code in invalid_code:
            with pytest.raises(ValidationError):
                class TestModel(BaseModel):
                    code: CodeData

                TestModel(code=code)


class TestNumericTypes:
    """Test suite for numeric types."""

    def test_tx_index_validation(self):
        """Test transaction index validation."""
        class TestModel(BaseModel):
            index: TxIndex

        model = TestModel(index=42)
        assert model.index == 42

    def test_nonce_validation(self):
        """Test nonce validation."""
        class TestModel(BaseModel):
            nonce: Nonce

        model = TestModel(nonce=123)
        assert model.nonce == 123


class TestBlockNumberValidation:
    """Test suite for block number validation."""

    def test_valid_block_numbers(self):
        """Test that valid block numbers are accepted."""
        valid_block_numbers = [
            123456,
            "latest",
            "earliest",
            "pending",
        ]

        for block_num in valid_block_numbers:
            class TestModel(BaseModel):
                block: BlockNumber

            model = TestModel(block=block_num)
            assert model.block == block_num

    def test_invalid_block_numbers(self):
        """Test that invalid block numbers are rejected."""
        invalid_block_numbers = [
            "invalid",
            "0x123",  # Hex not supported in this context
        ]

        for block_num in invalid_block_numbers:
            with pytest.raises(ValidationError):
                class TestModel(BaseModel):
                    block: BlockNumber

                TestModel(block=block_num)


# Functional validation utilities
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


def validate_evm_word(value: str) -> bool:
    """Pure function to validate EVM word format."""
    try:
        class TestModel(BaseModel):
            word: EVMWord

        TestModel(word=value)
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

    def test_evm_word_validator_function(self):
        """Test pure EVM word validator function."""
        assert validate_evm_word("0x0000000000000000000000000000000000000000000000000000000000000000") is True
        assert validate_evm_word("0x123") is False