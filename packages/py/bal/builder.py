"""Builder for constructing Block Access Lists from execution traces."""

from .types import (
    BlockAccessList,
    AccountBalanceDiff,
    BalanceChange,
    AccountAccess,
    SlotAccess,
    PerTxAccess,
)
from .utils import encode_balance_delta
from rpc.types import TransactionTrace, BlockDebugTraceResult


class BlockAccessListBuilder:
    """Builds block access lists from transaction execution data."""

    def __init__(self):
        """Initialize the builder."""
        self.bal = BlockAccessList()

    def _create_or_get(self, collection: list, key: str, factory_func, key_attr: str):
        """Generic function to find existing item by key or create new one.

        Pure functional approach - searches collection for item with matching key.
        If found, returns existing item. If not found, creates new item using factory_func
        and appends to collection.

        Args:
            collection: List to search in (e.g., self.bal.balance_diffs)
            key: Key to match against item's key attribute
            factory_func: Function that creates new item when called with key
            key_attr: Attribute name to match against (e.g., "address", "slot")

        Returns:
            Existing or newly created item from collection
        """
        # Search for existing item with matching key
        for item in collection:
            if getattr(item, key_attr) == key:
                return item

        # Create new item if none found
        new_item = factory_func(key)
        collection.append(new_item)
        return new_item

    def add_balance_change(
        self, tx_index: int, transaction_trace: TransactionTrace
    ) -> None:
        """Add balance changes from a transaction trace.

        Extracts balance changes from pre/post states and processes each one.
        Composes pure functions to calculate, validate, and encode balance changes.
        Only mutates state when valid, non-zero changes are detected.

        Args:
            tx_index: Transaction index in block
            transaction_trace: TransactionTrace containing pre/post states

        Raises:
            ValueError: If balance delta exceeds 12-byte two's complement range
        """
        # Extract balance changes from transaction trace
        all_addresses = set(transaction_trace.result.pre.keys()) | set(
            transaction_trace.result.post.keys()
        )

        for address in all_addresses:
            pre_state = transaction_trace.result.pre.get(address)
            post_state = transaction_trace.result.post.get(address)

            # Extract balances, defaulting to 0 if not present
            pre_balance = 0
            if pre_state and pre_state.balance:
                pre_balance = int(pre_state.balance, 16)

            post_balance = 0
            if post_state and post_state.balance:
                post_balance = int(post_state.balance, 16)

            # Only process if there's a balance change
            if pre_balance != post_balance:
                # Step 1: Calculate delta (pure function)
                delta = post_balance - pre_balance

                # Step 2: Encode delta as two's complement hex string
                encoded_delta = encode_balance_delta(delta)

                # Step 3: Create balance change entry (pure function, returns None if delta=0)
                balance_change = BalanceChange(tx_index=tx_index, delta=encoded_delta)

                # Step 4: Get or create AccountBalanceDiff and append balance change
                account_diff = self._create_or_get(
                    self.bal.balance_diffs,
                    address,
                    lambda addr: AccountBalanceDiff(address=addr),
                    key_attr="address",
                )
                account_diff.changes.append(balance_change)

    def add_account_access(
        self, tx_index: int, transaction_trace: TransactionTrace
    ) -> None:
        """Add storage access information from a transaction trace.

        Extracts storage accesses from pre/post states and processes each one.
        Composes pure functions to identify, compare, and track storage changes.
        Only mutates state when actual storage changes are detected.

        Args:
            tx_index: Transaction index in block
            transaction_trace: TransactionTrace containing pre/post states

        Note:
            This tracks storage slot accesses by comparing pre/post storage states.
            Each modified storage slot is recorded with its post-transaction value.
        """
        # Extract all addresses that have storage changes
        all_addresses = set(transaction_trace.result.pre.keys()) | set(
            transaction_trace.result.post.keys()
        )

        # Step 1: Iterate over all addresses in pre/post states
        for address in all_addresses:
            pre_state = transaction_trace.result.pre.get(address)
            post_state = transaction_trace.result.post.get(address)

            # Extract storage states, defaulting to empty dict if not present
            pre_storage = {}
            if pre_state and pre_state.storage:
                pre_storage = pre_state.storage

            post_storage = {}
            if post_state and post_state.storage:
                post_storage = post_state.storage

            # Step 2: Loop through all storage slots
            all_slots = set(pre_storage.keys()) | set(post_storage.keys())
            for slot in all_slots:
                pre_value = pre_storage.get(
                    slot,
                    "0x0000000000000000000000000000000000000000000000000000000000000000",
                )
                post_value = post_storage.get(
                    slot,
                    "0x0000000000000000000000000000000000000000000000000000000000000000",
                )

                # Step 3: Check if value was changed
                if pre_value != post_value:
                    # Step 4: Add per-tx entry this slot.

                    # Step 4a: Create or get account access entry
                    account_access = self._create_or_get(
                        self.bal.account_accesses,
                        address,
                        lambda addr: AccountAccess(address=addr),
                        key_attr="address",
                    )

                    # Step 4b: Create or get slot access entry
                    slot_access = self._create_or_get(
                        account_access.accesses,
                        slot,
                        lambda slot_key: SlotAccess(slot=slot_key),
                        key_attr="slot",
                    )

                    # Step 4c: Add per-transaction access to slot
                    slot_access.accesses.append(
                        PerTxAccess(tx_index=tx_index, value_after=post_value)
                    )

    def build(self) -> BlockAccessList:
        """Build the final BlockAccessList."""
        return self.bal


def from_execution_trace(trace_data: BlockDebugTraceResult) -> BlockAccessList:
    """Build BlockAccessList from execution trace data.

    Processes each transaction trace to extract balance changes, storage accesses,
    code changes, and nonce changes using functional programming approach.

    Args:
        trace_data: BlockDebugTraceResult

    Returns:
        Complete BlockAccessList with all tracked changes
    """
    builder = BlockAccessListBuilder()

    for tx_index, transaction_trace in enumerate(trace_data):
        # Process balance changes from this transaction
        builder.add_balance_change(tx_index, transaction_trace)

        # Process storage access from this transaction
        builder.add_account_access(tx_index, transaction_trace)

        # TODO: Add code change processing
        # TODO: Add nonce change processing

    return builder.build()
