from ssz.sedes import (
    ByteList,
    ByteVector,
    Container,
    List,
    uint128,
    uint64,
    uint16,
)

from pokebal.bal.types import (
    MAX_ACCOUNTS,
    MAX_CODE_SIZE,
    MAX_SLOTS,
    MAX_TXS,
    BlockAccessList,
    AccountChanges,
    BalanceChange,
    CodeChange,
    NonceChange,
    SlotChanges,
    SlotRead,
    StorageChange,
)


def get_bal_ssz_sedes():
    """Build SSZ sedes for BlockAccessList serialization following EIP-7928."""

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
            List(_code_change, MAX_TXS),
        ]
    )

    # BlockAccessList sedes
    return Container(field_sedes=[List(_account_changes, MAX_ACCOUNTS)])


def serialize(bal: BlockAccessList) -> bytes:
    """Serialize a BlockAccessList to SSZ format."""
    ssz_sedes = get_bal_ssz_sedes()
    return ssz_sedes.serialize(bal)


def _convert_ssz_to_bal(ssz_data) -> BlockAccessList:
    """Convert SSZ-deserialized data to BlockAccessList."""

    account_changes = []
    for ssz_account in ssz_data[0]:  # First field is List[AccountChanges]
        address = bytes(ssz_account[0])

        # Storage changes
        storage_changes = []
        for ssz_slot_changes in ssz_account[1]:
            slot = bytes(ssz_slot_changes[0])
            changes = []
            for ssz_change in ssz_slot_changes[1]:
                changes.append(
                    StorageChange(
                        tx_index=int(ssz_change[0]), new_value=bytes(ssz_change[1])
                    )
                )
            storage_changes.append(SlotChanges(slot=slot, changes=changes))

        # Storage reads
        storage_reads = []
        for ssz_slot_read in ssz_account[2]:
            storage_reads.append(SlotRead(slot=bytes(ssz_slot_read)))

        # Balance changes
        balance_changes = []
        for ssz_balance_change in ssz_account[3]:
            balance_changes.append(
                BalanceChange(
                    tx_index=int(ssz_balance_change[0]),
                    post_balance=int(ssz_balance_change[1]),
                )
            )

        # Nonce changes
        nonce_changes = []
        for ssz_nonce_change in ssz_account[4]:
            nonce_changes.append(
                NonceChange(
                    tx_index=int(ssz_nonce_change[0]),
                    new_nonce=int(ssz_nonce_change[1]),
                )
            )

        # Code changes
        code_changes = []
        for ssz_code_change in ssz_account[5]:
            code_changes.append(
                CodeChange(
                    tx_index=int(ssz_code_change[0]), new_code=bytes(ssz_code_change[1])
                )
            )

        account_changes.append(
            AccountChanges(
                address=address,
                storage_changes=storage_changes,
                storage_reads=storage_reads,
                balance_changes=balance_changes,
                nonce_changes=nonce_changes,
                code_changes=code_changes,
            )
        )

    return BlockAccessList(account_changes=account_changes)


def deserialize(data: bytes) -> BlockAccessList:
    """Deserialize bytes to a BlockAccessList."""
    ssz_sedes = get_bal_ssz_sedes()
    ssz_data = ssz_sedes.deserialize(data)
    return _convert_ssz_to_bal(ssz_data)
