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

Library only — nothing runs it from the shell. Metrics import `decode`.
"""

from dataclasses import dataclass
from pathlib import Path

import rlp
from rlp.codec import consume_length_prefix

_HEADER_NUMBER = 8  # index of `number` within the block header


def _split_items(buf: bytes):
    """Yield (start, end) byte ranges for each top-level RLP item in buf."""
    i, n = 0, len(buf)
    while i < n:
        _, _, content_start, content_len = consume_length_prefix(buf, i)
        end = content_start + content_len
        yield i, end
        i = end


def _flags(bitmap: bytes, n: int) -> list[bool]:
    """Unpack the first n bits of a void bitmap into per-item flags.

    Bits are LSB-first within each byte, byte 0 first — pinned by the padding
    check below: every bit past item n-1 must be zero, which only holds under
    this convention (a set pad bit would mean we're reading the wrong end).
    """
    flags = [bool((bitmap[i // 8] >> (i % 8)) & 1) for i in range(n)]
    for i in range(n, len(bitmap) * 8):
        if (bitmap[i // 8] >> (i % 8)) & 1:
            raise ValueError(f"void bitmap: pad bit {i} set (bad bit order or count)")
    return flags


@dataclass(frozen=True)
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


def _slot_count(bal) -> int:
    total = 0
    for _addr, writes, reads, *_ in bal:
        total += len({sc[0] for sc in writes} | set(reads))
    return total


def decode(path) -> list[BlockVoid]:
    """Decode an empty-arm export into per-block void tallies, block order."""
    buf = Path(path).read_bytes()
    out = []
    for start, end in _split_items(buf):
        block, sidecar = rlp.decode(buf[start:end])
        number = int.from_bytes(block[0][_HEADER_NUMBER], "big")
        decoded = rlp.decode(sidecar)
        if len(decoded) != 3:
            raise ValueError(
                f"block {number}: sidecar has {len(decoded)} fields, expected 3 "
                "([bal, voidAccountBitmap, voidSlotBitmap]) — is this the empty arm?"
            )
        bal, bm_accounts, bm_slots = decoded
        account_void = _flags(bm_accounts, len(bal))
        slot_void = _flags(bm_slots, _slot_count(bal))
        out.append(BlockVoid(number, account_void, slot_void))
    return out
