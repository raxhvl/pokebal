"""Test utilities for common operations."""

from typing import Any


def normalize_to_bytes(data: Any) -> Any:
    """Convert hex strings to bytes recursively.
    
    This function traverses nested data structures and converts hex strings
    (with or without '0x' prefix) to bytes objects.
    
    Args:
        data: Input data that may contain hex strings
        
    Returns:
        Data with hex strings converted to bytes
    """
    if isinstance(data, dict):
        return {k: normalize_to_bytes(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [normalize_to_bytes(elem) for elem in data]
    elif isinstance(data, str):
        original_string = data
        hex_part = original_string

        if original_string.lower().startswith("0x"):
            hex_part = original_string[2:]

        if not all(c in "0123456789abcdefABCDEF" for c in hex_part):
            return original_string

        try:
            if len(hex_part) % 2 != 0:
                hex_part = "0" + hex_part
            return bytes.fromhex(hex_part)
        except ValueError:
            return original_string
    else:
        return data