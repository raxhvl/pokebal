from pathlib import Path
import json
from pokebal.bal.types import (
    BlockAccessList,
    AccountChanges,
    SlotChanges,
    StorageChange,
    BalanceChange,
    NonceChange,
    CodeChange,
)
from pokebal.bal.serialization import (
    _transform_storage_change,
    _transform_balance_change,
    _transform_nonce_change,
    _transform_code_change,
    _transform_slot_changes,
    _transform_account_changes,
)
from typing import Any


def normalize_to_bytes(data: Any) -> Any:
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


def test_transform_storage_change():
    change = StorageChange(tx_index=63, new_value=b"\x01" * 32)
    result = _transform_storage_change(change)
    assert result == (63, b"\x01" * 32)


def test_transform_balance_change():
    balance_bytes = (123456).to_bytes(16, byteorder="little")
    change = BalanceChange(tx_index=42, post_balance=balance_bytes)
    result = _transform_balance_change(change)
    assert result == (42, 123456)


def test_transform_nonce_change():
    change = NonceChange(tx_index=42, new_nonce=10)
    result = _transform_nonce_change(change)
    assert result == (42, 10)


def test_transform_code_change():
    code = b"\x60\x80\x60\x40"
    change = CodeChange(tx_index=42, new_code=code)
    result = _transform_code_change(change)
    assert result == (42, code)


def test_transform_slot_changes():
    storage_changes = [
        StorageChange(tx_index=1, new_value=b"\x01" * 32),
        StorageChange(tx_index=2, new_value=b"\x02" * 32),
    ]
    slot_changes = SlotChanges(slot=b"\xff" * 32, changes=storage_changes)
    result = _transform_slot_changes(slot_changes)

    expected = (b"\xff" * 32, [(1, b"\x01" * 32), (2, b"\x02" * 32)])
    assert result == expected


def test_empty_block_access_list_serialization():
    bal = BlockAccessList()
    result = bal.serialize()
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_simple_block_access_list_serialization():
    account = AccountChanges(address=b"\x01" * 20)
    bal = BlockAccessList(account_changes=[account])
    result = bal.serialize()
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_complex_block_access_list_serialization():
    storage_change = StorageChange(tx_index=1, new_value=b"\xaa" * 32)
    slot_changes = SlotChanges(slot=b"\xbb" * 32, changes=[storage_change])

    balance_change = BalanceChange(
        tx_index=2, post_balance=(1000).to_bytes(16, "little")
    )
    nonce_change = NonceChange(tx_index=3, new_nonce=5)
    code_change = CodeChange(tx_index=4, new_code=b"\x60\x80")

    account = AccountChanges(
        address=b"\x01" * 20,
        storage_changes=[slot_changes],
        storage_reads=[b"\xcc" * 32],
        balance_changes=[balance_change],
        nonce_changes=[nonce_change],
        code_changes=[code_change],
    )

    bal = BlockAccessList(account_changes=[account])
    result = bal.serialize()
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_fixture_data_serialization():
    fixtures_path = Path(__file__).parent.parent / "fixtures" / "22615532.json"
    with open(fixtures_path) as f:
        data = json.load(f)
        normalized_data = normalize_to_bytes(data)

        bal = BlockAccessList(**normalized_data)
        result = bal.serialize()

        assert isinstance(result, bytes)
        assert len(result) > 0
        assert len(bal.account_changes) > 0


def test_fixture_ssz_validation():
    """Test that our serialized SSZ matches the expected .ssz fixture file."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures"
    json_path = fixtures_dir / "22615532.json"
    ssz_path = fixtures_dir / "22615532.ssz"

    # Load and parse JSON fixture
    with open(json_path) as f:
        data = json.load(f)
        normalized_data = normalize_to_bytes(data)
        bal = BlockAccessList(**normalized_data)

    # Serialize using our implementation
    serialized_result = bal.serialize()

    # Read expected SSZ file
    with open(ssz_path, "rb") as f:
        expected_ssz = f.read()

    # Validate that our serialization matches expected output
    assert isinstance(serialized_result, bytes), "Serialized result should be bytes"
    assert isinstance(expected_ssz, bytes), "Expected SSZ should be bytes"
    assert len(serialized_result) > 0, "Serialized result should not be empty"
    assert len(expected_ssz) > 0, "Expected SSZ should not be empty"

    # Debug: Find first difference
    for i, (a, b) in enumerate(zip(serialized_result, expected_ssz)):
        if a != b:
            print(f"First difference at byte {i}: got {hex(a)} expected {hex(b)}")
            print(f"Context around byte {i}:")
            start = max(0, i - 10)
            end = min(len(serialized_result), i + 10)
            print(f"Got:      {serialized_result[start:end].hex()}")
            print(f"Expected: {expected_ssz[start:end].hex()}")
            break

    # The main validation: our serialization should match the fixture
    assert serialized_result == expected_ssz, (
        f"Serialized SSZ doesn't match fixture. "
        f"Got {len(serialized_result)} bytes, expected {len(expected_ssz)} bytes"
    )


def test_serialization_functional_composition():
    storage_change = StorageChange(tx_index=1, new_value=b"\x12" * 32)
    slot_changes = SlotChanges(slot=b"\x34" * 32, changes=[storage_change])
    account = AccountChanges(address=b"\x56" * 20, storage_changes=[slot_changes])

    account_tuple = _transform_account_changes(account)
    assert len(account_tuple) == 6
    assert account_tuple[0] == b"\x56" * 20
    assert len(account_tuple[1]) == 1
    assert account_tuple[1][0] == (b"\x34" * 32, [(1, b"\x12" * 32)])
