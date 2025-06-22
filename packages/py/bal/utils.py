"""Utility functions for Block Access List operations."""


# Test Address Constants for easier reasoning about tests
class TestAddresses:
    """Named test addresses for better test readability."""

    ALICE = "0x1234567890abcdef1234567890abcdef12345678"
    BOB = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"
    CHARLIE = "0x1111111111111111111111111111111111111111"
    DAVE = "0x2222222222222222222222222222222222222222"
    EVE = "0x3333333333333333333333333333333333333333"
    FRANK = "0x4444444444444444444444444444444444444444"
    GRACE = "0x5555555555555555555555555555555555555555"


def int_to_hex(value: int) -> str:
    """Convert integer to hex string with 0x prefix.

    Pure function for converting integers to hex format for AccountState balance fields.
    Returns hex string with minimal representation (no padding).
    """
    return hex(value)


def is_valid_balance_delta(delta: int) -> bool:
    """Validate that balance delta fits in 12-byte two's complement.

    Pure function for validating balance deltas.
    12 bytes = 96 bits, signed range: -2^95 to 2^95-1
    """
    max_value = 2**95 - 1
    min_value = -(2**95)
    return min_value <= delta <= max_value


def encode_balance_delta(delta: int) -> str:
    """Encode balance delta as 12-byte two's complement hex string.

    Pure function that converts integer delta to EIP-7928 compliant format.
    Raises ValueError if delta doesn't fit in 12 bytes.
    """
    if not is_valid_balance_delta(delta):
        raise ValueError(
            f"Balance delta {delta} exceeds 12-byte two's complement range"
        )

    # Convert to 12-byte two's complement
    if delta >= 0:
        # Positive: straightforward conversion
        delta_bytes = delta.to_bytes(12, byteorder="big", signed=False)
    else:
        # Negative: use two's complement
        delta_bytes = delta.to_bytes(12, byteorder="big", signed=True)

    return "0x" + delta_bytes.hex()
