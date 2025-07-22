from pydantic import BaseModel, Field
from pokebal.common.types import EVM_ZERO_WORD
from typing import List

# Type aliases for bytes - keeping semantic meaning
Address = bytes
StorageKey = bytes
StorageValue = bytes
Bytecode = bytes
# Numeric types
Balance = bytes
TxIndex = int
Nonce = int

################################
#          CONSTANTS           #
################################

# Constants from EIP-7928
MAX_TXS = 30_000
MAX_SLOTS = 300_000
MAX_ACCOUNTS = 300_000
MAX_CODE_SIZE = 24_576  # 24 KiB


class StorageChange(BaseModel):
    """Storage change for a specific transaction."""

    tx_index: TxIndex
    new_value: StorageValue = EVM_ZERO_WORD


class BalanceChange(BaseModel):
    """Balance change for a specific transaction."""

    tx_index: TxIndex
    post_balance: Balance = b"\x00" * 16


class NonceChange(BaseModel):
    """Nonce change for a specific transaction."""

    tx_index: TxIndex
    new_nonce: Nonce = Field(
        default=0,
    )


class CodeChange(BaseModel):
    """Code change for a specific transaction."""

    tx_index: TxIndex
    new_code: Bytecode


class SlotChanges(BaseModel):
    """Storage slot changes information."""

    slot: StorageKey
    changes: List[StorageChange] = Field(default=[], max_length=MAX_TXS)


class AccountChanges(BaseModel):
    """Account changes information per EIP-7928."""

    address: Address
    storage_changes: List[SlotChanges] = Field(default=[], max_length=MAX_SLOTS)
    storage_reads: List[StorageKey] = Field(default=[], max_length=MAX_SLOTS)
    balance_changes: List[BalanceChange] = Field(default=[], max_length=MAX_TXS)
    nonce_changes: List[NonceChange] = Field(default=[], max_length=MAX_TXS)
    code_changes: List[CodeChange] = Field(default=[], max_length=MAX_TXS)
