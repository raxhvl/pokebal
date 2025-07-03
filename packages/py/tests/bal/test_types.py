"""Tests for Block Access List types.

Definitions:
Touched account: An account that has been either nonce, balance, code or storage modified. Storage read
is also considered a touch.
Untouched account: An account that has not been touched.

Generalized Testing Pattern for Account Fields:
This test suite follows a systematic pattern for testing each account field (storage, balance, nonce, code).
The pattern ensures comprehensive coverage of field behavior within the Block Access List system.

1. Account State Coverage:
    Test how a field behaves on different account states.
   - "untouched_account": Test operation on a fresh account (creates new account entry)
   - "touched_account": Test operation on an already modified account (extends existing account)

2. Transaction Scope Testing:
    Test how a field behaves within the context of transactions.
   - "same_transaction": Multiple operations within the same transaction
   - "different_transactions": Same operation across multiple transactions

3. Deduplication Logic:
    Test how a field handles deduplication.
   - "same_transaction_duplicates": Handle repeated operations in same transaction
     * For writes: Last write wins
     * For reads: No duplication
   - "cross_transaction_duplicates": Handle repeated operations across transactions
   - "same_transactions_multiple_unique_entries": Same operation multiple times in same transaction
   - "different_transactions_multiple_unique_entries": Same operation multiple times across transactions

4. Operation Type Coverage:
    Test different operation types for each field.
   - "read_operations": Test read-only operations (storage reads)
   - "write_operations": Test write operations (storage writes, balance/nonce/code changes)
   - "mixed_operations": Test combination of reads and writes

5. Field Interaction Testing:
    Test how different fields interact with each other.
   - "same_account_mixed_operations": Combine different field operations on same account
   - "multi_account_mixed_operations": Combine different field operations across multiple accounts

6. Edge Case Coverage:
   - "read_write_interactions": Test interactions between read and write operations on same slot
   - "boundary_conditions": Test limits and edge scenarios specific to the field
   - "empty_operations": Test behavior with empty or zero values

Test Structure Template:
```python
def test_{field}_{scenario}:
    \"\"\"Test {field} {scenario}.\"\"\"
    # Arrange: Setup BAL, address, and field-specific data
    bal = BlockAccessList()
    address = Address("0x...")

    # Act: Perform the operation
    bal.add_{field}_operation(...)

    # Assert: Verify account structure and field state
    assert len(bal.account_changes) == expected_count
    account = bal.account_changes[0]
    # Note: Use appropriate field name based on operation type:
    # - storage_changes, storage_reads
    # - balance_changes, nonce_changes, code_changes
    assert len(account.{field}_operations) == expected_changes
```

"""

from pokebal.bal.types import (
    BlockAccessList,
)


from .constants import (
    Addresses,
    StorageSlots,
    StorageValues,
    TxIndices,
    Nonces,
    Balances,
    CodeSamples,
)


class TestStorageOperations:
    """Test cases for storage operations following the generalized testing pattern."""

    # 1. Account State Coverage Tests

    def test_storage_write_untouched_account(self):
        """Test storage write on untouched account creates new account entry."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_storage_write(
            Addresses.ALICE, StorageSlots.SLOT_1, TxIndices.TX_0, StorageValues.VALUE_2
        )

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert account.address == Addresses.ALICE
        assert len(account.storage_changes) == 1
        assert account.storage_changes[0].slot == StorageSlots.SLOT_1
        assert len(account.storage_changes[0].changes) == 1
        assert account.storage_changes[0].changes[0].tx_index == TxIndices.TX_0
        assert account.storage_changes[0].changes[0].new_value == StorageValues.VALUE_2

    def test_storage_write_touched_account(self):
        """Test storage write on touched account extends existing account entry."""
        # Arrange
        bal = BlockAccessList()

        # Pre-touch the account with balance change
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_0, Balances.BALANCE_1000)

        # Act
        bal.add_storage_write(
            Addresses.ALICE, StorageSlots.SLOT_1, TxIndices.TX_0, StorageValues.VALUE_1
        )

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.storage_changes) == 1
        assert len(account.balance_changes) == 1
        assert account.storage_changes[0].slot == StorageSlots.SLOT_1

    def test_storage_read_untouched_account(self):
        """Test storage read on untouched account creates new account entry."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_storage_read(Addresses.ALICE, StorageSlots.SLOT_1)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert account.address == Addresses.ALICE
        assert len(account.storage_reads) == 1
        assert account.storage_reads[0].slot == StorageSlots.SLOT_1

    def test_storage_read_touched_account(self):
        """Test storage read on touched account extends existing account entry."""
        # Arrange
        bal = BlockAccessList()

        # Pre-touch the account with nonce change
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_0, Nonces.NONCE_42)

        # Act
        bal.add_storage_read(Addresses.ALICE, StorageSlots.SLOT_1)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.storage_reads) == 1
        assert len(account.nonce_changes) == 1
        assert account.storage_reads[0].slot == StorageSlots.SLOT_1

    # 2. Transaction Scope Testing

    def test_storage_write_same_transaction(self):
        """Test multiple storage writes within same transaction."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_storage_write(
            Addresses.ALICE, StorageSlots.SLOT_1, TxIndices.TX_0, StorageValues.VALUE_1
        )
        bal.add_storage_write(
            Addresses.ALICE, StorageSlots.SLOT_2, TxIndices.TX_0, StorageValues.VALUE_2
        )

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.storage_changes) == 2
        assert {sc.slot for sc in account.storage_changes} == {
            StorageSlots.SLOT_1,
            StorageSlots.SLOT_2,
        }
        assert account.storage_changes[0].changes[0].tx_index == TxIndices.TX_0
        assert account.storage_changes[1].changes[0].tx_index == TxIndices.TX_0

    def test_storage_write_different_transactions(self):
        """Test same storage operation across multiple transactions."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_storage_write(
            Addresses.ALICE, StorageSlots.SLOT_1, TxIndices.TX_0, StorageValues.VALUE_1
        )
        bal.add_storage_write(
            Addresses.ALICE, StorageSlots.SLOT_1, TxIndices.TX_1, StorageValues.VALUE_2
        )

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.storage_changes) == 1
        slot_changes = account.storage_changes[0]
        assert len(slot_changes.changes) == 2
        assert slot_changes.changes[0].tx_index == TxIndices.TX_0
        assert slot_changes.changes[1].tx_index == TxIndices.TX_1

    # 3. Deduplication Logic Testing

    def test_storage_write_same_transaction_duplicates(self):
        """Test storage write deduplication within same transaction (last write wins)."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_storage_write(
            Addresses.ALICE, StorageSlots.SLOT_1, TxIndices.TX_0, StorageValues.VALUE_1
        )
        bal.add_storage_write(
            Addresses.ALICE, StorageSlots.SLOT_1, TxIndices.TX_0, StorageValues.VALUE_2
        )

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.storage_changes) == 1
        slot_changes = account.storage_changes[0]
        assert len(slot_changes.changes) == 1
        assert slot_changes.changes[0].tx_index == TxIndices.TX_0
        assert slot_changes.changes[0].new_value == StorageValues.VALUE_2

    def test_storage_read_same_transaction_duplicates(self):
        """Test storage read deduplication within same transaction (no duplication)."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_storage_read(Addresses.ALICE, StorageSlots.SLOT_1)
        bal.add_storage_read(Addresses.ALICE, StorageSlots.SLOT_1)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.storage_reads) == 1

    def test_storage_read_cross_transaction_duplicates(self):
        """Test storage read deduplication across transactions (no duplication)."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_storage_read(Addresses.ALICE, StorageSlots.SLOT_1)
        bal.add_storage_read(Addresses.ALICE, StorageSlots.SLOT_1)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.storage_reads) == 1

    def test_storage_write_same_transactions_multiple_unique_entries(self):
        """Test same storage operation multiple times in same transaction with unique slots."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_storage_write(
            Addresses.ALICE, StorageSlots.SLOT_1, TxIndices.TX_0, StorageValues.VALUE_1
        )
        bal.add_storage_write(
            Addresses.ALICE, StorageSlots.SLOT_2, TxIndices.TX_0, StorageValues.VALUE_1
        )
        bal.add_storage_write(
            Addresses.ALICE, StorageSlots.SLOT_3, TxIndices.TX_0, StorageValues.VALUE_1
        )

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.storage_changes) == 3
        slots = {sc.slot for sc in account.storage_changes}
        assert slots == {StorageSlots.SLOT_1, StorageSlots.SLOT_2, StorageSlots.SLOT_3}

    def test_storage_write_different_transactions_multiple_unique_entries(self):
        """Test same storage operation multiple times across transactions with unique slots."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_storage_write(
            Addresses.ALICE, StorageSlots.SLOT_1, TxIndices.TX_0, StorageValues.VALUE_1
        )
        bal.add_storage_write(
            Addresses.ALICE, StorageSlots.SLOT_2, TxIndices.TX_1, StorageValues.VALUE_1
        )

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.storage_changes) == 2
        slots = {sc.slot for sc in account.storage_changes}
        assert slots == {StorageSlots.SLOT_1, StorageSlots.SLOT_2}

    # 4. Operation Type Coverage

    def test_storage_read_operations(self):
        """Test read-only storage operations."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_storage_read(Addresses.ALICE, StorageSlots.SLOT_1)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.storage_reads) == 1
        assert len(account.storage_changes) == 0
        assert account.storage_reads[0].slot == StorageSlots.SLOT_1

    def test_storage_write_operations(self):
        """Test write storage operations."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_storage_write(
            Addresses.ALICE, StorageSlots.SLOT_1, TxIndices.TX_0, StorageValues.VALUE_2
        )

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.storage_changes) == 1
        assert len(account.storage_reads) == 0
        assert account.storage_changes[0].slot == StorageSlots.SLOT_1

    def test_storage_mixed_operations(self):
        """Test combination of storage reads and writes."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_storage_write(
            Addresses.ALICE, StorageSlots.SLOT_1, TxIndices.TX_0, StorageValues.VALUE_2
        )
        bal.add_storage_read(Addresses.ALICE, StorageSlots.SLOT_1)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.storage_reads) == 1
        assert len(account.storage_changes) == 1
        assert account.storage_reads[0].slot == StorageSlots.SLOT_1
        assert account.storage_changes[0].slot == StorageSlots.SLOT_1

    # 5. Field Interaction Testing (handled in TestMixedOperations)

    # 6. Edge Case Coverage

    def test_storage_read_write_interactions(self):
        """Test interactions between read and write operations on same slot."""
        # Arrange
        bal = BlockAccessList()

        # Act - Read first, then write
        bal.add_storage_read(Addresses.ALICE, StorageSlots.SLOT_1)
        bal.add_storage_write(
            Addresses.ALICE, StorageSlots.SLOT_1, TxIndices.TX_0, StorageValues.VALUE_2
        )

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.storage_reads) == 1
        assert len(account.storage_changes) == 1
        assert account.storage_reads[0].slot == StorageSlots.SLOT_1
        assert account.storage_changes[0].slot == StorageSlots.SLOT_1

    def test_storage_empty_operations(self):
        """Test behavior with zero storage values."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_storage_write(
            Addresses.ALICE,
            StorageSlots.SLOT_1,
            TxIndices.TX_0,
            StorageValues.ZERO_VALUE,
        )

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.storage_changes) == 1
        assert (
            account.storage_changes[0].changes[0].new_value == StorageValues.ZERO_VALUE
        )

    def test_storage_boundary_conditions(self):
        """Test boundary conditions for storage operations."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_storage_write(
            Addresses.ALICE,
            StorageSlots.MAX_SLOT,
            TxIndices.TX_0,
            StorageValues.MAX_VALUE,
        )
        bal.add_storage_write(
            Addresses.ALICE,
            StorageSlots.MIN_SLOT,
            TxIndices.TX_0,
            StorageValues.ZERO_VALUE,
        )
        bal.add_storage_read(Addresses.ALICE, StorageSlots.MAX_SLOT)
        bal.add_storage_read(Addresses.ALICE, StorageSlots.MIN_SLOT)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.storage_changes) == 2
        assert len(account.storage_reads) == 2
        slots_written = {sc.slot for sc in account.storage_changes}
        slots_read = {sr.slot for sr in account.storage_reads}
        assert slots_written == {StorageSlots.MAX_SLOT, StorageSlots.MIN_SLOT}
        assert slots_read == {StorageSlots.MAX_SLOT, StorageSlots.MIN_SLOT}


class TestBalanceOperations:
    """Test cases for balance operations."""

    def test_add_balance_change(self):
        """Test adding balance change."""
        bal = BlockAccessList()

        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_0, Balances.BALANCE_1000)

        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.balance_changes) == 1
        assert account.balance_changes[0].tx_index == TxIndices.TX_0
        assert account.balance_changes[0].post_balance == Balances.BALANCE_1000


class TestNonceOperations:
    """Test cases for nonce operations."""

    def test_add_nonce_change(self):
        """Test adding nonce change."""
        bal = BlockAccessList()

        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_0, Nonces.NONCE_42)

        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.nonce_changes) == 1
        assert account.nonce_changes[0].tx_index == TxIndices.TX_0
        assert account.nonce_changes[0].new_nonce == Nonces.NONCE_42


class TestCodeOperations:
    """Test cases for code operations."""

    def test_add_code_change(self):
        """Test adding code change."""
        bal = BlockAccessList()

        bal.add_code_change(Addresses.ALICE, TxIndices.TX_0, CodeSamples.SIMPLE_CODE)

        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.code_changes) == 1
        assert account.code_changes[0].tx_index == TxIndices.TX_0
        assert account.code_changes[0].new_code == CodeSamples.SIMPLE_CODE


class TestMixedOperations:
    """Test cases for mixed operations."""

    def test_mixed_operations_same_account(self):
        """Test multiple different operations on the same account."""
        bal = BlockAccessList()

        bal.add_storage_write(
            Addresses.ALICE, StorageSlots.SLOT_1, TxIndices.TX_0, StorageValues.VALUE_2
        )
        bal.add_storage_read(Addresses.ALICE, StorageSlots.SLOT_1)
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_0, Balances.BALANCE_1000)
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_0, Nonces.NONCE_42)
        bal.add_code_change(Addresses.ALICE, TxIndices.TX_0, CodeSamples.ANOTHER_CODE)

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

        bal.add_storage_write(
            Addresses.BOB, StorageSlots.SLOT_1, TxIndices.TX_0, StorageValues.VALUE_2
        )
        bal.add_storage_write(
            Addresses.CAROL, StorageSlots.SLOT_1, TxIndices.TX_0, StorageValues.VALUE_2
        )

        assert len(bal.account_changes) == 2
        addresses = {account.address for account in bal.account_changes}
        assert addresses == {Addresses.BOB, Addresses.CAROL}
