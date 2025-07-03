"""Test data constants for Block Access List tests.

This module provides reusable test data as class attributes for use with dot notation.
"""

from pokebal.common.types import (
    Address,
    StorageKey,
    StorageValue,
    CodeData,
    TxIndex,
    Nonce,
)


class Addresses:
    """Test addresses with meaningful names."""

    ALICE = Address("0x1234567890123456789012345678901234567890")
    BOB = Address("0x1111111111111111111111111111111111111111")
    CAROL = Address("0x2222222222222222222222222222222222222222")


class StorageSlots:
    """Test storage slots for various scenarios."""

    SLOT_1 = StorageKey(
        "0x0000000000000000000000000000000000000000000000000000000000000001"
    )
    SLOT_2 = StorageKey(
        "0x0000000000000000000000000000000000000000000000000000000000000002"
    )
    SLOT_3 = StorageKey(
        "0x0000000000000000000000000000000000000000000000000000000000000003"
    )
    MIN_SLOT = StorageKey(
        "0x0000000000000000000000000000000000000000000000000000000000000000"
    )
    MAX_SLOT = StorageKey(
        "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    )


class StorageValues:
    """Test storage values for various scenarios."""

    VALUE_1 = StorageValue(
        "0x0000000000000000000000000000000000000000000000000000000000000001"
    )
    VALUE_2 = StorageValue(
        "0x0000000000000000000000000000000000000000000000000000000000000002"
    )
    ZERO_VALUE = StorageValue(
        "0x0000000000000000000000000000000000000000000000000000000000000000"
    )
    MAX_VALUE = StorageValue(
        "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    )


class TxIndices:
    """Test transaction indices."""

    TX_0 = TxIndex(0)
    TX_1 = TxIndex(1)
    TX_2 = TxIndex(2)


class Nonces:
    """Test nonce values."""

    NONCE_0 = Nonce(0)
    NONCE_1 = Nonce(1)
    NONCE_42 = Nonce(42)
    NONCE_100 = Nonce(100)
    NONCE_1000 = Nonce(1000)


class Balances:
    """Test balance values."""

    BALANCE_1000 = 1000
    BALANCE_2000 = 2000


class CodeSamples:
    """Test code data samples."""

    EMPTY_CODE = CodeData("0x")
    SIMPLE_CODE = CodeData("0x736f6d655f627974656e636f6465")
    ANOTHER_CODE = CodeData("0x627974656e636f6465")
    COMPLEX_CODE = CodeData("0x608060405234801561001057600080fd5b50")
    LARGE_CODE = CodeData("0x" + "60" * 100)  # Large bytecode sample
