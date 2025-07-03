"""Common types for Ethereum data structures with Pydantic validation.

This module provides foundational type aliases with runtime validation following
functional programming principles. Each type validates hex string formats at runtime.
"""

from typing import Union, Literal, Annotated
from pydantic import Field


# Base hex string validation - foundation for all hex-encoded data
HexString = Annotated[str, Field(pattern=r"^0x[0-9a-fA-F]+$")]
EVM_WORD_ZERO = "0x" + "00" * 32  # Default value for EVM word

# EVM word - 32-byte hex string (64 hex chars + 0x prefix)
# This is the fundamental unit of the EVM stack and storage
EVMWord = Annotated[
    HexString,
    Field(
        default=EVM_WORD_ZERO,
        pattern=r"^0x[0-9a-fA-F]{64}$",
        description="EVM word (32 bytes)",
    ),
]

# Ethereum address type - 20-byte hex string (40 hex chars + 0x prefix)
Address = Annotated[
    HexString,
    Field(
        default="0x" + "00" * 20,
        pattern=r"^0x[0-9a-fA-F]{40}$",
        description="Ethereum address (20 bytes)",
    ),
]

# 32-byte types that alias EVMWord with specific descriptions
Hash = Annotated[
    EVMWord, Field(description="Transaction hash, block hash, or other 32-byte hash")
]

StorageKey = Annotated[
    EVMWord, Field(description="Storage slot key in contract storage")
]

StorageValue = Annotated[
    EVMWord,
    Field(default=EVM_WORD_ZERO, description="Storage value in contract storage"),
]

# Code data type - variable length hex string for contract bytecode
CodeData = Annotated[
    HexString,
    Field(description="Contract bytecode"),
]

# Balance delta type - 12-byte two's complement (24 hex chars + 0x prefix)
BalanceDelta = Annotated[
    HexString,
    Field(
        default="0x" + "00" * 12,
        pattern=r"^0x[0-9a-fA-F]{24}$",
        description="Balance delta (12 bytes)",
    ),
]

# Numeric types for transaction and account data
TxIndex = int
Nonce = int

# Block number type - can be numeric or special string values
BlockNumber = Union[int, Literal["latest", "earliest", "pending"]]
