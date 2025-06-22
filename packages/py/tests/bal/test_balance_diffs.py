"""Comprehensive tests for balance_diffs functionality using from_execution_trace."""

import pytest
from bal.builder import from_execution_trace
from bal.types import BlockAccessList
from tests.utils import TestAddresses
from bal.utils import int_to_hex
from rpc.types import (
    TransactionTrace,
    PrePostStates,
    AccountState,
)


class TestBalanceDiffs:
    """Test the balance_diffs property of BlockAccessList."""

    def test_empty_trace_produces_no_balance_diffs(self):
        """Test that empty trace produces no balance diffs."""
        trace_data = []
        bal = from_execution_trace(trace_data)

        assert len(bal.balance_diffs) == 0

    def test_transaction_with_no_balance_changes_ignored(self):
        """Test that transactions with no balance changes are ignored."""
        trace_data = [
            TransactionTrace(
                result=PrePostStates(
                    pre={
                        TestAddresses.ALICE: AccountState(
                            balance=int_to_hex(100),  # 100 wei
                            nonce=1,
                        )
                    },
                    post={
                        TestAddresses.ALICE: AccountState(
                            balance=int_to_hex(100),  # Same balance, only nonce changed
                            nonce=2,
                        )
                    },
                ),
                txHash="0x1111111111111111111111111111111111111111111111111111111111111111",
            )
        ]
        bal = from_execution_trace(trace_data)

        assert len(bal.balance_diffs) == 0

    def test_alice_gains_100_wei_single_transaction(self):
        """Test Alice gaining 100 wei in a single transaction."""
        trace_data = [
            TransactionTrace(
                result=PrePostStates(
                    pre={
                        TestAddresses.ALICE: AccountState(
                            balance=int_to_hex(100)  # 100 wei
                        )
                    },
                    post={
                        TestAddresses.ALICE: AccountState(
                            balance=int_to_hex(200)  # 200 wei
                        )
                    },
                ),
                txHash="0x1111111111111111111111111111111111111111111111111111111111111111",
            )
        ]
        bal = from_execution_trace(trace_data)

        assert len(bal.balance_diffs) == 1
        assert bal.balance_diffs[0].address == TestAddresses.ALICE
        assert len(bal.balance_diffs[0].changes) == 1
        assert bal.balance_diffs[0].changes[0].tx_index == 0
        assert (
            bal.balance_diffs[0].changes[0].delta == "0x000000000000000000000064"
        )  # +100

        self._validate_balance_diff_encoding(bal)

    def test_alice_loses_100_wei_single_transaction(self):
        """Test Alice losing 100 wei in a single transaction."""
        trace_data = [
            TransactionTrace(
                result=PrePostStates(
                    pre={
                        TestAddresses.ALICE: AccountState(
                            balance=int_to_hex(200)  # 200 wei
                        )
                    },
                    post={
                        TestAddresses.ALICE: AccountState(
                            balance=int_to_hex(100)  # 100 wei
                        )
                    },
                ),
                txHash="0x1111111111111111111111111111111111111111111111111111111111111111",
            )
        ]
        bal = from_execution_trace(trace_data)

        assert len(bal.balance_diffs) == 1
        assert bal.balance_diffs[0].address == TestAddresses.ALICE
        assert len(bal.balance_diffs[0].changes) == 1
        assert bal.balance_diffs[0].changes[0].tx_index == 0
        assert (
            bal.balance_diffs[0].changes[0].delta == "0xffffffffffffffffffffff9c"
        )  # -100

        self._validate_balance_diff_encoding(bal)

    def test_missing_balance_field_defaults_to_zero(self):
        """Test that missing balance field defaults to 0, Alice gains 500 wei."""
        trace_data = [
            TransactionTrace(
                result=PrePostStates(
                    pre={
                        TestAddresses.ALICE: AccountState(
                            nonce=1  # No balance field - defaults to 0
                        )
                    },
                    post={
                        TestAddresses.ALICE: AccountState(
                            balance=int_to_hex(500),  # 500 wei
                            nonce=2,
                        )
                    },
                ),
                txHash="0x1111111111111111111111111111111111111111111111111111111111111111",
            )
        ]
        bal = from_execution_trace(trace_data)

        assert len(bal.balance_diffs) == 1
        assert bal.balance_diffs[0].address == TestAddresses.ALICE
        assert len(bal.balance_diffs[0].changes) == 1
        assert bal.balance_diffs[0].changes[0].tx_index == 0
        assert (
            bal.balance_diffs[0].changes[0].delta == "0x0000000000000000000001f4"
        )  # +500

        self._validate_balance_diff_encoding(bal)

    def test_balance_goes_to_zero_when_missing_from_post(self):
        """Test Alice's balance goes to 0 when missing from post state (-1000 wei)."""
        trace_data = [
            TransactionTrace(
                result=PrePostStates(
                    pre={
                        TestAddresses.ALICE: AccountState(
                            balance=int_to_hex(1000)  # 1000 wei
                        )
                    },
                    post={
                        # Alice not present in post = balance goes to 0
                    },
                ),
                txHash="0x1111111111111111111111111111111111111111111111111111111111111111",
            )
        ]
        bal = from_execution_trace(trace_data)

        assert len(bal.balance_diffs) == 1
        assert bal.balance_diffs[0].address == TestAddresses.ALICE
        assert len(bal.balance_diffs[0].changes) == 1
        assert bal.balance_diffs[0].changes[0].tx_index == 0
        assert (
            bal.balance_diffs[0].changes[0].delta == "0xfffffffffffffffffffffc18"
        )  # -1000

        self._validate_balance_diff_encoding(bal)

    def test_alice_receives_large_eth_amount(self):
        """Test Alice receiving a large amount: gains 1 ETH."""
        trace_data = [
            TransactionTrace(
                result=PrePostStates(
                    pre={
                        TestAddresses.ALICE: AccountState(
                            balance=int_to_hex(10**18)  # 1 ETH in wei
                        )
                    },
                    post={
                        TestAddresses.ALICE: AccountState(
                            balance=int_to_hex(2 * 10**18)  # 2 ETH in wei
                        )
                    },
                ),
                txHash="0x1111111111111111111111111111111111111111111111111111111111111111",
            )
        ]
        bal = from_execution_trace(trace_data)

        assert len(bal.balance_diffs) == 1
        assert bal.balance_diffs[0].address == TestAddresses.ALICE
        assert len(bal.balance_diffs[0].changes) == 1
        assert bal.balance_diffs[0].changes[0].tx_index == 0
        assert (
            bal.balance_diffs[0].changes[0].delta == "0x000000000de0b6b3a7640000"
        )  # +1 ETH

        self._validate_balance_diff_encoding(bal)

    def test_multiple_people_single_transaction_excludes_unchanged(self):
        """Test Alice gains 100 wei, Bob loses 50 wei, Charlie unchanged (ignored)."""
        trace_data = [
            TransactionTrace(
                result=PrePostStates(
                    pre={
                        TestAddresses.ALICE: AccountState(
                            balance=int_to_hex(100)  # 100 wei
                        ),
                        TestAddresses.BOB: AccountState(
                            balance=int_to_hex(300)  # 300 wei
                        ),
                        TestAddresses.CHARLIE: AccountState(
                            balance=int_to_hex(100)  # 100 wei - no change
                        ),
                    },
                    post={
                        TestAddresses.ALICE: AccountState(
                            balance=int_to_hex(200)  # 200 wei
                        ),
                        TestAddresses.BOB: AccountState(
                            balance=int_to_hex(250)  # 250 wei
                        ),
                        TestAddresses.CHARLIE: AccountState(
                            balance=int_to_hex(
                                100
                            )  # 100 wei - no change, should be ignored
                        ),
                    },
                ),
                txHash="0x1111111111111111111111111111111111111111111111111111111111111111",
            )
        ]
        bal = from_execution_trace(trace_data)

        assert len(bal.balance_diffs) == 2  # Should exclude Charlie (no change)
        addresses = {diff.address for diff in bal.balance_diffs}
        assert TestAddresses.ALICE in addresses
        assert TestAddresses.BOB in addresses
        assert TestAddresses.CHARLIE not in addresses  # No change

        # Verify changes
        diffs_by_address = {diff.address: diff for diff in bal.balance_diffs}

        # Alice: +100 wei
        alice_diff = diffs_by_address[TestAddresses.ALICE]
        assert len(alice_diff.changes) == 1
        assert alice_diff.changes[0].delta == "0x000000000000000000000064"  # +100

        # Bob: -50 wei
        bob_diff = diffs_by_address[TestAddresses.BOB]
        assert len(bob_diff.changes) == 1
        assert bob_diff.changes[0].delta == "0xffffffffffffffffffffffce"  # -50

        self._validate_balance_diff_encoding(bal)

    def test_alice_multiple_transactions_accumulates_changes(self):
        """Test Alice across multiple transactions: gains 100 wei in tx0, loses 25 wei in tx1."""
        trace_data = [
            # Transaction 0: Alice gains 100 wei
            TransactionTrace(
                result=PrePostStates(
                    pre={
                        TestAddresses.ALICE: AccountState(
                            balance=int_to_hex(100)  # 100 wei
                        )
                    },
                    post={
                        TestAddresses.ALICE: AccountState(
                            balance=int_to_hex(200)  # 200 wei
                        )
                    },
                ),
                txHash="0x1111111111111111111111111111111111111111111111111111111111111111",
            ),
            # Transaction 1: Alice loses 25 wei
            TransactionTrace(
                result=PrePostStates(
                    pre={
                        TestAddresses.ALICE: AccountState(
                            balance=int_to_hex(200)  # 200 wei
                        )
                    },
                    post={
                        TestAddresses.ALICE: AccountState(
                            balance=int_to_hex(175)  # 175 wei
                        )
                    },
                ),
                txHash="0x2222222222222222222222222222222222222222222222222222222222222222",
            ),
        ]
        bal = from_execution_trace(trace_data)

        assert len(bal.balance_diffs) == 1
        assert bal.balance_diffs[0].address == TestAddresses.ALICE
        assert len(bal.balance_diffs[0].changes) == 2

        changes_by_tx = {
            change.tx_index: change for change in bal.balance_diffs[0].changes
        }
        assert changes_by_tx[0].delta == "0x000000000000000000000064"  # +100
        assert changes_by_tx[1].delta == "0xffffffffffffffffffffffe7"  # -25

        self._validate_balance_diff_encoding(bal)

    def test_comprehensive_scenario_all_edge_cases(self):
        """Test comprehensive scenario with all edge cases across multiple transactions."""
        trace_data = [
            # Transaction 0: Multiple people with various scenarios
            TransactionTrace(
                result=PrePostStates(
                    pre={
                        # Alice: gains 100 wei (100 -> 200)
                        TestAddresses.ALICE: AccountState(
                            balance=int_to_hex(100)  # 100 wei
                        ),
                        # Bob: loses 50 wei (300 -> 250)
                        TestAddresses.BOB: AccountState(
                            balance=int_to_hex(300)  # 300 wei
                        ),
                        # Charlie: no change (100 -> 100) - should be ignored
                        TestAddresses.CHARLIE: AccountState(
                            balance=int_to_hex(100)  # 100 wei
                        ),
                        # Dave: missing balance field (defaults to 0) -> gains 500 wei
                        TestAddresses.DAVE: AccountState(
                            nonce=1  # No balance field
                        ),
                        # Eve: balance goes to 0 (1000 -> 0)
                        TestAddresses.EVE: AccountState(
                            balance=int_to_hex(1000)  # 1000 wei
                        ),
                    },
                    post={
                        TestAddresses.ALICE: AccountState(
                            balance=int_to_hex(200)  # 200 wei
                        ),
                        TestAddresses.BOB: AccountState(
                            balance=int_to_hex(250)  # 250 wei
                        ),
                        TestAddresses.CHARLIE: AccountState(
                            balance=int_to_hex(100)  # 100 wei (no change)
                        ),
                        TestAddresses.DAVE: AccountState(
                            balance=int_to_hex(500),  # 500 wei
                            nonce=2,
                        ),
                        # Eve: not present in post (balance -> 0)
                    },
                ),
                txHash="0x1111111111111111111111111111111111111111111111111111111111111111",
            ),
            # Transaction 1: More people and edge cases
            TransactionTrace(
                result=PrePostStates(
                    pre={
                        # Alice: loses 25 wei (200 -> 175)
                        TestAddresses.ALICE: AccountState(
                            balance=int_to_hex(200)  # 200 wei
                        ),
                        # Frank: large ETH amount (1 ETH -> 2 ETH)
                        TestAddresses.FRANK: AccountState(
                            balance=int_to_hex(10**18)  # 1 ETH in wei
                        ),
                    },
                    post={
                        TestAddresses.ALICE: AccountState(
                            balance=int_to_hex(175)  # 175 wei
                        ),
                        TestAddresses.FRANK: AccountState(
                            balance=int_to_hex(2 * 10**18)  # 2 ETH in wei
                        ),
                        # Grace: only appears in post (0 -> 1000 wei)
                        TestAddresses.GRACE: AccountState(
                            balance=int_to_hex(1000)  # 1000 wei
                        ),
                    },
                ),
                txHash="0x2222222222222222222222222222222222222222222222222222222222222222",
            ),
        ]
        bal = from_execution_trace(trace_data)

        # Should have 6 people with changes (excluding Charlie who has no change)
        expected_addresses = {
            TestAddresses.ALICE,  # Alice: 2 changes
            TestAddresses.BOB,  # Bob: 1 change
            TestAddresses.DAVE,  # Dave: 1 change
            TestAddresses.EVE,  # Eve: 1 change
            TestAddresses.FRANK,  # Frank: 1 change
            TestAddresses.GRACE,  # Grace: 1 change
        }

        assert len(bal.balance_diffs) == len(expected_addresses)
        actual_addresses = {diff.address for diff in bal.balance_diffs}
        assert actual_addresses == expected_addresses

        # Verify Alice has 2 changes
        diffs_by_address = {diff.address: diff for diff in bal.balance_diffs}
        alice_diff = diffs_by_address[TestAddresses.ALICE]
        assert len(alice_diff.changes) == 2

        # Verify specific changes for key people
        bob_diff = diffs_by_address[TestAddresses.BOB]
        assert len(bob_diff.changes) == 1
        assert (
            bob_diff.changes[0].delta == "0xffffffffffffffffffffffce"
        )  # Bob loses 50 wei

        dave_diff = diffs_by_address[TestAddresses.DAVE]
        assert len(dave_diff.changes) == 1
        assert (
            dave_diff.changes[0].delta == "0x0000000000000000000001f4"
        )  # Dave gains 500 wei from 0

        eve_diff = diffs_by_address[TestAddresses.EVE]
        assert len(eve_diff.changes) == 1
        assert (
            eve_diff.changes[0].delta == "0xfffffffffffffffffffffc18"
        )  # Eve loses 1000 wei (goes to 0)

        frank_diff = diffs_by_address[TestAddresses.FRANK]
        assert len(frank_diff.changes) == 1
        assert (
            frank_diff.changes[0].delta == "0x000000000de0b6b3a7640000"
        )  # Frank gains 1 ETH

        grace_diff = diffs_by_address[TestAddresses.GRACE]
        assert len(grace_diff.changes) == 1
        assert (
            grace_diff.changes[0].delta == "0x0000000000000000000003e8"
        )  # Grace gains 1000 wei from 0

        self._validate_balance_diff_encoding(bal)

    def _validate_balance_diff_encoding(self, bal: "BlockAccessList") -> None:
        """Helper method to validate balance diff encoding for all test cases."""
        if len(bal.balance_diffs) > 0:
            # Verify all deltas are properly encoded as 12-byte hex strings
            for diff in bal.balance_diffs:
                for change in diff.changes:
                    assert change.delta.startswith("0x"), (
                        f"Delta {change.delta} should start with 0x"
                    )
                    assert len(change.delta) == 26, (
                        f"Delta {change.delta} should be 26 chars (0x + 24 hex)"
                    )

                    # Verify it's valid hex
                    try:
                        delta_int = int(change.delta, 16)
                    except ValueError:
                        pytest.fail(f"Delta {change.delta} is not valid hex")

                    # Verify within 12-byte two's complement range
                    max_valid_delta = 2**95 - 1
                    min_valid_delta = -(2**95)

                    # Handle two's complement conversion for negative values
                    if delta_int >= 2**95:  # If high bit is set, it's negative
                        delta_int = delta_int - 2**96

                    assert min_valid_delta <= delta_int <= max_valid_delta, (
                        f"Delta {delta_int} is outside valid 12-byte range"
                    )

    def test_functional_programming_determinism(self):
        """Test that from_execution_trace is deterministic (functional programming principle)."""
        # Test with Alice gaining 100 wei
        trace_data = [
            TransactionTrace(
                result=PrePostStates(
                    pre={
                        TestAddresses.ALICE: AccountState(
                            balance=int_to_hex(100)
                        )  # 100 wei
                    },
                    post={
                        TestAddresses.ALICE: AccountState(
                            balance=int_to_hex(200)
                        )  # 200 wei
                    },
                ),
                txHash="0x1111111111111111111111111111111111111111111111111111111111111111",
            )
        ]

        # Same input should always produce same output
        bal1 = from_execution_trace(trace_data)
        bal2 = from_execution_trace(trace_data)

        assert len(bal1.balance_diffs) == len(bal2.balance_diffs)

        # Convert to sets for comparison
        def balance_diff_to_tuple(diff):
            changes = tuple(sorted([(c.tx_index, c.delta) for c in diff.changes]))
            return (diff.address, changes)

        bal1_set = {balance_diff_to_tuple(diff) for diff in bal1.balance_diffs}
        bal2_set = {balance_diff_to_tuple(diff) for diff in bal2.balance_diffs}

        assert bal1_set == bal2_set, "Function should be deterministic"
