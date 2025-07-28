import ssz
from typing import Any
from ssz.sedes import (
    ByteList,
    ByteVector,
    Container,
    List,
    uint64,
    uint16,
)

from .basic import (
    MAX_ACCOUNTS,
    MAX_CODE_SIZE,
    MAX_SLOTS,
    MAX_TXS,
    AccountChanges,
)


def _group_changes_by_tx(account: AccountChanges) -> dict[int, dict]:
    """Group all changes by transaction index."""
    tx_changes: Any = {}

    # Group storage changes by transaction
    for slot_changes in account.storage_changes:
        for s_change in slot_changes.changes:
            tx_idx = s_change.tx_index
            if tx_idx not in tx_changes:
                tx_changes[tx_idx] = {
                    "storage": {},
                    "balance": None,
                    "nonce": None,
                    "code": None,
                }
            tx_changes[tx_idx]["storage"][slot_changes.slot] = s_change.new_value

    # Group balance changes by transaction
    for b_change in account.balance_changes:
        tx_idx = b_change.tx_index
        if tx_idx not in tx_changes:
            tx_changes[tx_idx] = {
                "storage": {},
                "balance": None,
                "nonce": None,
                "code": None,
            }
        tx_changes[tx_idx]["balance"] = b_change.post_balance

    # Group nonce changes by transaction
    for n_change in account.nonce_changes:
        tx_idx = n_change.tx_index
        if tx_idx not in tx_changes:
            tx_changes[tx_idx] = {
                "storage": {},
                "balance": None,
                "nonce": None,
                "code": None,
            }
        tx_changes[tx_idx]["nonce"] = n_change.new_nonce

    # Group code changes by transaction
    for c_change in account.code_changes:
        tx_idx = c_change.tx_index
        if tx_idx not in tx_changes:
            tx_changes[tx_idx] = {
                "storage": {},
                "balance": None,
                "nonce": None,
                "code": None,
            }
        tx_changes[tx_idx]["code"] = c_change.new_code

    return tx_changes


def _transform_account_changes(
    account: AccountChanges,
):
    """Transform AccountChanges to transaction-grouped SSZ-compatible tuple."""
    tx_changes = _group_changes_by_tx(account)

    # Transform to list of (tx_index, changes) tuples, sorted by tx_index
    tx_tuples = []
    for tx_idx in sorted(tx_changes.keys()):
        changes = tx_changes[tx_idx]
        # Convert storage dict to list of (slot, value) tuples, sorted by slot
        storage_list = [
            (slot, value) for slot, value in sorted(changes["storage"].items())
        ]

        tx_tuple = (
            tx_idx,
            {
                "storage": storage_list,
                "balance": changes["balance"],
                "nonce": changes["nonce"],
                "code": changes["code"],
            },
        )
        tx_tuples.append(tx_tuple)

    # Convert tx_tuples to proper SSZ format
    ssz_tx_tuples = []
    for tx_idx, changes in tx_tuples:
        ssz_tx_tuple = (
            tx_idx,
            (
                changes["storage"],  # list of (slot, value) tuples
                changes["balance"] or b"\x00" * 16,  # default balance if None
                changes["nonce"] or 0,  # default nonce if None
                changes["code"] or b"",  # default code if None
            ),
        )
        ssz_tx_tuples.append(ssz_tx_tuple)

    return (account.address, account.storage_reads, ssz_tx_tuples)


def to_ssz_group_by_tx(bal) -> bytes:
    """Group by tx"""

    # Basic types
    _address = ByteVector(20)
    _storage_key = ByteVector(32)
    _storage_value = ByteVector(32)
    _code_data = ByteList(MAX_CODE_SIZE)
    _tx_index = uint16
    _nonce = uint64
    _balance = ByteVector(16)

    # Storage change: (slot, value)
    _storage_change = Container(field_sedes=[_storage_key, _storage_value])

    # Transaction changes: storage, balance, nonce, code for a single transaction
    _tx_change_data = Container(
        field_sedes=[
            List(_storage_change, MAX_SLOTS),  # storage changes
            _balance,  # balance change (nullable)
            _nonce,  # nonce change (nullable)
            _code_data,  # code change (nullable)
        ]
    )

    # Transaction changes with index: (tx_index, changes)
    _tx_changes = Container(field_sedes=[_tx_index, _tx_change_data])

    # AccountChanges sedes: address, storage_reads, transaction_changes
    _account_changes = Container(
        field_sedes=[
            _address,  # account address
            List(_storage_key, MAX_SLOTS),  # storage reads
            List(_tx_changes, MAX_TXS),  # transaction changes
        ]
    )

    # BlockAccessList sedes
    _block_access_list = Container(field_sedes=[List(_account_changes, MAX_ACCOUNTS)])

    # Transform BlockAccessList to SSZ
    account_tuples = [
        _transform_account_changes(account) for account in bal.account_changes
    ]

    # Encode using SSZ
    return ssz.encode((account_tuples,), _block_access_list)
