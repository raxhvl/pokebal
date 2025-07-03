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
    new_nonce: Nonce = Field(
        default=0,
    )


class CodeChange(BaseModel):
    """Code change for a specific transaction."""

    tx_index: TxIndex
    new_code: CodeData


class SlotChanges(BaseModel):
    """Storage slot changes information."""

    slot: StorageKey
    changes: List[StorageChange] = Field(default=[], max_length=MAX_TXS)


class SlotRead(BaseModel):
    """Storage slot read information."""

    slot: StorageKey


class AccountChanges(BaseModel):
    """Account changes information per EIP-7928."""

    address: Address
    storage_changes: List[SlotChanges] = Field(default=[], max_length=MAX_SLOTS)
    storage_reads: List[SlotRead] = Field(default=[], max_length=MAX_SLOTS)
    balance_changes: List[BalanceChange] = Field(default=[], max_length=MAX_TXS)
    nonce_changes: List[NonceChange] = Field(default=[], max_length=MAX_TXS)
    code_changes: List[CodeChange] = Field(default=[], max_length=MAX_TXS)


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

    def _slot_already_read(self, account: AccountChanges, slot: StorageKey) -> bool:
        """Ensure slot read entry exists for given slot."""
        for slot_read in account.storage_reads:
            if slot_read.slot == slot:
                return True
        return False

    def _get_balance_change_for_tx(
        self, account: AccountChanges, tx_index: TxIndex
    ) -> BalanceChange:
        """Find existing balance change for specific transaction or create new one."""
        # Find existing balance change for this transaction
        for balance_change in account.balance_changes:
            if balance_change.tx_index == tx_index:
                return balance_change

        # No existing change for this tx, create and add new one
        new_balance_change = BalanceChange(tx_index=tx_index, post_balance=0)
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
        new_code_change = CodeChange(tx_index=tx_index, new_code=CodeData("0x"))
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
        if not self._slot_already_read(account, slot):
            account.storage_reads.append(SlotRead(slot=slot))

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
        new_code: CodeData,
    ):
        """Add a code changed by a specific transaction."""
        account = self._get_account(address)

        # Get or create code change for this transaction (last write wins)
        code_change = self._get_code_change_for_tx(account, tx_index)
        code_change.new_code = new_code
