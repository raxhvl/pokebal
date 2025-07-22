"""Types for Block Level Access Lists (EIP-7928)."""

from typing import List
from pydantic import BaseModel, Field
from .basic import (
    MAX_ACCOUNTS,
    AccountChanges,
    Address,
    StorageChange,
    TxIndex,
    SlotChanges,
    StorageKey,
    BalanceChange,
    NonceChange,
    CodeChange,
    StorageValue,
    Balance,
    Nonce,
    Bytecode,
)

from .serialization import to_ssz


class BlockAccessList(BaseModel):
    """Complete block access list as per EIP-7928."""

    account_changes: List[AccountChanges] = Field(default=[], max_length=MAX_ACCOUNTS)

    def _get_account(self, address: Address) -> AccountChanges:
        """Find existing account or create new one."""
        for account in self.account_changes:
            if account.address == address:
                return account

        new_account = AccountChanges(address=address)
        self.account_changes.append(new_account)
        return new_account

    def _get_slot_change_for_tx(
        self, account: AccountChanges, slot: StorageKey, tx_index: TxIndex
    ) -> StorageChange:
        """Find existing storage change for specific transaction or create new one."""
        # First find or create the SlotChanges for this slot
        slot_changes = None
        for sc in account.storage_changes:
            if sc.slot == slot:
                slot_changes = sc
                break

        if slot_changes is None:
            slot_changes = SlotChanges(slot=slot)
            account.storage_changes.append(slot_changes)

        # Then find or create the StorageChange for this transaction
        for change in slot_changes.changes:
            if change.tx_index == tx_index:
                return change

        # No existing change for this tx, create and add new one
        new_change = StorageChange(tx_index=tx_index)
        slot_changes.changes.append(new_change)
        return new_change

    def _get_balance_change_for_tx(
        self, account: AccountChanges, tx_index: TxIndex
    ) -> BalanceChange:
        """Find existing balance change for specific transaction or create new one."""
        # Find existing balance change for this transaction
        for balance_change in account.balance_changes:
            if balance_change.tx_index == tx_index:
                return balance_change

        # No existing change for this tx, create and add new one
        new_balance_change = BalanceChange(tx_index=tx_index)
        account.balance_changes.append(new_balance_change)
        return new_balance_change

    def _get_nonce_change_for_tx(
        self, account: AccountChanges, tx_index: TxIndex
    ) -> NonceChange:
        """Find existing nonce change for specific transaction or create new one."""
        # Find existing nonce change for this transaction
        for nonce_change in account.nonce_changes:
            if nonce_change.tx_index == tx_index:
                return nonce_change

        # No existing change for this tx, create and add new one
        new_nonce_change = NonceChange(tx_index=tx_index)
        account.nonce_changes.append(new_nonce_change)
        return new_nonce_change

    def _get_code_change_for_tx(
        self, account: AccountChanges, tx_index: TxIndex
    ) -> CodeChange:
        """Find existing code change for specific transaction or create new one."""
        # Find existing code change for this transaction
        for code_change in account.code_changes:
            if code_change.tx_index == tx_index:
                return code_change

        # No existing change for this tx, create and add new one
        new_code_change = CodeChange(tx_index=tx_index, new_code=b"")
        account.code_changes.append(new_code_change)
        return new_code_change

    def add_storage_write(
        self,
        address: Address,
        slot: StorageKey,
        tx_index: TxIndex,
        new_value: StorageValue,
    ):
        """Add a storage changed by specific transaction."""
        account = self._get_account(address)

        # Get or create storage change for this transaction (last write wins)
        storage_change = self._get_slot_change_for_tx(account, slot, tx_index)
        storage_change.new_value = new_value

    def add_storage_read(
        self,
        address: Address,
        slot: StorageKey,
    ):
        """Add a storage read by a block."""
        account = self._get_account(address)
        if slot not in account.storage_reads:
            account.storage_reads.append(slot)

    def add_balance_change(
        self,
        address: Address,
        tx_index: TxIndex,
        post_balance: Balance,
    ):
        """Add a balance changed by a specific transaction."""
        account = self._get_account(address)

        # Get or create balance change for this transaction (last write wins)
        balance_change = self._get_balance_change_for_tx(account, tx_index)
        balance_change.post_balance = post_balance

    def add_nonce_change(
        self,
        address: Address,
        tx_index: TxIndex,
        new_nonce: Nonce,
    ):
        """Add a nonce changed by a specific transaction."""
        account = self._get_account(address)

        # Get or create nonce change for this transaction (last write wins)
        nonce_change = self._get_nonce_change_for_tx(account, tx_index)
        nonce_change.new_nonce = new_nonce

    def add_code_change(
        self,
        address: Address,
        tx_index: TxIndex,
        new_code: Bytecode,
    ):
        """Add a code changed by a specific transaction."""
        account = self._get_account(address)

        # Get or create code change for this transaction (last write wins)
        code_change = self._get_code_change_for_tx(account, tx_index)
        code_change.new_code = new_code

    def sort(self) -> "BlockAccessList":
        """Return a new sorted BlockAccessList according to EIP-7928 ordering requirements.

        Ordering rules:
        1. Addresses: lexicographic (bytewise)
        2. Storage keys: lexicographic within each account
        3. Transaction indices: ascending within each change list
        """
        # Sort account changes by address (lexicographic)
        sorted_accounts = sorted(self.account_changes, key=lambda acc: acc.address)

        # Create new sorted account changes
        new_accounts = []
        for account in sorted_accounts:
            # Sort storage changes by slot key (lexicographic)
            sorted_storage_changes = sorted(
                account.storage_changes, key=lambda slot_change: slot_change.slot
            )

            # Within each slot change, sort changes by tx_index (ascending)
            new_storage_changes = []
            for slot_change in sorted_storage_changes:
                sorted_changes = sorted(
                    slot_change.changes, key=lambda change: change.tx_index
                )
                new_slot_change = SlotChanges(
                    slot=slot_change.slot, changes=sorted_changes
                )
                new_storage_changes.append(new_slot_change)

            # Sort storage reads lexicographically
            sorted_storage_reads = sorted(account.storage_reads)

            # Sort balance changes by tx_index (ascending)
            sorted_balance_changes = sorted(
                account.balance_changes, key=lambda change: change.tx_index
            )

            # Sort nonce changes by tx_index (ascending)
            sorted_nonce_changes = sorted(
                account.nonce_changes, key=lambda change: change.tx_index
            )

            # Sort code changes by tx_index (ascending)
            sorted_code_changes = sorted(
                account.code_changes, key=lambda change: change.tx_index
            )

            # Create new sorted account
            new_account = AccountChanges(
                address=account.address,
                storage_changes=new_storage_changes,
                storage_reads=sorted_storage_reads,
                balance_changes=sorted_balance_changes,
                nonce_changes=sorted_nonce_changes,
                code_changes=sorted_code_changes,
            )
            new_accounts.append(new_account)

        # Return new sorted instance
        return BlockAccessList(account_changes=new_accounts)

    def serialize(self, sort: bool = True) -> bytes:
        """Serialize the BlockAccessList to SSZ bytes.

        Args:
            sort: Whether to sort the data according to EIP-7928 requirements before serialization.
                 Defaults to True.
        """
        bal_to_serialize = self.sort() if sort else self
        return to_ssz(bal_to_serialize)
