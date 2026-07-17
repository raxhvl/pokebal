"""Pin the export shape the streaming decoder walks, and that it streams.

The synthetic entries (built by synth.py) mirror the geth `export --with-bal`
layout the sidecar module documents.
"""

import tracemalloc

import pytest
import rlp

import sidecar
import synth
from synth import account, addr, bitmap, empty_arm, entry, key

# block A: acct0 writes 2 slots and re-reads one of them (2 unique), acct1
# reads 1, acct2 touches none -> 3 accounts, 3 slots
BAL_A = [
    account(addr(1), [key(1), key(2)], [key(2)]),
    account(addr(2), [], [key(3)]),
    account(addr(3), [], []),
]
A_ACCT_VOID = [True, False, True]
A_SLOT_VOID = [True, True, False]

# block B: 1 account, 4 read slots
BAL_B = [account(addr(9), [], [key(i) for i in range(4)])]
B_ACCT_VOID = [False]
B_SLOT_VOID = [True, False, True, True]


@pytest.fixture
def export(tmp_path):
    path = tmp_path / "empty.rlp"
    path.write_bytes(
        entry(23_000_000, empty_arm(BAL_A, A_ACCT_VOID, A_SLOT_VOID))
        + entry(23_000_001, empty_arm(BAL_B, B_ACCT_VOID, B_SLOT_VOID),
                body_blob=b"\xbb" * 5000)
    )
    return path


def test_scan_tallies_in_block_order(export):
    rows = sidecar.scan(export)
    assert [r.number for r in rows] == [23_000_000, 23_000_001]
    a, b = rows
    assert (a.accounts, a.void_accounts, a.slots, a.void_slots) == (3, 2, 3, 2)
    assert (b.accounts, b.void_accounts, b.slots, b.void_slots) == (1, 0, 4, 3)


def test_load_recovers_exact_flags_at_offset(export):
    rows = sidecar.scan(export)
    block = sidecar.load(export, rows[1].offset)
    assert block.number == 23_000_001
    assert block.account_void == B_ACCT_VOID
    assert block.slot_void == B_SLOT_VOID


def test_decode_matches_scan(export):
    blocks = sidecar.decode(export)
    assert [(b.number, b.account_void, b.slot_void) for b in blocks] == [
        (23_000_000, A_ACCT_VOID, A_SLOT_VOID),
        (23_000_001, B_ACCT_VOID, B_SLOT_VOID),
    ]


def test_pad_bit_past_last_item_rejected(tmp_path):
    bad_bitmap = bytes([bitmap(A_SLOT_VOID)[0] | 0x20])  # bit 5 set, 3 items
    payload = rlp.encode([BAL_A, bitmap(A_ACCT_VOID), bad_bitmap])
    path = tmp_path / "padbit.rlp"
    path.write_bytes(entry(1, payload))
    with pytest.raises(ValueError, match="pad bit"):
        sidecar.scan(path)


def test_truncated_bitmap_rejected(tmp_path):
    """A short bitmap must not zero-extend into phantom 'exists' flags —
    it means our item count disagrees with the one geth sized the bitmap to."""
    payload = rlp.encode([BAL_A, bitmap(A_ACCT_VOID), b""])  # 3 slots need 1 byte
    path = tmp_path / "short.rlp"
    path.write_bytes(entry(1, payload))
    with pytest.raises(ValueError, match="0 bytes for 3 items"):
        sidecar.scan(path)


def test_oversized_bitmap_rejected_even_with_zero_pad(tmp_path):
    bad_bitmap = bitmap(A_SLOT_VOID) + b"\x00"  # extra byte, passes the pad-bit check
    payload = rlp.encode([BAL_A, bitmap(A_ACCT_VOID), bad_bitmap])
    path = tmp_path / "long.rlp"
    path.write_bytes(entry(1, payload))
    with pytest.raises(ValueError, match="2 bytes for 3 items"):
        sidecar.scan(path)


def test_base_arm_sidecar_rejected(tmp_path):
    path = tmp_path / "base.rlp"
    path.write_bytes(entry(1, rlp.encode(BAL_A[:2])))  # bal only, no bitmaps
    with pytest.raises(ValueError, match="empty arm"):
        sidecar.scan(path)


def test_synth_export_tallies_match_construction(tmp_path):
    path = tmp_path / "synth.rlp"
    synth.write_export(path, blocks=10)
    rows = sidecar.scan(path)
    assert [r.number for r in rows] == list(range(synth.FIRST, synth.FIRST + 10))
    for i, r in enumerate(rows):
        assert (r.accounts, r.void_accounts, r.slots, r.void_slots) == synth.expected(i)


def test_scan_streams_instead_of_loading_the_file(tmp_path):
    """Python-heap peak while scanning must stay far below the file size —
    the pre-streaming decoder read the whole export into memory, which a
    mainnet-range export (tens of GB) does not allow."""
    payload = empty_arm(BAL_A, A_ACCT_VOID, A_SLOT_VOID)
    blob = b"\xcc" * 1_000_000
    path = tmp_path / "big.rlp"
    with path.open("wb") as f:
        for i in range(300):
            f.write(entry(23_000_000 + i, payload, body_blob=blob))
    size = path.stat().st_size
    assert size > 250_000_000

    tracemalloc.start()
    try:
        rows = sidecar.scan(path)
    finally:
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        sidecar.scan.cache_clear()

    assert len(rows) == 300
    assert all((r.accounts, r.slots) == (3, 3) for r in rows)
    assert peak < 32_000_000, f"scan heap peaked at {peak} bytes for a {size}-byte file"
