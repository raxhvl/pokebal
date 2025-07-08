"""Simple conversion utilities for hex string to bytes transformations."""


def hex_to_bytes(hex_string: str) -> bytes:
    """Convert hex string to bytes.
    
    Args:
        hex_string: Hex string with or without '0x' prefix
        
    Returns:
        bytes: The decoded bytes
    """
    if hex_string.startswith('0x'):
        hex_string = hex_string[2:]
    
    if not hex_string:
        return b''
    
    # Ensure even length
    if len(hex_string) % 2 != 0:
        hex_string = '0' + hex_string
    
    return bytes.fromhex(hex_string)


def bytes_to_hex(data: bytes) -> str:
    """Convert bytes to hex string with 0x prefix.
    
    Args:
        data: The bytes to convert
        
    Returns:
        str: Hex string with 0x prefix
    """
    return f"0x{data.hex()}"