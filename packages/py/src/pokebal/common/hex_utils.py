"""Simple conversion utilities for hex string to bytes transformations."""

BALANCE_BYTE_LENGTH = 16


def hex_to_bytes(hex_string: str) -> bytes:
    """Convert hex string to bytes.

    Args:
        hex_string: Hex string with or without '0x' prefix

    Returns:
        bytes: The decoded bytes
    """
    if hex_string.startswith("0x"):
        hex_string = hex_string[2:]

    if not hex_string:
        return b""

    # Ensure even length
    if len(hex_string) % 2 != 0:
        hex_string = "0" + hex_string

    return bytes.fromhex(hex_string)


def bytes_to_hex(data: bytes) -> str:
    """Convert bytes to hex string with 0x prefix.

    Args:
        data: The bytes to convert

    Returns:
        str: Hex string with 0x prefix
    """
    return f"0x{data.hex()}"


def encode_balance(value: int) -> bytes:
    """Convert integer to bytes with specified length.

    Args:
        value: The integer to convert

    Returns:
        bytes: The integer as big-endian bytes
    """
    return value.to_bytes(BALANCE_BYTE_LENGTH, byteorder="big", signed=True)


def bytes_to_int(data: bytes) -> int:
    """Convert bytes to integer.

    Args:
        data: The bytes to convert

    Returns:
        int: The integer value from big-endian bytes
    """
    return int.from_bytes(data, byteorder="big")
