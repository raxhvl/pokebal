"""Types for Block Level Access Lists (EIP-7928)."""

from typing import List
from pydantic import BaseModel, Field

from pokebal.common.types import (
    Address,
    StorageKey,
    StorageValue,
    CodeData,
    TxIndex,
    Nonce,
)


################################
#          CONSTANTS           #
################################

# Constants from EIP-7928
MAX_TXS = 30_000
MAX_SLOTS = 300_000
MAX_ACCOUNTS = 300_000
MAX_CODE_SIZE = 24_576  # 24 KiB


# Type aliases from EIP-7928
Balance = int  # uint128 in spec


class StorageChange(BaseModel):
    """Storage change for a specific transaction."""

    tx_index: TxIndex
    new_value: StorageValue


class BalanceChange(BaseModel):
    """Balance change for a specific transaction."""

    tx_index: TxIndex
    post_balance: Balance


class NonceChange(BaseModel):
    """Nonce change for a specific transaction."""

    tx_index: TxIndex
    new_nonce: Nonce


class CodeChange(BaseModel):
    """Code change for a specific transaction."""

    tx_index: TxIndex
    new_code: CodeData


class SlotChanges(BaseModel):
    """Storage slot changes information."""

    slot: StorageKey
    changes: List[StorageChange] = Field(default_factory=list, max_items=MAX_TXS)


class SlotRead(BaseModel):
    """Storage slot read information."""

    slot: StorageKey


class AccountChanges(BaseModel):
    """Account changes information per EIP-7928."""

    address: Address
    storage_changes: List[SlotChanges] = Field(default_factory=list, max_items=MAX_SLOTS)
    storage_reads: List[SlotRead] = Field(default_factory=list, max_items=MAX_SLOTS)
    balance_changes: List[BalanceChange] = Field(default_factory=list, max_items=MAX_TXS)
    nonce_changes: List[NonceChange] = Field(default_factory=list, max_items=MAX_TXS)
    code_changes: List[CodeChange] = Field(default_factory=list, max_items=MAX_TXS)


class BlockAccessList(BaseModel):
    """Complete block access list as per EIP-7928."""

    account_changes: List[AccountChanges] = Field(default_factory=list, max_items=MAX_ACCOUNTS)
