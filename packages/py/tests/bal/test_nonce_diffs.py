"""Tests if `nonce_diffs` is computed correctly."""

import pytest
from typing import List
from bal.builder import from_execution_trace
from bal.types import BlockAccessList, AccountNonce
from tests.utils import TestAddresses, TestTxHashes, BALTestCase
from bal.utils import int_to_hex
from rpc.types import (
    TransactionTrace,
    PrePostStates,
    AccountState,
)


def create_test_cases() -> List[BALTestCase]:
    """Create test case data following functional programming principles."""

    return [
        BALTestCase(
            description="Empty trace produces no nonce diffs",
            trace_input=[],
            expected_result=BlockAccessList(),
        ),
        BALTestCase(
            description="Transaction with no nonce changes ignored",
            trace_input=[
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(
                                balance=int_to_hex(100),
                                nonce=5,
                            )
                        },
                        post={
                            TestAddresses.ALICE: AccountState(
                                balance=int_to_hex(100),  # Same balance
                                nonce=5,  # Same nonce
                            )
                        },
                    ),
                    txHash=TestTxHashes.TX1,
                )
            ],
            expected_result=BlockAccessList(),
        ),
        BALTestCase(
            description="Alice nonce increments in single transaction",
            trace_input=[
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(nonce=1)
                        },
                        post={
                            TestAddresses.ALICE: AccountState(nonce=2)
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
            description="Missing nonce field defaults to zero, Alice nonce becomes 1",
            trace_input=[
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(
                                balance=int_to_hex(100)  # No nonce field
                            )
                        },
                        post={
                            TestAddresses.ALICE: AccountState(
                                balance=int_to_hex(100),
                                nonce=1,
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
                        nonce=1,
                    )
                ]
            ),
        ),
        BALTestCase(
            description="Multiple accounts nonce changes in single transaction",
            trace_input=[
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(nonce=1),
                            TestAddresses.BOB: AccountState(nonce=5),
                            TestAddresses.CHARLIE: AccountState(nonce=10),
                        },
                        post={
                            TestAddresses.ALICE: AccountState(nonce=2),
                            TestAddresses.BOB: AccountState(nonce=5),  # No change
                            TestAddresses.CHARLIE: AccountState(nonce=15),
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
                    ),
                    AccountNonce(
                        address=TestAddresses.CHARLIE,
                        nonce=15,
                    ),
                ]
            ),
        ),
        BALTestCase(
            description="Same account nonce changes across multiple transactions",
            trace_input=[
                TransactionTrace(
                    result=PrePostStates(
                        pre={TestAddresses.ALICE: AccountState(nonce=1)},
                        post={TestAddresses.ALICE: AccountState(nonce=2)},
                    ),
                    txHash=TestTxHashes.TX1,
                ),
                TransactionTrace(
                    result=PrePostStates(
                        pre={TestAddresses.ALICE: AccountState(nonce=2)},
                        post={TestAddresses.ALICE: AccountState(nonce=3)},
                    ),
                    txHash=TestTxHashes.TX2,
                ),
            ],
            expected_result=BlockAccessList(
                nonce_diffs=[
                    AccountNonce(
                        address=TestAddresses.ALICE,
                        nonce=3,  # Last nonce value wins
                    )
                ]
            ),
        ),
    ]


class TestNonceDiffs:
    """Test nonce diffs computation."""

    @pytest.mark.parametrize(
        "test_case", create_test_cases(), ids=lambda tc: tc.description
    )
    def test_nonce_diffs_from_execution_trace(self, test_case: BALTestCase):
        """Test nonce diffs with expected output."""
        # Execute the function under test
        result = from_execution_trace(test_case.trace_input)

        # Validate the result matches the expected BlockAccessList structure
        assert len(result.account_accesses) == len(
            test_case.expected_result.account_accesses
        )
        assert len(result.balance_diffs) == len(test_case.expected_result.balance_diffs)
        assert len(result.code_diffs) == len(test_case.expected_result.code_diffs)
        assert len(result.nonce_diffs) == len(test_case.expected_result.nonce_diffs)

        # Validate nonce diffs content
        for expected_nonce_diff in test_case.expected_result.nonce_diffs:
            matching_nonce_diff = next(
                (
                    nd
                    for nd in result.nonce_diffs
                    if nd.address == expected_nonce_diff.address
                ),
                None,
            )
            assert matching_nonce_diff is not None
            assert matching_nonce_diff.nonce == expected_nonce_diff.nonce