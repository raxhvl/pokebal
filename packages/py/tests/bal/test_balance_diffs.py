"""Tests if `balance_diffs` is computed correctly."""

import pytest
from typing import List
from bal.builder import from_execution_trace
from bal.types import BlockAccessList, AccountBalanceDiff, BalanceChange, AccountNonce
from tests.utils import TestAddresses, TestTxHashes, BALTestCase
from bal.utils import int_to_hex, encode_balance_delta
from rpc.types import (
    TransactionTrace,
    PrePostStates,
    AccountState,
)


def create_test_cases() -> List[BALTestCase]:
    """Create test case data following functional programming principles."""

    return [
        BALTestCase(
            description="Empty trace produces no balance diffs",
            trace_input=[],
            expected_result=BlockAccessList(),
        ),
        BALTestCase(
            description="Transaction with no balance changes ignored",
            trace_input=[
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(
                                balance=int_to_hex(100),
                                nonce=1,
                            )
                        },
                        post={
                            TestAddresses.ALICE: AccountState(
                                balance=int_to_hex(100),  # Same balance
                                nonce=2,
                            )
                        },
                    ),
                    txHash=TestTxHashes.TX1,
                )
            ],
            expected_result=BlockAccessList(
                nonce_diffs=[
                    AccountNonce(
                        address=TestAddresses.ALICE,
                        nonce=2,
                    )
                ]
            ),
        ),
        BALTestCase(
            description="Alice gains 100 wei in single transaction",
            trace_input=[
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(balance=int_to_hex(100))
                        },
                        post={
                            TestAddresses.ALICE: AccountState(balance=int_to_hex(200))
                        },
                    ),
                    txHash=TestTxHashes.TX1,
                )
            ],
            expected_result=BlockAccessList(
                balance_diffs=[
                    AccountBalanceDiff(
                        address=TestAddresses.ALICE,
                        changes=[
                            BalanceChange(
                                tx_index=0,
                                delta=encode_balance_delta(100),  # +100
                            )
                        ],
                    )
                ]
            ),
        ),
        BALTestCase(
            description="Alice loses 100 wei in single transaction",
            trace_input=[
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(balance=int_to_hex(200))
                        },
                        post={
                            TestAddresses.ALICE: AccountState(balance=int_to_hex(100))
                        },
                    ),
                    txHash=TestTxHashes.TX1,
                )
            ],
            expected_result=BlockAccessList(
                balance_diffs=[
                    AccountBalanceDiff(
                        address=TestAddresses.ALICE,
                        changes=[
                            BalanceChange(
                                tx_index=0,
                                delta=encode_balance_delta(-100),  # -100
                            )
                        ],
                    )
                ]
            ),
        ),
        BALTestCase(
            description="Missing balance field defaults to zero, Alice gains 500 wei",
            trace_input=[
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(
                                nonce=1  # No balance field
                            )
                        },
                        post={
                            TestAddresses.ALICE: AccountState(
                                balance=int_to_hex(500),
                                nonce=2,
                            )
                        },
                    ),
                    txHash=TestTxHashes.TX1,
                )
            ],
            expected_result=BlockAccessList(
                balance_diffs=[
                    AccountBalanceDiff(
                        address=TestAddresses.ALICE,
                        changes=[
                            BalanceChange(
                                tx_index=0,
                                delta=encode_balance_delta(500),  # +500
                            )
                        ],
                    )
                ],
                nonce_diffs=[
                    AccountNonce(
                        address=TestAddresses.ALICE,
                        nonce=2,
                    )
                ]
            ),
        ),
        BALTestCase(
            description="Balance goes to zero when missing from post state",
            trace_input=[
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(balance=int_to_hex(1000))
                        },
                        post={
                            # Alice not present in post = balance goes to 0
                        },
                    ),
                    txHash=TestTxHashes.TX1,
                )
            ],
            expected_result=BlockAccessList(
                balance_diffs=[
                    AccountBalanceDiff(
                        address=TestAddresses.ALICE,
                        changes=[
                            BalanceChange(
                                tx_index=0,
                                delta=encode_balance_delta(-1000),  # -1000
                            )
                        ],
                    )
                ]
            ),
        ),
        BALTestCase(
            description="Alice receives large ETH amount (1 ETH gain)",
            trace_input=[
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(
                                balance=int_to_hex(10**18)  # 1 ETH
                            )
                        },
                        post={
                            TestAddresses.ALICE: AccountState(
                                balance=int_to_hex(2 * 10**18)  # 2 ETH
                            )
                        },
                    ),
                    txHash=TestTxHashes.TX1,
                )
            ],
            expected_result=BlockAccessList(
                balance_diffs=[
                    AccountBalanceDiff(
                        address=TestAddresses.ALICE,
                        changes=[
                            BalanceChange(
                                tx_index=0,
                                delta=encode_balance_delta(10**18),  # +1 ETH
                            )
                        ],
                    )
                ]
            ),
        ),
        BALTestCase(
            description="Multiple people single transaction, excludes unchanged",
            trace_input=[
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(balance=int_to_hex(100)),
                            TestAddresses.BOB: AccountState(balance=int_to_hex(300)),
                            TestAddresses.CHARLIE: AccountState(
                                balance=int_to_hex(100)
                            ),  # No change
                        },
                        post={
                            TestAddresses.ALICE: AccountState(balance=int_to_hex(200)),
                            TestAddresses.BOB: AccountState(balance=int_to_hex(250)),
                            TestAddresses.CHARLIE: AccountState(
                                balance=int_to_hex(100)
                            ),  # No change
                        },
                    ),
                    txHash=TestTxHashes.TX1,
                )
            ],
            expected_result=BlockAccessList(
                balance_diffs=[
                    AccountBalanceDiff(
                        address=TestAddresses.ALICE,
                        changes=[
                            BalanceChange(tx_index=0, delta=encode_balance_delta(100))
                        ],  # +100
                    ),
                    AccountBalanceDiff(
                        address=TestAddresses.BOB,
                        changes=[
                            BalanceChange(tx_index=0, delta=encode_balance_delta(-50))
                        ],  # -50
                    ),
                    # Charlie excluded (no change)
                ]
            ),
        ),
        BALTestCase(
            description="Alice multiple transactions accumulates changes",
            trace_input=[
                # Transaction 0: Alice gains 100 wei
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(balance=int_to_hex(100))
                        },
                        post={
                            TestAddresses.ALICE: AccountState(balance=int_to_hex(200))
                        },
                    ),
                    txHash=TestTxHashes.TX1,
                ),
                # Transaction 1: Alice loses 25 wei
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(balance=int_to_hex(200))
                        },
                        post={
                            TestAddresses.ALICE: AccountState(balance=int_to_hex(175))
                        },
                    ),
                    txHash=TestTxHashes.TX2,
                ),
            ],
            expected_result=BlockAccessList(
                balance_diffs=[
                    AccountBalanceDiff(
                        address=TestAddresses.ALICE,
                        changes=[
                            BalanceChange(
                                tx_index=0, delta=encode_balance_delta(100)
                            ),  # +100
                            BalanceChange(
                                tx_index=1, delta=encode_balance_delta(-25)
                            ),  # -25
                        ],
                    )
                ]
            ),
        ),
    ]


class TestBalanceDiffs:
    """Tests for balance diffs functionality."""

    @pytest.mark.parametrize(
        "test_case", create_test_cases(), ids=lambda tc: tc.description
    )
    def test_balance_diffs_from_execution_trace(self, test_case: BALTestCase):
        """Test balance diffs with expected output."""
        # Execute the function under test
        result = from_execution_trace(test_case.trace_input)

        # Validate the result matches the expected BlockAccessList structure
        assert len(result.account_accesses) == len(
            test_case.expected_result.account_accesses
        )
        assert len(result.code_diffs) == len(test_case.expected_result.code_diffs)
        assert len(result.nonce_diffs) == len(test_case.expected_result.nonce_diffs)

        # Validate specific balance_diffs (order-independent)
        assert len(result.balance_diffs) == len(test_case.expected_result.balance_diffs)

        # Convert to dictionaries for easier comparison
        result_by_address = {diff.address: diff for diff in result.balance_diffs}
        expected_by_address = {
            diff.address: diff for diff in test_case.expected_result.balance_diffs
        }

        assert set(result_by_address.keys()) == set(expected_by_address.keys())

        # Compare each address's changes
        for address in expected_by_address:
            result_diff = result_by_address[address]
            expected_diff = expected_by_address[address]

            assert len(result_diff.changes) == len(expected_diff.changes)

            for result_change, expected_change in zip(
                result_diff.changes, expected_diff.changes
            ):
                assert result_change.tx_index == expected_change.tx_index
                assert result_change.delta == expected_change.delta
