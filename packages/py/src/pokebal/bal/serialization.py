import ssz
from ssz.sedes import (
    ByteList,
    ByteVector,
    Container,
    List,
    uint128,
    uint64,
    uint16,
)

from .basic import (
    MAX_ACCOUNTS,
    MAX_CODE_SIZE,
    MAX_SLOTS,
    MAX_TXS,
    MAX_CODE_CHANGES,
    AccountChanges,
    BalanceChange,
    CodeChange,
    NonceChange,
    SlotChanges,
    StorageChange,
)


def _transform_storage_change(change: StorageChange) -> tuple[int, bytes]:
    """Transform StorageChange to SSZ-compatible tuple."""
    return (change.tx_index, change.new_value)


def _transform_balance_change(change: BalanceChange) -> tuple[int, int]:
    """Transform BalanceChange to SSZ-compatible tuple."""
    balance_int = int.from_bytes(change.post_balance, byteorder="little")
    return (change.tx_index, balance_int)


def _transform_nonce_change(change: NonceChange) -> tuple[int, int]:
    """Transform NonceChange to SSZ-compatible tuple."""
    return (change.tx_index, change.new_nonce)


def _transform_code_change(change: CodeChange) -> tuple[int, bytes]:
    """Transform CodeChange to SSZ-compatible tuple."""
    return (change.tx_index, change.new_code)


def _transform_slot_changes(
    slot_changes: SlotChanges,
) -> tuple[bytes, list[tuple[int, bytes]]]:
    """Transform SlotChanges to SSZ-compatible tuple."""
    changes_tuples = [
        _transform_storage_change(change) for change in slot_changes.changes
    ]
    return (slot_changes.slot, changes_tuples)


def _transform_account_changes(
    account: AccountChanges,
) -> tuple[bytes, list, list[bytes], list, list, list]:
    """Transform AccountChanges to SSZ-compatible tuple."""
    return (
        account.address,
        [_transform_slot_changes(sc) for sc in account.storage_changes],
        account.storage_reads,
        [_transform_balance_change(bc) for bc in account.balance_changes],
        [_transform_nonce_change(nc) for nc in account.nonce_changes],
        [_transform_code_change(cc) for cc in account.code_changes],
    )


def to_ssz(bal) -> bytes:
    """Serialize BlockAccessList to SSZ format."""

    # Basic types
    _address = ByteVector(20)
    _storage_key = ByteVector(32)
    _storage_value = ByteVector(32)
    _code_data = ByteList(MAX_CODE_SIZE)
    _tx_index = uint16
    _nonce = uint64
    _balance = uint128

    # StorageChange sedes
    _storage_change = Container(field_sedes=[_tx_index, _storage_value])

    # BalanceChange sedes
    _balance_change = Container(
        field_sedes=[_tx_index, _balance],
    )

    # NonceChange sedes
    _nonce_change = Container(
        field_sedes=[_tx_index, _nonce],
    )

    # CodeChange sedes
    _code_change = Container(
        field_sedes=[_tx_index, _code_data],
    )

    # SlotChanges sedes
    _slot_changes = Container(
        field_sedes=[_storage_key, List(_storage_change, MAX_TXS)],
    )

    # AccountChanges sedes
    _account_changes = Container(
        field_sedes=[
            _address,
            List(_slot_changes, MAX_SLOTS),
            List(_storage_key, MAX_SLOTS),
            List(_balance_change, MAX_TXS),
            List(_nonce_change, MAX_TXS),
            List(_code_change, MAX_CODE_CHANGES),
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
