"""Test utilities and constants for easier reasoning about tests."""

from pydantic import BaseModel
from rpc.types import BlockDebugTraceResult
from bal.types import BlockAccessList
from common.types import EVMWord


class TestAddresses:
    """Named test addresses for better test readability."""

    ALICE = "0x1234567890abcdef1234567890abcdef12345678"
    BOB = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"
    CHARLIE = "0x1111111111111111111111111111111111111111"
    DAVE = "0x2222222222222222222222222222222222222222"
    EVE = "0x3333333333333333333333333333333333333333"
    FRANK = "0x4444444444444444444444444444444444444444"
    GRACE = "0x5555555555555555555555555555555555555555"


class TestTxHashes:
    """Named test transaction hashes for better test readability."""

    TX1 = "0x1111111111111111111111111111111111111111111111111111111111111111"
    TX2 = "0x2222222222222222222222222222222222222222222222222222222222222222"
    TX3 = "0x3333333333333333333333333333333333333333333333333333333333333333"
    TX4 = "0x4444444444444444444444444444444444444444444444444444444444444444"
    TX5 = "0x5555555555555555555555555555555555555555555555555555555555555555"


class BALTestCase(BaseModel):
    """Generic test case data structure for Block Access List testing.

    This can be used to test different aspects of BlockAccessList generation:
    - Complete BlockAccessList validation
    - Individual field testing (balance_diffs, account_accesses, code_diffs, nonce_diffs)
    """

    description: str
    trace_input: BlockDebugTraceResult
    expected_result: BlockAccessList


def to_evm_word(value: int) -> EVMWord:
    """Convert integer to 32-byte hex EVM word."""
    return f"0x{value:064x}"
