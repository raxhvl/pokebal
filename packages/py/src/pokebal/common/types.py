"""Common types for Ethereum data structures.

This module provides foundational types following functional programming principles.
"""

from typing import Union, Literal

# Constants
EVM_ZERO_WORD = b'\x00' * 32  # 32 bytes of zero - default EVM word

# Numeric types for transaction and account data

# Block number type - can be numeric or special string values
BlockNumber = Union[int, Literal["latest", "earliest", "pending"]]
