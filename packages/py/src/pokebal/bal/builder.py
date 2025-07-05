"""Builder for constructing Block Access Lists from execution traces."""

from .types import BlockAccessList
from pokebal.rpc.types import BlockDebugTraceResult
from pokebal.common.types import EVM_WORD_ZERO


def from_execution_trace(trace_data: BlockDebugTraceResult) -> BlockAccessList:
    """Build BlockAccessList from execution trace data.

    Processes each transaction trace to extract balance changes, storage accesses,
    code changes, and nonce changes using functional programming approach.

    Args:
        trace_data: BlockDebugTraceResult

    Returns:
        Complete BlockAccessList with all tracked changes
    """
    bal = BlockAccessList()

    for tx_index, transaction_trace in enumerate(trace_data):
        # All touched addresses in this transaction
        touched_addresses = set(transaction_trace.result.pre.keys()) | set(
            transaction_trace.result.post.keys()
        )

        for address in touched_addresses:
            pre_state = transaction_trace.result.pre.get(address)
            post_state = transaction_trace.result.post.get(address)

            # Process nonce changes
            pre_nonce = pre_state.nonce if pre_state and pre_state.nonce else None
            post_nonce = post_state.nonce if post_state and post_state.nonce else None

            if pre_nonce != post_nonce and post_nonce is not None:
                bal.add_nonce_change(address, tx_index, post_nonce)

            # Process balance changes
            pre_balance = (
                int(pre_state.balance, 16) if pre_state and pre_state.balance else 0
            )
            post_balance = (
                int(post_state.balance, 16) if post_state and post_state.balance else 0
            )

            if pre_balance != post_balance:
                bal.add_balance_change(address, tx_index, post_balance)

            # Process storage changes
            pre_storage = pre_state.storage if pre_state and pre_state.storage else {}
            post_storage = (
                post_state.storage if post_state and post_state.storage else {}
            )
            touched_slots = set(pre_storage.keys()) | set(post_storage.keys())

            for slot in touched_slots:
                pre_value = pre_storage.get(slot, None)
                post_value = post_storage.get(slot, None)

                # Check if storage was written (set, reset, or changed)
                is_set = pre_value is None and post_value is not None
                is_reset = pre_value is not None and post_value is None
                is_changed = pre_value != post_value and not (is_set or is_reset)

                is_write = is_set or is_reset or is_changed

                if is_write:
                    # Use zero word for reset operations
                    new_value = EVM_WORD_ZERO if is_reset else post_value
                    bal.add_storage_write(address, slot, tx_index, new_value)

            # Process code changes
            pre_code = pre_state.code if pre_state and pre_state.code else None
            post_code = post_state.code if post_state and post_state.code else None

            if pre_code != post_code and post_code is not None:
                bal.add_code_change(address, tx_index, post_code)

    return bal
