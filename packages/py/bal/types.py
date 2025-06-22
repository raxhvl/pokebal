"""Types for Block Level Access Lists (EIP-7928)."""

from typing import List
from pydantic import BaseModel

from common.types import (
    Address,
    StorageKey,
    StorageValue,
    CodeData,
    BalanceDelta,
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
MAX_CODE_SIZE = 24 * 1024  # 24 Kib


class BalanceChange(BaseModel):
    """Balance change for a specific transaction."""
    
    tx_index: TxIndex
    delta: BalanceDelta


class PerTxAccess(BaseModel):
    """Per-transaction storage access information."""
    
    tx_index: TxIndex
    value_after: StorageValue


class SlotAccess(BaseModel):
    """Storage slot access information."""
    
    slot: StorageKey
    accesses: List[PerTxAccess]


class AccountAccess(BaseModel):
    """Account storage access information."""
    
    address: Address
    accesses: List[SlotAccess]


class AccountBalanceDiff(BaseModel):
    """Account balance difference information."""
    
    address: Address
    changes: List[BalanceChange]


class AccountCodeDiff(BaseModel):
    """Account code difference information."""
    
    address: Address
    new_code: CodeData


class AccountNonce(BaseModel):
    """Account nonce information."""
    
    address: Address
    nonce: Nonce


AccountAccessList = List[AccountAccess]
BalanceDiffs = List[AccountBalanceDiff]
AccountCodeDiffs = List[AccountCodeDiff]
NonceDiffs = List[AccountNonce]


class BlockAccessList(BaseModel):
    """Complete block access list as per EIP-7928."""
    
    account_accesses: AccountAccessList = []
    balance_diffs: BalanceDiffs = []
    code_diffs: AccountCodeDiffs = []
    nonce_diffs: NonceDiffs = []
