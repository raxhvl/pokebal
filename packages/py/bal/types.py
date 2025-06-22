"""Types for Block Level Access Lists (EIP-7928)."""

from typing import List
from dataclasses import dataclass


################################
#          CONSTANTS           #
################################

# Constants from EIP-7928
MAX_TXS = 30_000
MAX_SLOTS = 300_000
MAX_ACCOUNTS = 300_000
MAX_CODE_SIZE = 24 * 1024  # 24 Kib


################################
#          TYPE ALIAS          #
################################

HexString = str  # 0x-prefixed hex string
Address = HexString  # 20-byte hex string
StorageKey = HexString  # 32-byte hex string
StorageValue = HexString  # 32-byte hex string
CodeData = HexString  # up to MAX_CODE_SIZE bytes
# TODO: Why is it 12 bytes and not 32 bytes?
# TODO: Also why is this not an integer?
BalanceDelta = HexString  # 12-byte two's complement
TxIndex = int
Nonce = int


@dataclass
class BalanceChange:
    tx_index: TxIndex
    delta: BalanceDelta


@dataclass
class PerTxAccess:
    tx_index: TxIndex
    value_after: StorageValue


@dataclass
class SlotAccess:
    slot: StorageKey
    accesses: List[PerTxAccess]


@dataclass
class AccountAccess:
    address: Address
    accesses: List[SlotAccess]


@dataclass
class AccountBalanceDiff:
    address: Address
    changes: List[BalanceChange]


@dataclass
class AccountCodeDiff:
    address: Address
    new_code: CodeData


@dataclass
class AccountNonce:
    address: Address
    nonce: Nonce


AccountAccessList = List[AccountAccess]
BalanceDiffs = List[AccountBalanceDiff]
AccountCodeDiffs = List[AccountCodeDiff]
NonceDiffs = List[AccountNonce]


@dataclass
class BlockAccessList:
    account_accesses: AccountAccessList
    balance_diffs: BalanceDiffs
    code_diffs: AccountCodeDiffs
    nonce_diffs: NonceDiffs
