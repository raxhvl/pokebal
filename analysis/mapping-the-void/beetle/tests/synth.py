"""Build synthetic empty-arm exports in the shape sidecar.py documents.

Small pieces (account/entry/bitmap) serve the unit tests; write_export
streams a mainnet-shaped range to disk for the opt-in scale test — a ~190 KB
opaque tx blob stands in for the block body, and the BAL carries ~1500
accounts / ~1650 slots (the essay's mainnet-shaped block). Sidecar variants
are pre-encoded once and cycled block % V, so generation runs at write speed
and every block's expected tallies are recomputable from VARIANTS.
"""

from pathlib import Path

import rlp

FIRST = 23_000_000  # mainnet-era numbering
BODY_BLOB = b"\xbb" * 190_000

# (accounts, slots, void accounts, void slots) — jittered around the essay's
# mainnet-shaped block so entries aren't byte-identical
VARIANTS = [
    (1500, 1650, 300, 500),
    (1350, 1480, 270, 440),
    (1650, 1820, 330, 550),
    (1420, 1560, 280, 470),
    (1580, 1740, 320, 520),
]


def addr(i: int) -> bytes:
    return i.to_bytes(20, "big")


def key(i: int) -> bytes:
    return i.to_bytes(32, "big")


def account(address: bytes, write_keys: list[bytes], read_keys: list[bytes]) -> list:
    writes = [[k, b""] for k in write_keys]
    return [address, writes, read_keys, b"", b"", b""]


def bitmap(flags: list[bool]) -> bytes:
    value = sum(1 << i for i, f in enumerate(flags) if f)
    return value.to_bytes((len(flags) + 7) // 8, "little")


def void_flags(n: int, void: int) -> list[bool]:
    """Deterministic spread: every step-th item void until the quota is spent."""
    step = max(n // void, 1)
    marked = set(range(0, void * step, step))
    return [i in marked for i in range(n)]


def empty_arm(bal: list, account_void: list[bool], slot_void: list[bool]) -> bytes:
    return rlp.encode([bal, bitmap(account_void), bitmap(slot_void)])


def entry(number: int, sidecar_payload: bytes, body_blob: bytes = b"") -> bytes:
    header = [b"\xaa" * 32] * 8 + [number] + [b""] * 6  # number sits at index 8
    block = [header, [body_blob] if body_blob else [], [], []]
    return rlp.encode([block, sidecar_payload])


def variant_sidecar(accounts: int, slots: int, void_a: int, void_s: int) -> bytes:
    bal = []
    remaining = slots
    for i in range(accounts):
        share = min(remaining, (slots // accounts) + (1 if i < slots % accounts else 0))
        reads = [key(i * 10_000 + j) for j in range(share)]
        remaining -= share
        bal.append(account(addr(i), [], reads))
    assert remaining == 0
    return empty_arm(bal, void_flags(accounts, void_a), void_flags(slots, void_s))


def write_export(path: Path, blocks: int, progress=lambda msg: None) -> None:
    """Stream a mainnet-shaped export of `blocks` entries to `path`."""
    sidecars = [variant_sidecar(*v) for v in VARIANTS]
    with path.open("wb", buffering=1 << 22) as f:
        for i in range(blocks):
            f.write(entry(FIRST + i, sidecars[i % len(VARIANTS)], BODY_BLOB))
            if i and i % 10_000 == 0:
                progress(f"{i}/{blocks} blocks, {f.tell() / 1e9:.1f} GB")


def expected(i: int) -> tuple[int, int, int, int]:
    """Block i's (accounts, void accounts, slots, void slots) by construction."""
    accounts, slots, void_a, void_s = VARIANTS[i % len(VARIANTS)]
    return accounts, void_a, slots, void_s
