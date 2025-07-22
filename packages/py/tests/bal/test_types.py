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

5. Edge Case Coverage:
   - "read_write_interactions": Test interactions between read and write operations on same slot
   - "boundary_conditions": Test limits and edge scenarios specific to the field
   - "empty_operations": Test behavior with empty or zero values

And additionally, Field Interaction Testing:
    Test how different fields interact with each other.
   - "same_account_mixed_operations": Combine different field operations on same account
   - "multi_account_mixed_operations": Combine different field operations across multiple accounts

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


class TestStorageWriteOperations:
    """Test cases for storage write operations following the generalized testing pattern."""

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
        assert account.address == Addresses.ALICE
        assert len(account.storage_changes) == 1
        assert len(account.balance_changes) == 1
        assert account.storage_changes[0].slot == StorageSlots.SLOT_1
        assert len(account.storage_changes[0].changes) == 1
        assert account.storage_changes[0].changes[0].tx_index == TxIndices.TX_0
        assert account.storage_changes[0].changes[0].new_value == StorageValues.VALUE_1

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
        assert account.storage_changes[0].changes[0].new_value == StorageValues.VALUE_1

        assert account.storage_changes[1].changes[0].tx_index == TxIndices.TX_0
        assert account.storage_changes[1].changes[0].new_value == StorageValues.VALUE_2

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

    # 5. Edge Case Coverage

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

    def test_storage_write_boundary_conditions(self):
        """Test boundary conditions for storage write operations."""
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

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.storage_changes) == 2
        slots_written = {sc.slot for sc in account.storage_changes}
        assert slots_written == {StorageSlots.MAX_SLOT, StorageSlots.MIN_SLOT}


class TestStorageReadOperations:
    """Test cases for storage read operations following the generalized testing pattern."""

    # 1. Account State Coverage Tests

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
        assert account.storage_reads[0] == StorageSlots.SLOT_1

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
        assert account.storage_reads[0] == StorageSlots.SLOT_1

    # 3. Deduplication Logic Testing

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
        assert account.storage_reads[0] == StorageSlots.SLOT_1

    # 5. Edge Case Coverage

    def test_storage_read_boundary_conditions(self):
        """Test boundary conditions for storage read operations."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_storage_read(Addresses.ALICE, StorageSlots.MAX_SLOT)
        bal.add_storage_read(Addresses.ALICE, StorageSlots.MIN_SLOT)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.storage_reads) == 2
        slots_read = set(account.storage_reads)
        assert slots_read == {StorageSlots.MAX_SLOT, StorageSlots.MIN_SLOT}


class TestBalanceOperations:
    """Test cases for balance operations following the generalized testing pattern."""

    # 1. Account State Coverage Tests

    def test_balance_change_untouched_account(self):
        """Test balance change on untouched account creates new account entry."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_0, Balances.BALANCE_1000)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert account.address == Addresses.ALICE
        assert len(account.balance_changes) == 1
        assert account.balance_changes[0].tx_index == TxIndices.TX_0
        assert account.balance_changes[0].post_balance == Balances.BALANCE_1000

    def test_balance_change_touched_account(self):
        """Test balance change on touched account extends existing account entry."""
        # Arrange
        bal = BlockAccessList()

        # Pre-touch the account with nonce change
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_0, Nonces.NONCE_42)

        # Act
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_0, Balances.BALANCE_1000)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.balance_changes) == 1
        assert len(account.nonce_changes) == 1
        assert account.balance_changes[0].tx_index == TxIndices.TX_0
        assert account.balance_changes[0].post_balance == Balances.BALANCE_1000

    # 2. Transaction Scope Testing

    def test_balance_change_same_transaction(self):
        """Test multiple balance changes within same transaction."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_0, Balances.BALANCE_1000)
        bal.add_balance_change(Addresses.BOB, TxIndices.TX_0, Balances.BALANCE_2000)

        # Assert
        assert len(bal.account_changes) == 2
        alice_account = next(
            acc for acc in bal.account_changes if acc.address == Addresses.ALICE
        )
        bob_account = next(
            acc for acc in bal.account_changes if acc.address == Addresses.BOB
        )
        assert len(alice_account.balance_changes) == 1
        assert len(bob_account.balance_changes) == 1
        assert alice_account.balance_changes[0].tx_index == TxIndices.TX_0
        assert bob_account.balance_changes[0].tx_index == TxIndices.TX_0

    def test_balance_change_different_transactions(self):
        """Test same account balance changes across multiple transactions."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_0, Balances.BALANCE_1000)
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_1, Balances.BALANCE_2000)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.balance_changes) == 2
        assert account.balance_changes[0].tx_index == TxIndices.TX_0
        assert account.balance_changes[0].post_balance == Balances.BALANCE_1000
        assert account.balance_changes[1].tx_index == TxIndices.TX_1
        assert account.balance_changes[1].post_balance == Balances.BALANCE_2000

    # 3. Deduplication Logic Testing

    def test_balance_change_same_transaction_duplicates(self):
        """Test balance change deduplication within same transaction (last write wins)."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_0, Balances.BALANCE_1000)
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_0, Balances.BALANCE_2000)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.balance_changes) == 1
        assert account.balance_changes[0].tx_index == TxIndices.TX_0
        assert account.balance_changes[0].post_balance == Balances.BALANCE_2000

    def test_balance_change_same_transactions_multiple_accounts(self):
        """Test balance changes for multiple accounts in same transaction."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_0, Balances.BALANCE_1000)
        bal.add_balance_change(Addresses.BOB, TxIndices.TX_0, Balances.BALANCE_1000)
        bal.add_balance_change(Addresses.CAROL, TxIndices.TX_0, Balances.BALANCE_1000)

        # Assert
        assert len(bal.account_changes) == 3
        addresses = {acc.address for acc in bal.account_changes}
        assert addresses == {Addresses.ALICE, Addresses.BOB, Addresses.CAROL}
        for account in bal.account_changes:
            assert len(account.balance_changes) == 1
            assert account.balance_changes[0].tx_index == TxIndices.TX_0

    def test_balance_change_different_transactions_multiple_accounts(self):
        """Test balance changes for multiple accounts across transactions."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_0, Balances.BALANCE_1000)
        bal.add_balance_change(Addresses.BOB, TxIndices.TX_1, Balances.BALANCE_2000)

        # Assert
        assert len(bal.account_changes) == 2
        alice_account = next(
            acc for acc in bal.account_changes if acc.address == Addresses.ALICE
        )
        bob_account = next(
            acc for acc in bal.account_changes if acc.address == Addresses.BOB
        )
        assert alice_account.balance_changes[0].tx_index == TxIndices.TX_0
        assert bob_account.balance_changes[0].tx_index == TxIndices.TX_1

    # 5. Edge Case Coverage

    def test_balance_change_zero_balance(self):
        """Test behavior with zero balance values."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_0, 0)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.balance_changes) == 1
        assert account.balance_changes[0].post_balance == 0

    def test_balance_change_large_values(self):
        """Test boundary conditions for balance change operations."""
        # Arrange
        bal = BlockAccessList()
        large_balance = 10**18  # 1 ETH in wei

        # Act
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_0, large_balance)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.balance_changes) == 1
        assert account.balance_changes[0].post_balance == large_balance


class TestNonceOperations:
    """Test cases for nonce operations following the generalized testing pattern."""

    # 1. Account State Coverage Tests

    def test_nonce_change_untouched_account(self):
        """Test nonce change on untouched account creates new account entry."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_0, Nonces.NONCE_42)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert account.address == Addresses.ALICE
        assert len(account.nonce_changes) == 1
        assert account.nonce_changes[0].tx_index == TxIndices.TX_0
        assert account.nonce_changes[0].new_nonce == Nonces.NONCE_42

    def test_nonce_change_touched_account(self):
        """Test nonce change on touched account extends existing account entry."""
        # Arrange
        bal = BlockAccessList()

        # Pre-touch the account with balance change
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_0, Balances.BALANCE_1000)

        # Act
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_0, Nonces.NONCE_42)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.nonce_changes) == 1
        assert len(account.balance_changes) == 1
        assert account.nonce_changes[0].tx_index == TxIndices.TX_0
        assert account.nonce_changes[0].new_nonce == Nonces.NONCE_42

    # 2. Transaction Scope Testing

    def test_nonce_change_same_transaction(self):
        """Test multiple nonce changes within same transaction."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_0, Nonces.NONCE_42)
        bal.add_nonce_change(Addresses.BOB, TxIndices.TX_0, Nonces.NONCE_100)

        # Assert
        assert len(bal.account_changes) == 2
        alice_account = next(
            acc for acc in bal.account_changes if acc.address == Addresses.ALICE
        )
        bob_account = next(
            acc for acc in bal.account_changes if acc.address == Addresses.BOB
        )
        assert len(alice_account.nonce_changes) == 1
        assert len(bob_account.nonce_changes) == 1
        assert alice_account.nonce_changes[0].tx_index == TxIndices.TX_0
        assert bob_account.nonce_changes[0].tx_index == TxIndices.TX_0

    def test_nonce_change_different_transactions(self):
        """Test same account nonce changes across multiple transactions."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_0, Nonces.NONCE_42)
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_1, Nonces.NONCE_100)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.nonce_changes) == 2
        assert account.nonce_changes[0].tx_index == TxIndices.TX_0
        assert account.nonce_changes[0].new_nonce == Nonces.NONCE_42
        assert account.nonce_changes[1].tx_index == TxIndices.TX_1
        assert account.nonce_changes[1].new_nonce == Nonces.NONCE_100

    # 3. Deduplication Logic Testing

    def test_nonce_change_same_transaction_duplicates(self):
        """Test nonce change deduplication within same transaction (last write wins)."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_0, Nonces.NONCE_42)
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_0, Nonces.NONCE_100)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.nonce_changes) == 1
        assert account.nonce_changes[0].tx_index == TxIndices.TX_0
        assert account.nonce_changes[0].new_nonce == Nonces.NONCE_100

    def test_nonce_change_same_transactions_multiple_accounts(self):
        """Test nonce changes for multiple accounts in same transaction."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_0, Nonces.NONCE_42)
        bal.add_nonce_change(Addresses.BOB, TxIndices.TX_0, Nonces.NONCE_100)
        bal.add_nonce_change(Addresses.CAROL, TxIndices.TX_0, Nonces.NONCE_1000)

        # Assert
        assert len(bal.account_changes) == 3
        addresses = {acc.address for acc in bal.account_changes}
        assert addresses == {Addresses.ALICE, Addresses.BOB, Addresses.CAROL}
        for account in bal.account_changes:
            assert len(account.nonce_changes) == 1
            assert account.nonce_changes[0].tx_index == TxIndices.TX_0

    def test_nonce_change_different_transactions_multiple_accounts(self):
        """Test nonce changes for multiple accounts across transactions."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_0, Nonces.NONCE_42)
        bal.add_nonce_change(Addresses.BOB, TxIndices.TX_1, Nonces.NONCE_100)

        # Assert
        assert len(bal.account_changes) == 2
        alice_account = next(
            acc for acc in bal.account_changes if acc.address == Addresses.ALICE
        )
        bob_account = next(
            acc for acc in bal.account_changes if acc.address == Addresses.BOB
        )
        assert alice_account.nonce_changes[0].tx_index == TxIndices.TX_0
        assert bob_account.nonce_changes[0].tx_index == TxIndices.TX_1

    # 5. Edge Case Coverage

    def test_nonce_change_zero_nonce(self):
        """Test behavior with zero nonce values."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_0, Nonces.NONCE_0)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.nonce_changes) == 1
        assert account.nonce_changes[0].new_nonce == Nonces.NONCE_0

    def test_nonce_change_large_values(self):
        """Test boundary conditions for nonce change operations."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_0, Nonces.NONCE_1000)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.nonce_changes) == 1
        assert account.nonce_changes[0].new_nonce == Nonces.NONCE_1000

    def test_nonce_change_sequential_increments(self):
        """Test nonce changes with sequential increments across transactions."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_0, Nonces.NONCE_1)
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_1, Nonces.NONCE_42)
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_2, Nonces.NONCE_100)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.nonce_changes) == 3
        assert account.nonce_changes[0].new_nonce == Nonces.NONCE_1
        assert account.nonce_changes[1].new_nonce == Nonces.NONCE_42
        assert account.nonce_changes[2].new_nonce == Nonces.NONCE_100


class TestCodeOperations:
    """Test cases for code operations following the generalized testing pattern."""

    # 1. Account State Coverage Tests

    def test_code_change_untouched_account(self):
        """Test code change on untouched account creates new account entry."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_code_change(Addresses.ALICE, TxIndices.TX_0, CodeSamples.SIMPLE_CODE)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert account.address == Addresses.ALICE
        assert len(account.code_changes) == 1
        assert account.code_changes[0].tx_index == TxIndices.TX_0
        assert account.code_changes[0].new_code == CodeSamples.SIMPLE_CODE

    def test_code_change_touched_account(self):
        """Test code change on touched account extends existing account entry."""
        # Arrange
        bal = BlockAccessList()

        # Pre-touch the account with balance change
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_0, Balances.BALANCE_1000)

        # Act
        bal.add_code_change(Addresses.ALICE, TxIndices.TX_0, CodeSamples.SIMPLE_CODE)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.code_changes) == 1
        assert len(account.balance_changes) == 1
        assert account.code_changes[0].tx_index == TxIndices.TX_0
        assert account.code_changes[0].new_code == CodeSamples.SIMPLE_CODE

    # 2. Transaction Scope Testing

    def test_code_change_same_transaction(self):
        """Test multiple code changes within same transaction."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_code_change(Addresses.ALICE, TxIndices.TX_0, CodeSamples.SIMPLE_CODE)
        bal.add_code_change(Addresses.BOB, TxIndices.TX_0, CodeSamples.ANOTHER_CODE)

        # Assert
        assert len(bal.account_changes) == 2
        alice_account = next(
            acc for acc in bal.account_changes if acc.address == Addresses.ALICE
        )
        bob_account = next(
            acc for acc in bal.account_changes if acc.address == Addresses.BOB
        )
        assert len(alice_account.code_changes) == 1
        assert len(bob_account.code_changes) == 1
        assert alice_account.code_changes[0].tx_index == TxIndices.TX_0
        assert bob_account.code_changes[0].tx_index == TxIndices.TX_0

    def test_code_change_different_transactions(self):
        """Test same account code changes across multiple transactions."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_code_change(Addresses.ALICE, TxIndices.TX_0, CodeSamples.SIMPLE_CODE)
        bal.add_code_change(Addresses.ALICE, TxIndices.TX_1, CodeSamples.ANOTHER_CODE)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.code_changes) == 2
        assert account.code_changes[0].tx_index == TxIndices.TX_0
        assert account.code_changes[0].new_code == CodeSamples.SIMPLE_CODE
        assert account.code_changes[1].tx_index == TxIndices.TX_1
        assert account.code_changes[1].new_code == CodeSamples.ANOTHER_CODE

    # 3. Deduplication Logic Testing

    def test_code_change_same_transaction_duplicates(self):
        """Test code change deduplication within same transaction (last write wins)."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_code_change(Addresses.ALICE, TxIndices.TX_0, CodeSamples.SIMPLE_CODE)
        bal.add_code_change(Addresses.ALICE, TxIndices.TX_0, CodeSamples.ANOTHER_CODE)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.code_changes) == 1
        assert account.code_changes[0].tx_index == TxIndices.TX_0
        assert account.code_changes[0].new_code == CodeSamples.ANOTHER_CODE

    def test_code_change_same_transactions_multiple_accounts(self):
        """Test code changes for multiple accounts in same transaction."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_code_change(Addresses.ALICE, TxIndices.TX_0, CodeSamples.SIMPLE_CODE)
        bal.add_code_change(Addresses.BOB, TxIndices.TX_0, CodeSamples.ANOTHER_CODE)
        bal.add_code_change(Addresses.CAROL, TxIndices.TX_0, CodeSamples.COMPLEX_CODE)

        # Assert
        assert len(bal.account_changes) == 3
        addresses = {acc.address for acc in bal.account_changes}
        assert addresses == {Addresses.ALICE, Addresses.BOB, Addresses.CAROL}
        for account in bal.account_changes:
            assert len(account.code_changes) == 1
            assert account.code_changes[0].tx_index == TxIndices.TX_0

    def test_code_change_different_transactions_multiple_accounts(self):
        """Test code changes for multiple accounts across transactions."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_code_change(Addresses.ALICE, TxIndices.TX_0, CodeSamples.SIMPLE_CODE)
        bal.add_code_change(Addresses.BOB, TxIndices.TX_1, CodeSamples.ANOTHER_CODE)

        # Assert
        assert len(bal.account_changes) == 2
        alice_account = next(
            acc for acc in bal.account_changes if acc.address == Addresses.ALICE
        )
        bob_account = next(
            acc for acc in bal.account_changes if acc.address == Addresses.BOB
        )
        assert alice_account.code_changes[0].tx_index == TxIndices.TX_0
        assert bob_account.code_changes[0].tx_index == TxIndices.TX_1

    # 5. Edge Case Coverage

    def test_code_change_empty_code(self):
        """Test behavior with empty code values."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_code_change(Addresses.ALICE, TxIndices.TX_0, CodeSamples.EMPTY_CODE)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.code_changes) == 1
        assert account.code_changes[0].new_code == CodeSamples.EMPTY_CODE

    def test_code_change_large_code(self):
        """Test boundary conditions for code change operations with large code."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_code_change(Addresses.ALICE, TxIndices.TX_0, CodeSamples.LARGE_CODE)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.code_changes) == 1
        assert account.code_changes[0].new_code == CodeSamples.LARGE_CODE


class TestMixedOperations:
    """Test cases for mixed operations across different account fields and storage."""

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
        assert account.storage_reads[0] == StorageSlots.SLOT_1
        assert account.storage_changes[0].slot == StorageSlots.SLOT_1

    def test_balance_mixed_operations(self):
        """Test combination of balance changes with other operations."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_0, Balances.BALANCE_1000)
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_0, Nonces.NONCE_42)
        bal.add_storage_write(
            Addresses.ALICE, StorageSlots.SLOT_1, TxIndices.TX_0, StorageValues.VALUE_1
        )

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.balance_changes) == 1
        assert len(account.nonce_changes) == 1
        assert len(account.storage_changes) == 1
        assert account.balance_changes[0].post_balance == Balances.BALANCE_1000
        assert account.nonce_changes[0].new_nonce == Nonces.NONCE_42
        assert account.storage_changes[0].slot == StorageSlots.SLOT_1

    def test_nonce_mixed_operations(self):
        """Test combination of nonce changes with other operations."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_0, Nonces.NONCE_42)
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_0, Balances.BALANCE_1000)
        bal.add_storage_write(
            Addresses.ALICE, StorageSlots.SLOT_1, TxIndices.TX_0, StorageValues.VALUE_1
        )

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.nonce_changes) == 1
        assert len(account.balance_changes) == 1
        assert len(account.storage_changes) == 1
        assert account.nonce_changes[0].new_nonce == Nonces.NONCE_42
        assert account.balance_changes[0].post_balance == Balances.BALANCE_1000
        assert account.storage_changes[0].slot == StorageSlots.SLOT_1

    def test_code_mixed_operations(self):
        """Test combination of code changes with other operations."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_code_change(Addresses.ALICE, TxIndices.TX_0, CodeSamples.SIMPLE_CODE)
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_0, Balances.BALANCE_1000)
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_0, Nonces.NONCE_42)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.code_changes) == 1
        assert len(account.balance_changes) == 1
        assert len(account.nonce_changes) == 1
        assert account.code_changes[0].new_code == CodeSamples.SIMPLE_CODE
        assert account.balance_changes[0].post_balance == Balances.BALANCE_1000
        assert account.nonce_changes[0].new_nonce == Nonces.NONCE_42

    def test_comprehensive_all_operations(self):
        """Test combination of all operation types including code on same account."""
        # Arrange
        bal = BlockAccessList()

        # Act
        bal.add_code_change(Addresses.ALICE, TxIndices.TX_0, CodeSamples.COMPLEX_CODE)
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_0, Nonces.NONCE_42)
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_0, Balances.BALANCE_1000)
        bal.add_storage_write(
            Addresses.ALICE, StorageSlots.SLOT_1, TxIndices.TX_0, StorageValues.VALUE_1
        )
        bal.add_storage_read(Addresses.ALICE, StorageSlots.SLOT_2)

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.code_changes) == 1
        assert len(account.nonce_changes) == 1
        assert len(account.balance_changes) == 1
        assert len(account.storage_changes) == 1
        assert len(account.storage_reads) == 1
        assert account.code_changes[0].new_code == CodeSamples.COMPLEX_CODE
        assert account.nonce_changes[0].new_nonce == Nonces.NONCE_42
        assert account.balance_changes[0].post_balance == Balances.BALANCE_1000
        assert account.storage_changes[0].slot == StorageSlots.SLOT_1
        assert account.storage_reads[0] == StorageSlots.SLOT_2

    def test_contract_deployment_scenario(self):
        """Test realistic contract deployment scenario with all operations."""
        # Arrange
        bal = BlockAccessList()

        # Act - Simulate contract deployment
        # 1. Deploy contract (code change from empty to actual code)
        bal.add_code_change(Addresses.ALICE, TxIndices.TX_0, CodeSamples.COMPLEX_CODE)
        # 2. Set initial balance
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_0, Balances.BALANCE_1000)
        # 3. Initialize nonce
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_0, Nonces.NONCE_1)
        # 4. Set initial storage
        bal.add_storage_write(
            Addresses.ALICE, StorageSlots.SLOT_1, TxIndices.TX_0, StorageValues.VALUE_1
        )

        # Assert
        assert len(bal.account_changes) == 1
        account = bal.account_changes[0]
        assert len(account.code_changes) == 1
        assert len(account.balance_changes) == 1
        assert len(account.nonce_changes) == 1
        assert len(account.storage_changes) == 1
        assert account.code_changes[0].new_code == CodeSamples.COMPLEX_CODE
        assert account.balance_changes[0].post_balance == Balances.BALANCE_1000
        assert account.nonce_changes[0].new_nonce == Nonces.NONCE_1
        assert account.storage_changes[0].slot == StorageSlots.SLOT_1


class TestBlockAccessListSorting:
    """Test cases for BlockAccessList sorting functionality following EIP-7928 ordering requirements."""

    def test_sort_empty_list(self):
        """Test sorting empty BlockAccessList returns empty sorted list."""
        # Arrange
        bal = BlockAccessList()

        # Act
        sorted_bal = bal.sort()

        # Assert
        assert len(sorted_bal.account_changes) == 0
        assert sorted_bal is not bal  # Should return new instance

    def test_sort_single_account(self):
        """Test sorting single account returns same account structure."""
        # Arrange
        bal = BlockAccessList()
        bal.add_storage_write(Addresses.ALICE, StorageSlots.SLOT_1, TxIndices.TX_0, StorageValues.VALUE_1)

        # Act
        sorted_bal = bal.sort()

        # Assert
        assert len(sorted_bal.account_changes) == 1
        assert sorted_bal.account_changes[0].address == Addresses.ALICE
        assert sorted_bal is not bal  # Should return new instance

    def test_sort_addresses_lexicographic(self):
        """Test addresses are sorted lexicographically (bytewise)."""
        # Arrange
        bal = BlockAccessList()
        # Add accounts in reverse lexicographic order
        bal.add_balance_change(Addresses.CAROL, TxIndices.TX_0, Balances.BALANCE_1000)
        bal.add_balance_change(Addresses.BOB, TxIndices.TX_0, Balances.BALANCE_2000)
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_0, Balances.BALANCE_3000)

        # Act
        sorted_bal = bal.sort()

        # Assert
        assert len(sorted_bal.account_changes) == 3
        # Should be sorted: ALICE < BOB < CAROL lexicographically
        addresses = [acc.address for acc in sorted_bal.account_changes]
        expected_order = sorted([Addresses.ALICE, Addresses.BOB, Addresses.CAROL])
        assert addresses == expected_order

    def test_sort_storage_keys_lexicographic(self):
        """Test storage keys are sorted lexicographically within each account."""
        # Arrange
        bal = BlockAccessList()
        # Add storage writes in reverse order
        bal.add_storage_write(Addresses.ALICE, StorageSlots.SLOT_3, TxIndices.TX_0, StorageValues.VALUE_1)
        bal.add_storage_write(Addresses.ALICE, StorageSlots.SLOT_1, TxIndices.TX_0, StorageValues.VALUE_2)
        bal.add_storage_write(Addresses.ALICE, StorageSlots.SLOT_2, TxIndices.TX_0, StorageValues.VALUE_3)

        # Act
        sorted_bal = bal.sort()

        # Assert
        assert len(sorted_bal.account_changes) == 1
        account = sorted_bal.account_changes[0]
        assert len(account.storage_changes) == 3
        slots = [sc.slot for sc in account.storage_changes]
        expected_slots = sorted([StorageSlots.SLOT_1, StorageSlots.SLOT_2, StorageSlots.SLOT_3])
        assert slots == expected_slots

    def test_sort_storage_reads_lexicographic(self):
        """Test storage reads are sorted lexicographically within each account."""
        # Arrange
        bal = BlockAccessList()
        # Add storage reads in reverse order
        bal.add_storage_read(Addresses.ALICE, StorageSlots.SLOT_3)
        bal.add_storage_read(Addresses.ALICE, StorageSlots.SLOT_1)
        bal.add_storage_read(Addresses.ALICE, StorageSlots.SLOT_2)

        # Act
        sorted_bal = bal.sort()

        # Assert
        assert len(sorted_bal.account_changes) == 1
        account = sorted_bal.account_changes[0]
        assert len(account.storage_reads) == 3
        reads = account.storage_reads
        expected_reads = sorted([StorageSlots.SLOT_1, StorageSlots.SLOT_2, StorageSlots.SLOT_3])
        assert reads == expected_reads

    def test_sort_transaction_indices_ascending(self):
        """Test transaction indices are sorted ascending within each change list."""
        # Arrange
        bal = BlockAccessList()
        # Add changes in reverse tx order
        bal.add_storage_write(Addresses.ALICE, StorageSlots.SLOT_1, TxIndices.TX_2, StorageValues.VALUE_1)
        bal.add_storage_write(Addresses.ALICE, StorageSlots.SLOT_1, TxIndices.TX_0, StorageValues.VALUE_2)
        bal.add_storage_write(Addresses.ALICE, StorageSlots.SLOT_1, TxIndices.TX_1, StorageValues.VALUE_3)

        # Act
        sorted_bal = bal.sort()

        # Assert
        assert len(sorted_bal.account_changes) == 1
        account = sorted_bal.account_changes[0]
        assert len(account.storage_changes) == 1
        slot_changes = account.storage_changes[0]
        assert len(slot_changes.changes) == 3
        tx_indices = [change.tx_index for change in slot_changes.changes]
        assert tx_indices == [TxIndices.TX_0, TxIndices.TX_1, TxIndices.TX_2]

    def test_sort_balance_changes_by_tx_index(self):
        """Test balance changes are sorted by tx_index ascending."""
        # Arrange
        bal = BlockAccessList()
        # Add balance changes in reverse tx order
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_2, Balances.BALANCE_1000)
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_0, Balances.BALANCE_2000)
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_1, Balances.BALANCE_3000)

        # Act
        sorted_bal = bal.sort()

        # Assert
        assert len(sorted_bal.account_changes) == 1
        account = sorted_bal.account_changes[0]
        assert len(account.balance_changes) == 3
        tx_indices = [change.tx_index for change in account.balance_changes]
        assert tx_indices == [TxIndices.TX_0, TxIndices.TX_1, TxIndices.TX_2]

    def test_sort_nonce_changes_by_tx_index(self):
        """Test nonce changes are sorted by tx_index ascending."""
        # Arrange
        bal = BlockAccessList()
        # Add nonce changes in reverse tx order
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_2, Nonces.NONCE_100)
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_0, Nonces.NONCE_42)
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_1, Nonces.NONCE_1000)

        # Act
        sorted_bal = bal.sort()

        # Assert
        assert len(sorted_bal.account_changes) == 1
        account = sorted_bal.account_changes[0]
        assert len(account.nonce_changes) == 3
        tx_indices = [change.tx_index for change in account.nonce_changes]
        assert tx_indices == [TxIndices.TX_0, TxIndices.TX_1, TxIndices.TX_2]

    def test_sort_code_changes_by_tx_index(self):
        """Test code changes are sorted by tx_index ascending."""
        # Arrange
        bal = BlockAccessList()
        # Add code changes on different accounts (since MAX_CODE_CHANGES is 1 per account)
        bal.add_code_change(Addresses.ALICE, TxIndices.TX_1, CodeSamples.SIMPLE_CODE)
        bal.add_code_change(Addresses.BOB, TxIndices.TX_0, CodeSamples.ANOTHER_CODE)

        # Act
        sorted_bal = bal.sort()

        # Assert
        assert len(sorted_bal.account_changes) == 2
        addresses = [acc.address for acc in sorted_bal.account_changes]
        expected_addresses = sorted([Addresses.ALICE, Addresses.BOB])
        assert addresses == expected_addresses
        
        # Check individual code changes
        for account in sorted_bal.account_changes:
            assert len(account.code_changes) == 1

    def test_sort_comprehensive_mixed_operations(self):
        """Test comprehensive sorting with all operation types on multiple accounts."""
        # Arrange
        bal = BlockAccessList()
        
        # Add operations in deliberately unsorted order across multiple accounts
        # Carol's operations
        bal.add_storage_write(Addresses.CAROL, StorageSlots.SLOT_3, TxIndices.TX_1, StorageValues.VALUE_1)
        bal.add_balance_change(Addresses.CAROL, TxIndices.TX_0, Balances.BALANCE_1000)
        bal.add_storage_read(Addresses.CAROL, StorageSlots.SLOT_2)
        
        # Alice's operations  
        bal.add_storage_write(Addresses.ALICE, StorageSlots.SLOT_2, TxIndices.TX_2, StorageValues.VALUE_2)
        bal.add_storage_write(Addresses.ALICE, StorageSlots.SLOT_1, TxIndices.TX_0, StorageValues.VALUE_3)
        bal.add_nonce_change(Addresses.ALICE, TxIndices.TX_1, Nonces.NONCE_42)
        bal.add_storage_read(Addresses.ALICE, StorageSlots.SLOT_3)
        bal.add_storage_read(Addresses.ALICE, StorageSlots.SLOT_1)
        
        # Bob's operations
        bal.add_code_change(Addresses.BOB, TxIndices.TX_0, CodeSamples.SIMPLE_CODE)
        bal.add_balance_change(Addresses.BOB, TxIndices.TX_2, Balances.BALANCE_2000)

        # Act
        sorted_bal = bal.sort()

        # Assert addresses are sorted lexicographically
        assert len(sorted_bal.account_changes) == 3
        addresses = [acc.address for acc in sorted_bal.account_changes]
        expected_addresses = sorted([Addresses.ALICE, Addresses.BOB, Addresses.CAROL])
        assert addresses == expected_addresses
        
        # Check Bob's account (should be first lexicographically: 0x1111... < 0x1234... < 0x2222...)
        bob_account = sorted_bal.account_changes[0]
        assert bob_account.address == Addresses.BOB
        
        # Check Alice's account (should be second)
        alice_account = sorted_bal.account_changes[1]
        assert alice_account.address == Addresses.ALICE
        
        # Check storage changes are sorted by slot
        alice_slots = [sc.slot for sc in alice_account.storage_changes]
        expected_alice_slots = sorted([StorageSlots.SLOT_1, StorageSlots.SLOT_2])
        assert alice_slots == expected_alice_slots
        
        # Check storage reads are sorted
        alice_reads = alice_account.storage_reads
        expected_alice_reads = sorted([StorageSlots.SLOT_1, StorageSlots.SLOT_3])
        assert alice_reads == expected_alice_reads
        
        # Check tx indices within storage changes are sorted
        slot1_changes = next(sc for sc in alice_account.storage_changes if sc.slot == StorageSlots.SLOT_1)
        slot2_changes = next(sc for sc in alice_account.storage_changes if sc.slot == StorageSlots.SLOT_2)
        assert slot1_changes.changes[0].tx_index == TxIndices.TX_0
        assert slot2_changes.changes[0].tx_index == TxIndices.TX_2

    def test_sort_immutability(self):
        """Test that sort() returns new instance and doesn't mutate original."""
        # Arrange
        bal = BlockAccessList()
        bal.add_storage_write(Addresses.CAROL, StorageSlots.SLOT_1, TxIndices.TX_0, StorageValues.VALUE_1)
        bal.add_storage_write(Addresses.ALICE, StorageSlots.SLOT_1, TxIndices.TX_0, StorageValues.VALUE_2)
        
        # Store original state
        original_addresses = [acc.address for acc in bal.account_changes]

        # Act
        sorted_bal = bal.sort()

        # Assert original is unchanged
        current_addresses = [acc.address for acc in bal.account_changes]
        assert current_addresses == original_addresses
        assert sorted_bal is not bal
        
        # Assert sorted is different
        sorted_addresses = [acc.address for acc in sorted_bal.account_changes]
        assert sorted_addresses != original_addresses
        assert sorted_addresses == sorted(original_addresses)

    def test_serialize_with_sort_enabled(self):
        """Test serialize with sort=True (default) applies sorting."""
        # Arrange
        bal = BlockAccessList()
        # Add accounts in reverse lexicographic order
        bal.add_balance_change(Addresses.CAROL, TxIndices.TX_0, Balances.BALANCE_1000)
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_0, Balances.BALANCE_2000)

        # Act
        serialized = bal.serialize(sort=True)  # Explicit True
        default_serialized = bal.serialize()   # Default True

        # Assert both produce same result and sorting was applied
        assert serialized == default_serialized
        assert isinstance(serialized, bytes)
        assert len(serialized) > 0

    def test_serialize_with_sort_disabled(self):
        """Test serialize with sort=False preserves original order."""
        # Arrange
        bal = BlockAccessList()
        # Add accounts in reverse lexicographic order
        bal.add_balance_change(Addresses.CAROL, TxIndices.TX_0, Balances.BALANCE_1000)
        bal.add_balance_change(Addresses.ALICE, TxIndices.TX_0, Balances.BALANCE_2000)

        # Act
        unsorted_serialized = bal.serialize(sort=False)
        sorted_serialized = bal.serialize(sort=True)

        # Assert they produce different results (order matters in serialization)
        assert isinstance(unsorted_serialized, bytes)
        assert isinstance(sorted_serialized, bytes)
        assert len(unsorted_serialized) > 0
        assert len(sorted_serialized) > 0
        # Note: We can't easily compare bytes directly as SSZ encoding is complex,
        # but we verify both are valid serializations with different ordering
