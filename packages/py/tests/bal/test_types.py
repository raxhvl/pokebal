"""Tests for Block Access List types."""

from pokebal.bal.types import (
    BlockAccessList,
)
from pokebal.common.types import (
    Address,
    StorageKey,
    StorageValue,
    CodeData,
    TxIndex,
    Nonce,
)


class TestBlockAccessList:
    """Test cases for BlockAccessList functionality."""

    def test_add_storage_write_new_account(self):
        """Test adding storage write for a new account."""
        bal = BlockAccessList()
        address = Address("0x1234567890123456789012345678901234567890")
        slot = StorageKey(
            "0x0000000000000000000000000000000000000000000000000000000000000001"
        )
        tx_index = TxIndex(0)
        new_value = StorageValue(
            "0x0000000000000000000000000000000000000000000000000000000000000002"
        )

        bal.add_storage_write(address, slot, tx_index, new_value)

        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert account.address == address
        assert len(account.storage_changes) == 1
        assert account.storage_changes[0].slot == slot
        assert len(account.storage_changes[0].changes) == 1
        assert account.storage_changes[0].changes[0].tx_index == tx_index
        assert account.storage_changes[0].changes[0].new_value == new_value

    def test_add_storage_write_existing_account_new_slot(self):
        """Test adding storage write for existing account but new slot."""
        bal = BlockAccessList()
        address = Address("0x1234567890123456789012345678901234567890")
        slot1 = StorageKey(
            "0x0000000000000000000000000000000000000000000000000000000000000001"
        )
        slot2 = StorageKey(
            "0x0000000000000000000000000000000000000000000000000000000000000002"
        )
        tx_index = TxIndex(0)
        value1 = StorageValue(
            "0x0000000000000000000000000000000000000000000000000000000000000001"
        )
        value2 = StorageValue(
            "0x0000000000000000000000000000000000000000000000000000000000000002"
        )

        bal.add_storage_write(address, slot1, tx_index, value1)
        bal.add_storage_write(address, slot2, tx_index, value2)

        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.storage_changes) == 2
        assert {sc.slot for sc in account.storage_changes} == {slot1, slot2}

    def test_add_storage_write_existing_slot(self):
        """Test adding multiple storage writes for the same slot."""
        bal = BlockAccessList()
        address = Address("0x1234567890123456789012345678901234567890")
        slot = StorageKey(
            "0x0000000000000000000000000000000000000000000000000000000000000001"
        )
        tx_index1 = TxIndex(0)
        tx_index2 = TxIndex(1)
        value1 = StorageValue(
            "0x0000000000000000000000000000000000000000000000000000000000000001"
        )
        value2 = StorageValue(
            "0x0000000000000000000000000000000000000000000000000000000000000002"
        )

        bal.add_storage_write(address, slot, tx_index1, value1)
        bal.add_storage_write(address, slot, tx_index2, value2)

        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.storage_changes) == 1
        slot_changes = account.storage_changes[0]
        assert len(slot_changes.changes) == 2
        assert slot_changes.changes[0].tx_index == tx_index1
        assert slot_changes.changes[1].tx_index == tx_index2

    def test_add_storage_read_new_account(self):
        """Test adding storage read for a new account."""
        bal = BlockAccessList()
        address = Address("0x1234567890123456789012345678901234567890")
        slot = StorageKey(
            "0x0000000000000000000000000000000000000000000000000000000000000001"
        )

        bal.add_storage_read(address, slot)

        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert account.address == address
        assert len(account.storage_reads) == 1
        assert account.storage_reads[0].slot == slot

    def test_add_storage_read_existing_slot(self):
        """Test adding duplicate storage reads (should not duplicate)."""
        bal = BlockAccessList()
        address = Address("0x1234567890123456789012345678901234567890")
        slot = StorageKey(
            "0x0000000000000000000000000000000000000000000000000000000000000001"
        )

        bal.add_storage_read(address, slot)
        bal.add_storage_read(address, slot)

        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.storage_reads) == 1

    def test_add_balance_change(self):
        """Test adding balance change."""
        bal = BlockAccessList()
        address = Address("0x1234567890123456789012345678901234567890")
        tx_index = TxIndex(0)
        post_balance = 1000

        bal.add_balance_change(address, tx_index, post_balance)

        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.balance_changes) == 1
        assert account.balance_changes[0].tx_index == tx_index
        assert account.balance_changes[0].post_balance == post_balance

    def test_add_nonce_change(self):
        """Test adding nonce change."""
        bal = BlockAccessList()
        address = Address("0x1234567890123456789012345678901234567890")
        tx_index = TxIndex(0)
        new_nonce = Nonce(42)

        bal.add_nonce_change(address, tx_index, new_nonce)

        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.nonce_changes) == 1
        assert account.nonce_changes[0].tx_index == tx_index
        assert account.nonce_changes[0].new_nonce == new_nonce

    def test_add_code_change(self):
        """Test adding code change."""
        bal = BlockAccessList()
        address = Address("0x1234567890123456789012345678901234567890")
        tx_index = TxIndex(0)
        new_code = CodeData("0x736f6d655f627974656e636f6465")

        bal.add_code_change(address, tx_index, new_code)

        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.code_changes) == 1
        assert account.code_changes[0].tx_index == tx_index
        assert account.code_changes[0].new_code == new_code

    def test_mixed_operations_same_account(self):
        """Test multiple different operations on the same account."""
        bal = BlockAccessList()
        address = Address("0x1234567890123456789012345678901234567890")

        slot = StorageKey(
            "0x0000000000000000000000000000000000000000000000000000000000000001"
        )
        tx_index = TxIndex(0)
        value = StorageValue(
            "0x0000000000000000000000000000000000000000000000000000000000000002"
        )
        balance = 1000
        nonce = Nonce(42)
        code = CodeData("0x627974656e636f6465")

        bal.add_storage_write(address, slot, tx_index, value)
        bal.add_storage_read(address, slot)
        bal.add_balance_change(address, tx_index, balance)
        bal.add_nonce_change(address, tx_index, nonce)
        bal.add_code_change(address, tx_index, code)

        # Should only have one account
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]

        # Verify all operations were recorded
        assert len(account.storage_changes) == 1
        assert len(account.storage_reads) == 1
        assert len(account.balance_changes) == 1
        assert len(account.nonce_changes) == 1
        assert len(account.code_changes) == 1

    def test_multiple_accounts(self):
        """Test operations on multiple different accounts."""
        bal = BlockAccessList()
        address1 = Address("0x1111111111111111111111111111111111111111")
        address2 = Address("0x2222222222222222222222222222222222222222")

        slot = StorageKey(
            "0x0000000000000000000000000000000000000000000000000000000000000001"
        )
        tx_index = TxIndex(0)
        value = StorageValue(
            "0x0000000000000000000000000000000000000000000000000000000000000002"
        )

        bal.add_storage_write(address1, slot, tx_index, value)
        bal.add_storage_write(address2, slot, tx_index, value)

        assert len(bal.account_changes) == 2
        addresses = {account.address for account in bal.account_changes}
        assert addresses == {address1, address2}
