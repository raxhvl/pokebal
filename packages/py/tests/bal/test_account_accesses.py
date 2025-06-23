"""Tests if `account_accesses` is computed correctly."""

import pytest
from typing import List
from bal.builder import from_execution_trace
from bal.types import BlockAccessList, AccountAccess, SlotAccess, PerTxAccess
from tests.utils import (
    TestAddresses,
    TestTxHashes,
    BALTestCase,
    to_evm_word,
)
from rpc.types import (
    TransactionTrace,
    PrePostStates,
    AccountState,
)


def create_test_cases() -> List[BALTestCase]:
    """Create test case data following functional programming principles."""

    return [
        BALTestCase(
            description="Empty trace produces no account accesses",
            trace_input=[],
            expected_result=BlockAccessList(),
        ),
        BALTestCase(
            description="Transaction with no storage changes ignored",
            trace_input=[
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(
                                balance="0x64",  # 100 wei
                                storage={
                                    to_evm_word(0): to_evm_word(0x100),  # Same value
                                },
                            )
                        },
                        post={
                            TestAddresses.ALICE: AccountState(
                                balance="0x64",  # Same balance - no balance change
                                storage={
                                    to_evm_word(0): to_evm_word(
                                        0x100
                                    ),  # Same value - no storage change
                                },
                            )
                        },
                    ),
                    txHash=TestTxHashes.TX1,
                )
            ],
            expected_result=BlockAccessList(),
        ),
        BALTestCase(
            description="Alice single storage slot change in single transaction",
            trace_input=[
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(
                                storage={
                                    to_evm_word(0): to_evm_word(0x100),
                                }
                            )
                        },
                        post={
                            TestAddresses.ALICE: AccountState(
                                storage={
                                    to_evm_word(0): to_evm_word(0x200),
                                }
                            )
                        },
                    ),
                    txHash=TestTxHashes.TX1,
                )
            ],
            expected_result=BlockAccessList(
                account_accesses=[
                    AccountAccess(
                        address=TestAddresses.ALICE,
                        accesses=[
                            SlotAccess(
                                slot=to_evm_word(0),
                                accesses=[
                                    PerTxAccess(
                                        tx_index=0,
                                        value_after=to_evm_word(0x200),
                                    )
                                ],
                            )
                        ],
                    )
                ]
            ),
        ),
        BALTestCase(
            description="Alice multiple storage slots in single transaction",
            trace_input=[
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(
                                storage={
                                    to_evm_word(0): to_evm_word(0x100),
                                    to_evm_word(1): to_evm_word(0x200),
                                    to_evm_word(2): to_evm_word(0x300),
                                }
                            )
                        },
                        post={
                            TestAddresses.ALICE: AccountState(
                                storage={
                                    to_evm_word(0): to_evm_word(0x150),  # Changed
                                    to_evm_word(1): to_evm_word(0x200),  # Unchanged
                                    to_evm_word(2): to_evm_word(0x350),  # Changed
                                }
                            )
                        },
                    ),
                    txHash=TestTxHashes.TX1,
                )
            ],
            expected_result=BlockAccessList(
                account_accesses=[
                    AccountAccess(
                        address=TestAddresses.ALICE,
                        accesses=[
                            SlotAccess(
                                slot=to_evm_word(0),
                                accesses=[
                                    PerTxAccess(
                                        tx_index=0,
                                        value_after=to_evm_word(0x150),
                                    )
                                ],
                            ),
                            SlotAccess(
                                slot=to_evm_word(2),
                                accesses=[
                                    PerTxAccess(
                                        tx_index=0,
                                        value_after=to_evm_word(0x350),
                                    )
                                ],
                            ),
                        ],
                    )
                ]
            ),
        ),
        BALTestCase(
            description="Missing storage field defaults to empty, new slot created",
            trace_input=[
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(
                                balance="0x64"  # No storage field
                            )
                        },
                        post={
                            TestAddresses.ALICE: AccountState(
                                balance="0x64",
                                storage={
                                    to_evm_word(0): to_evm_word(0x500),
                                },
                            )
                        },
                    ),
                    txHash=TestTxHashes.TX1,
                )
            ],
            expected_result=BlockAccessList(
                account_accesses=[
                    AccountAccess(
                        address=TestAddresses.ALICE,
                        accesses=[
                            SlotAccess(
                                slot=to_evm_word(0),
                                accesses=[
                                    PerTxAccess(
                                        tx_index=0,
                                        value_after=to_evm_word(0x500),
                                    )
                                ],
                            )
                        ],
                    )
                ]
            ),
        ),
        BALTestCase(
            description="Storage slot deleted (missing from post state)",
            trace_input=[
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(
                                storage={
                                    to_evm_word(0): to_evm_word(0x1000),
                                }
                            )
                        },
                        post={
                            TestAddresses.ALICE: AccountState(
                                # No storage field = all slots go to 0x0
                            )
                        },
                    ),
                    txHash=TestTxHashes.TX1,
                )
            ],
            expected_result=BlockAccessList(
                account_accesses=[
                    AccountAccess(
                        address=TestAddresses.ALICE,
                        accesses=[
                            SlotAccess(
                                slot=to_evm_word(0),
                                accesses=[
                                    PerTxAccess(
                                        tx_index=0,
                                        value_after=to_evm_word(0x0),  # Deleted = 0x0
                                    )
                                ],
                            )
                        ],
                    )
                ]
            ),
        ),
        BALTestCase(
            description="Multiple accounts single transaction",
            trace_input=[
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(
                                storage={to_evm_word(0): to_evm_word(0x100)}
                            ),
                            TestAddresses.BOB: AccountState(
                                storage={to_evm_word(1): to_evm_word(0x200)}
                            ),
                        },
                        post={
                            TestAddresses.ALICE: AccountState(
                                storage={to_evm_word(0): to_evm_word(0x150)}
                            ),
                            TestAddresses.BOB: AccountState(
                                storage={to_evm_word(1): to_evm_word(0x250)}
                            ),
                        },
                    ),
                    txHash=TestTxHashes.TX1,
                )
            ],
            expected_result=BlockAccessList(
                account_accesses=[
                    AccountAccess(
                        address=TestAddresses.ALICE,
                        accesses=[
                            SlotAccess(
                                slot=to_evm_word(0),
                                accesses=[
                                    PerTxAccess(
                                        tx_index=0,
                                        value_after=to_evm_word(0x150),
                                    )
                                ],
                            )
                        ],
                    ),
                    AccountAccess(
                        address=TestAddresses.BOB,
                        accesses=[
                            SlotAccess(
                                slot=to_evm_word(1),
                                accesses=[
                                    PerTxAccess(
                                        tx_index=0,
                                        value_after=to_evm_word(0x250),
                                    )
                                ],
                            )
                        ],
                    ),
                ]
            ),
        ),
        BALTestCase(
            description="Same slot of an account changed across multiple transactions",
            trace_input=[
                # Transaction 0: Alice slot 0 changes from 0x100 to 0x200
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(
                                storage={to_evm_word(0): to_evm_word(0x100)}
                            )
                        },
                        post={
                            TestAddresses.ALICE: AccountState(
                                storage={to_evm_word(0): to_evm_word(0x200)}
                            )
                        },
                    ),
                    txHash=TestTxHashes.TX1,
                ),
                # Transaction 1: Alice slot 0 changes from 0x200 to 0x300
                TransactionTrace(
                    result=PrePostStates(
                        pre={
                            TestAddresses.ALICE: AccountState(
                                storage={to_evm_word(0): to_evm_word(0x200)}
                            )
                        },
                        post={
                            TestAddresses.ALICE: AccountState(
                                storage={to_evm_word(0): to_evm_word(0x300)}
                            )
                        },
                    ),
                    txHash=TestTxHashes.TX2,
                ),
            ],
            expected_result=BlockAccessList(
                account_accesses=[
                    AccountAccess(
                        address=TestAddresses.ALICE,
                        accesses=[
                            SlotAccess(
                                slot=to_evm_word(0),
                                accesses=[
                                    PerTxAccess(
                                        tx_index=0,
                                        value_after=to_evm_word(0x200),
                                    ),
                                    PerTxAccess(
                                        tx_index=1,
                                        value_after=to_evm_word(0x300),
                                    ),
                                ],
                            )
                        ],
                    )
                ]
            ),
        ),
    ]


class TestAccountAccesses:
    """Tests for account accesses functionality."""

    @pytest.mark.parametrize(
        "test_case", create_test_cases(), ids=lambda tc: tc.description
    )
    def test_account_accesses_from_execution_trace(self, test_case: BALTestCase):
        """Test account accesses with expected output."""
        # Execute the function under test
        result = from_execution_trace(test_case.trace_input)

        # Validate the result matches the expected BlockAccessList structure
        assert len(result.balance_diffs) == len(test_case.expected_result.balance_diffs)
        assert len(result.code_diffs) == len(test_case.expected_result.code_diffs)
        assert len(result.nonce_diffs) == len(test_case.expected_result.nonce_diffs)

        # Validate specific account_accesses (order-independent)
        assert len(result.account_accesses) == len(
            test_case.expected_result.account_accesses
        )

        # Convert to dictionaries for easier comparison
        result_by_address = {acc.address: acc for acc in result.account_accesses}
        expected_by_address = {
            acc.address: acc for acc in test_case.expected_result.account_accesses
        }

        assert set(result_by_address.keys()) == set(expected_by_address.keys())

        # Compare each address's accesses
        for address in expected_by_address:
            result_access = result_by_address[address]
            expected_access = expected_by_address[address]

            assert len(result_access.accesses) == len(expected_access.accesses)

            # Convert slot accesses to dictionaries for comparison
            result_slots = {slot.slot: slot for slot in result_access.accesses}
            expected_slots = {slot.slot: slot for slot in expected_access.accesses}

            assert set(result_slots.keys()) == set(expected_slots.keys())

            # Compare each slot's per-transaction accesses
            for slot_key in expected_slots:
                result_slot = result_slots[slot_key]
                expected_slot = expected_slots[slot_key]

                assert len(result_slot.accesses) == len(expected_slot.accesses)

                for result_per_tx, expected_per_tx in zip(
                    result_slot.accesses, expected_slot.accesses
                ):
                    assert result_per_tx.tx_index == expected_per_tx.tx_index
                    assert result_per_tx.value_after == expected_per_tx.value_after
