"""Decode a geth `export --with-bal` stream into per-block void structures.

The stream is a concatenation of top-level RLP items, one per exported block:

    entry := [ block, sidecar ]
    block   := [ header, txs, uncles, withdrawals ]   (standard geth block RLP)
    sidecar := [ bal, voidAccountBitmap, voidSlotBitmap ]   (empty arm)
             | bal                                          (base arm, no bitmaps)
    bal     := [ account, ... ]
    account := [ address, storageWrites, storageReads, balanceΔ, nonceΔ, codeΔ ]

The void bitmaps carry one bit per listed item, in BAL order: a set bit marks an
item that was void (non-existent account / zero slot) at block start. This shape
is pinned by tests against real exports, not read out of geth's Go.

Mainnet-range exports run to tens of GB, so nothing here reads a whole file
into memory: the file is mmapped and walked by RLP length prefix, and only
each entry's sidecar is decoded — the block body, most of the bytes, is
skipped over (bar the header's number field). `scan` streams the file into
small per-block tallies; `load` decodes the one block a metric wants full
bitmaps for; `sizes` streams per-block BAL byte sizes (raw and snappy)
without decoding, and so works on either arm.

Library only — nothing runs it from the shell. Metrics import `scan`/`load`/`sizes`.
"""

import functools
import mmap
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

import rlp
import snappy
from rlp.codec import consume_length_prefix

_HEADER_NUMBER = 8  # index of `number` within the block header


@contextmanager
def _mapped(path):
    with open(path, "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as buf:
        yield buf


def _item(buf, pos: int) -> tuple[int, int]:
    """(payload_start, payload_end) of the RLP item at pos.

    payload_end is also where the next sibling item starts.
    """
    _, _, length, payload = consume_length_prefix(buf, pos)
    return payload, payload + length


def _number(buf, block_pos: int) -> int:
    """The block number, read off the header without decoding the body."""
    header_pos, _ = _item(buf, block_pos)  # block payload starts at its header
    pos, _ = _item(buf, header_pos)
    for _ in range(_HEADER_NUMBER):
        _, pos = _item(buf, pos)
    start, end = _item(buf, pos)
    return int.from_bytes(buf[start:end], "big")


def _entries(buf, pos: int = 0):
    """Yield (offset, number, sidecar payload span) per entry, from pos on."""
    size = len(buf)
    while pos < size:
        block_pos, entry_end = _item(buf, pos)
        _, block_end = _item(buf, block_pos)
        yield pos, _number(buf, block_pos), _item(buf, block_end)
        pos = entry_end


def _bits(bitmap: bytes, n: int, number: int) -> int:
    """The bitmap as an int: bit i is item i (LSB-first within each byte,
    byte 0 first — exactly little-endian).

    geth sized the bitmap to *its* item count, so the byte length must equal
    ours exactly, and every bit past item n-1 must be zero — a disagreement
    in item counts or bit order fails loudly instead of zero-extending into
    phantom flags. Every block of a real export re-proves the shape this way.
    """
    if len(bitmap) != (n + 7) // 8:
        raise ValueError(
            f"block {number}: void bitmap is {len(bitmap)} bytes "
            f"for {n} items, expected {(n + 7) // 8}"
        )
    value = int.from_bytes(bitmap, "little")
    if value >> n:
        raise ValueError(
            f"block {number}: void bitmap pad bits set (bad bit order or count)"
        )
    return value


def _flags(value: int, n: int) -> list[bool]:
    return [bool(value >> i & 1) for i in range(n)]


def _slot_count(bal) -> int:
    total = 0
    for _addr, writes, reads, *_ in bal:
        total += len({sc[0] for sc in writes} | set(reads))
    return total


def _sidecar(buf, span: tuple[int, int], number: int) -> tuple[int, int, int, int]:
    """Decode one sidecar payload into (accounts, account bits, slots, slot bits)."""
    start, end = span
    decoded = rlp.decode(buf[start:end])
    if len(decoded) != 3:
        raise ValueError(
            f"block {number}: sidecar has {len(decoded)} fields, expected 3 "
            "([bal, voidAccountBitmap, voidSlotBitmap]) — is this the empty arm?"
        )
    bal, bm_accounts, bm_slots = decoded
    accounts, slots = len(bal), _slot_count(bal)
    return (
        accounts,
        _bits(bm_accounts, accounts, number),
        slots,
        _bits(bm_slots, slots, number),
    )


@dataclass(frozen=True, slots=True)
class BlockScan:
    """One block's void tallies, plus where its entry sits in the export."""

    number: int
    accounts: int
    void_accounts: int
    slots: int
    void_slots: int
    offset: int


@dataclass(frozen=True, slots=True)
class BlockSize:
    """One block's BAL bytes: raw, and snappy block-format compressed.

    `raw` is the sidecar payload length — exactly the `balRLP` geth meters
    (`chain/bal/size`), bitmaps included on the empty arm. `compressed` is
    `snappy.compress(balRLP)`, matching geth's `snappy.Encode(nil, balRLP)`
    (`chain/bal/size/compressed`). Both arms size the same way, so nothing
    here decodes — it walks the RLP framing and measures the bytes.
    """

    number: int
    raw: int
    compressed: int


@dataclass(frozen=True, slots=True)
class BlockVoid:
    """One block's void bitmaps: per accessed item, was it void at block start?

    `account_void[i]` / `slot_void[i]` are in BAL order (the order geth listed
    them in the sidecar). True = void (non-existent account / zero slot).
    """

    number: int
    account_void: list[bool]
    slot_void: list[bool]

    @property
    def accounts(self) -> int:
        return len(self.account_void)

    @property
    def void_accounts(self) -> int:
        return sum(self.account_void)

    @property
    def slots(self) -> int:
        return len(self.slot_void)

    @property
    def void_slots(self) -> int:
        return sum(self.slot_void)

    @property
    def account_void_share(self) -> float:
        return self.void_accounts / self.accounts if self.accounts else 0.0

    @property
    def slot_void_share(self) -> float:
        return self.void_slots / self.slots if self.slots else 0.0


@functools.cache
def scan(path: Path) -> list[BlockScan]:
    """Stream an empty-arm export into per-block void tallies, block order.

    One pass, holding one sidecar at a time. Cached per path, so metrics that
    share an export share the pass; for one block's full bitmaps, hand its
    `offset` to `load`.
    """
    out = []
    with _mapped(path) as buf:
        for offset, number, span in _entries(buf):
            accounts, a_bits, slots, s_bits = _sidecar(buf, span, number)
            out.append(
                BlockScan(
                    number, accounts, a_bits.bit_count(), slots, s_bits.bit_count(), offset
                )
            )
    return out


@functools.cache
def sizes(path: Path) -> list[BlockSize]:
    """Stream an export into per-block BAL byte sizes, raw and snappy.

    Works on either arm — the sidecar payload is `balRLP` in both, so this
    only measures the span and compresses it, never decoding the BAL. Cached
    per path like `scan`.
    """
    out = []
    with _mapped(path) as buf:
        for _offset, number, (start, end) in _entries(buf):
            raw = buf[start:end]
            out.append(BlockSize(number, len(raw), len(snappy.compress(raw))))
    return out


def load(path, offset: int) -> BlockVoid:
    """Decode the single entry at `offset` (a BlockScan's) into full bitmaps."""
    with _mapped(path) as buf:
        _, number, span = next(_entries(buf, offset))
        accounts, a_bits, slots, s_bits = _sidecar(buf, span, number)
        return BlockVoid(number, _flags(a_bits, accounts), _flags(s_bits, slots))


def decode(path) -> list[BlockVoid]:
    """Every block's full bitmaps in memory — tests and spot checks only.

    Metrics stream with `scan` and pinpoint with `load`; a mainnet-range
    export's bitmaps do not all fit in memory at once.
    """
    out = []
    with _mapped(path) as buf:
        for _, number, span in _entries(buf):
            accounts, a_bits, slots, s_bits = _sidecar(buf, span, number)
            out.append(BlockVoid(number, _flags(a_bits, accounts), _flags(s_bits, slots)))
    return out
