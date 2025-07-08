"""Test data constants for RPC tests.

This module provides reusable test data as constants for RPC type testing.
"""

from pokebal.common.hex_utils import hex_to_bytes


class TestBalances:
    """Test balance values as bytes."""
    
    BALANCE_1 = hex_to_bytes("0x9c9b5507ba47e103")
    BALANCE_2 = hex_to_bytes("0x73d0cdd7b8f91dc3")


class TestAddresses:
    """Test Ethereum addresses as bytes."""
    
    ADDRESS_1 = hex_to_bytes("0x3328f7f4a1d1c57c35df56bbf0c9dcafca309c49")
    ADDRESS_2 = hex_to_bytes("0x4838b106fce9647bdf1e7877bf73ce8b0bad5f97")


class TestHashes:
    """Test transaction hashes as bytes."""
    
    TX_HASH_1 = hex_to_bytes("0x2c541d6c59e171e4fce71fa28e076f733f21239a7af82441974616344d5b8426")


class TestCode:
    """Test contract code as bytes."""
    
    SIMPLE_CODE = hex_to_bytes("0x60806040523661001357610011610017565b005b6100115b61001f6101b7565b")


class TestStorageData:
    """Test storage keys and values as bytes."""
    
    STORAGE_KEY_1 = hex_to_bytes("0x0000000000000000000000000000000000000000000000000000000000000001")
    STORAGE_VALUE_1 = hex_to_bytes("0x0000000000000000000000000000000000000000000000009c9b5507ba47e102")