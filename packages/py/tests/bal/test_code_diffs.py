"""Tests if `code_diffs` is computed correctly."""

import pytest
from typing import List
from bal.builder import from_execution_trace
from bal.types import BlockAccessList, AccountCodeDiff, MAX_CODE_SIZE
from tests.utils import TestAddresses, TestTxHashes, BALTestCase
from rpc.types import (
    TransactionTrace,
    PrePostStates,
    AccountState,
)


def create_test_cases() -> List[BALTestCase]:
    """Create test case data following functional programming principles."""
    
    # Sample contract bytecode (small)
    SAMPLE_CODE = "0x608060405234801561001057600080fd5b50"
    SAMPLE_CODE_2 = "0x608060405234801561001057600080fd5b51"
    
    # Large code that exceeds MAX_CODE_SIZE
    OVERSIZED_CODE = "0x" + "60" * (MAX_CODE_SIZE + 1)

    return [
        BALTestCase(
            description="Empty trace produces no code diffs",
            trace_input=[],
            expected_result=BlockAccessList(),
        ),
        BALTestCase(
            description="Transaction with no code changes ignored",
            trace_input=[
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(
                                code=SAMPLE_CODE,
                            )
                        },
                        post={
                            TestAddresses.ALICE: AccountState(
                                code=SAMPLE_CODE,  # Same code
                            )
                        },
                    ),
                    txHash=TestTxHashes.TX1,
                )
            ],
            expected_result=BlockAccessList(),
        ),
        BALTestCase(
            description="Contract deployment - new code from empty",
            trace_input=[
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(
                                # No code field = empty code
                            )
                        },
                        post={
                            TestAddresses.ALICE: AccountState(
                                code=SAMPLE_CODE,
                            )
                        },
                    ),
                    txHash=TestTxHashes.TX1,
                )
            ],
            expected_result=BlockAccessList(
                code_diffs=[
                    AccountCodeDiff(
                        address=TestAddresses.ALICE,
                        new_code=SAMPLE_CODE,
                    )
                ]
            ),
        ),
        BALTestCase(
            description="Contract deployment - new code from empty string",
            trace_input=[
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(
                                # No code field = None/empty code
                            )
                        },
                        post={
                            TestAddresses.ALICE: AccountState(
                                code=SAMPLE_CODE,
                            )
                        },
                    ),
                    txHash=TestTxHashes.TX1,
                )
            ],
            expected_result=BlockAccessList(
                code_diffs=[
                    AccountCodeDiff(
                        address=TestAddresses.ALICE,
                        new_code=SAMPLE_CODE,
                    )
                ]
            ),
        ),
        BALTestCase(
            description="Contract upgrade - code changes between non-empty states",
            trace_input=[
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(
                                code=SAMPLE_CODE,
                            )
                        },
                        post={
                            TestAddresses.ALICE: AccountState(
                                code=SAMPLE_CODE_2,
                            )
                        },
                    ),
                    txHash=TestTxHashes.TX1,
                )
            ],
            expected_result=BlockAccessList(
                code_diffs=[
                    AccountCodeDiff(
                        address=TestAddresses.ALICE,
                        new_code=SAMPLE_CODE_2,
                    )
                ]
            ),
        ),
        BALTestCase(
            description="Multiple contracts deployed in single transaction",
            trace_input=[
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(),
                            TestAddresses.BOB: AccountState(),
                            TestAddresses.CHARLIE: AccountState(
                                code=SAMPLE_CODE,  # Already has code - no change
                            ),
                        },
                        post={
                            TestAddresses.ALICE: AccountState(
                                code=SAMPLE_CODE,
                            ),
                            TestAddresses.BOB: AccountState(
                                code=SAMPLE_CODE_2,
                            ),
                            TestAddresses.CHARLIE: AccountState(
                                code=SAMPLE_CODE,  # Same code - no change
                            ),
                        },
                    ),
                    txHash=TestTxHashes.TX1,
                )
            ],
            expected_result=BlockAccessList(
                code_diffs=[
                    AccountCodeDiff(
                        address=TestAddresses.ALICE,
                        new_code=SAMPLE_CODE,
                    ),
                    AccountCodeDiff(
                        address=TestAddresses.BOB,
                        new_code=SAMPLE_CODE_2,
                    ),
                    # Charlie excluded (no change)
                ]
            ),
        ),
        BALTestCase(
            description="Multiple transactions - last code change wins",
            trace_input=[
                # Transaction 0: Alice gets initial code
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState()
                        },
                        post={
                            TestAddresses.ALICE: AccountState(
                                code=SAMPLE_CODE,
                            )
                        },
                    ),
                    txHash=TestTxHashes.TX1,
                ),
                # Transaction 1: Alice code gets upgraded
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(
                                code=SAMPLE_CODE,
                            )
                        },
                        post={
                            TestAddresses.ALICE: AccountState(
                                code=SAMPLE_CODE_2,
                            )
                        },
                    ),
                    txHash=TestTxHashes.TX2,
                ),
            ],
            expected_result=BlockAccessList(
                code_diffs=[
                    AccountCodeDiff(
                        address=TestAddresses.ALICE,
                        new_code=SAMPLE_CODE_2,  # Last change wins
                    )
                ]
            ),
        ),
        BALTestCase(
            description="Code removal - from code to empty ignored",
            trace_input=[
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(
                                code=SAMPLE_CODE,
                            )
                        },
                        post={
                            TestAddresses.ALICE: AccountState(
                                # No code field = None/empty code
                            )
                        },
                    ),
                    txHash=TestTxHashes.TX1,
                )
            ],
            expected_result=BlockAccessList(),  # Empty code not tracked
        ),
    ]


def create_error_test_cases() -> List[tuple]:
    """Create test cases that should raise ValueError for oversized code."""
    
    # Code that exceeds MAX_CODE_SIZE
    OVERSIZED_CODE = "0x" + "60" * (MAX_CODE_SIZE + 1)
    
    return [
        (
            "Oversized code deployment raises ValueError",
            [
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState()
                        },
                        post={
                            TestAddresses.ALICE: AccountState(
                                code=OVERSIZED_CODE,
                            )
                        },
                    ),
                    txHash=TestTxHashes.TX1,
                )
            ],
            ValueError,
            f"Code size {MAX_CODE_SIZE + 1} exceeds maximum {MAX_CODE_SIZE} bytes",
        ),
    ]


class TestCodeDiffs:
    """Tests for code diffs functionality."""

    @pytest.mark.parametrize(
        "test_case", create_test_cases(), ids=lambda tc: tc.description
    )
    def test_code_diffs_from_execution_trace(self, test_case: BALTestCase):
        """Test code diffs with expected output."""
        # Execute the function under test
        result = from_execution_trace(test_case.trace_input)

        # Validate the result matches the expected BlockAccessList structure
        assert len(result.account_accesses) == len(
            test_case.expected_result.account_accesses
        )
        assert len(result.balance_diffs) == len(test_case.expected_result.balance_diffs)
        assert len(result.nonce_diffs) == len(test_case.expected_result.nonce_diffs)

        # Validate specific code_diffs (order-independent)
        assert len(result.code_diffs) == len(test_case.expected_result.code_diffs)

        # Convert to dictionaries for easier comparison
        result_by_address = {diff.address: diff for diff in result.code_diffs}
        expected_by_address = {
            diff.address: diff for diff in test_case.expected_result.code_diffs
        }

        assert set(result_by_address.keys()) == set(expected_by_address.keys())

        # Compare each address's code diff
        for address in expected_by_address:
            result_diff = result_by_address[address]
            expected_diff = expected_by_address[address]
            
            assert result_diff.address == expected_diff.address
            assert result_diff.new_code == expected_diff.new_code

    @pytest.mark.parametrize(
        "description,trace_input,expected_error,expected_message", 
        create_error_test_cases(),
    )
    def test_code_diffs_error_cases(
        self, description: str, trace_input: List[TransactionTrace], 
        expected_error: type, expected_message: str
    ):
        """Test that oversized code raises appropriate errors."""
        with pytest.raises(expected_error) as exc_info:
            from_execution_trace(trace_input)
        
        assert expected_message in str(exc_info.value)