# Mapping the void

## TL;DR

**Over a quarter** of a typical block's execution time is spent chasing data that does not exist.
These lookups are **over five times slower** because proving a value is absent requires descending
to the bottom of the trie and coming back empty-handed.

Marking absent entries in Block Access Lists (BAL) increases their size by only **0.4%** and
avoids most of this work during block validation.

## The void

A block with a median state access pattern is shown below.

![Void heatmap of the median block](results/25410001-25416000/void-heatmap.png)

Notice the large number of lookups that return void (marked red) - dominated by missing storage
slots, while missing accounts are comparatively rare.

This pattern is consistent across blocks. On average, **6%** of account lookups and **35%** of
storage lookups return void ([Appendix A](#appendix-a-analysis)).

![Void vs total accessed per block](results/25410001-25416000/void-trend.png)

The next question is whether these failed lookups are cheap.

## The cost of proving absence

Reading a void is decisively slower than reading real data — modestly for accounts (**1.8x**),
dramatically for storage (**5.1x**). Proving a slot is absent means descending the trie to the
bottom and coming back empty-handed; fetching an existing slot short-circuits as soon as
it's found.

![Read latency: existing vs void](results/25410001-25416000/cost-of-void.png)

## Encoding the void

A synthetic mainnet-shaped block (1,500 accounts, 1,650 storage slots) was chosen to
design the encoding.

**1. One flag per key.** The obvious representation is one flag per key indicating whether
the lookup returned void.

![One flag per key](results/encoding/design-1-flag.png)

**2. Replace flags with indexes.** Scattered flags can be compressed into indexes.
Empty accounts are indexed once at the BAL root. Empty storage is indexed within each account.
Since storage reads and writes are mutually exclusive, they share a single BAL-ordered sequence
(reads followed by writes). A single index is therefore sufficient for every empty storage lookup.
This reduces the encoding size by **79%**.

![Indexed flags](results/encoding/design-2-pointer.png)

**3. Pack the indexes into bitmaps.** The indexed information is purely boolean and can be packed into a bitmap.
Eight flags fit in a byte, reducing the encoding by another **40%**.

![Per-account bitmaps](results/encoding/design-3-scoped-bitmap.png)

**4. Two global bitmaps.** The per-account storage bitmap still wastes space. An account touching one or two slots
still occupies a full byte, along with an RLP field header. Packing the bits across account boundaries removes
this overhead. The result is two global bitmaps at the BAL root: one for accounts and one for storage.

This is exactly what the [heatmap above](#the-void) represents.

![Two global bitmaps](results/encoding/design-4-global-bitmap.png)

**399 bytes**, a **76%** reduction compared to the per-account bitmap, and **97%** smaller than
the baseline flag-based design.

The final design is as small as a bitmap can be:

* Accounts bitmap: `ceil(1500 / 8)` = **188 bytes**
* Storage bitmap: `ceil(1650 / 8)` = **207 bytes**

Total bitmap payload: **188 + 207 = 395 bytes**. The remaining **4 bytes** are RLP header overhead.


| Encoding | Cost | Reduction vs. baseline |
|----------|-----:|-----------------------:|
| One flag per key | 13.6 kB | — |
| Indexed flags | 2.8 kB | 79% |
| Per-account bitmaps | 1.7 kB | 87% |
| Two global bitmaps | **399 B** | **97%** |


## Skipping the void

Void-marked BAL reduces mean block execution time by **29.8%** across the analysed mainnet range.

![Block execution time: baseline vs void-marked](results/25410001-25416000/block-processing.png)

The improvement comes from skipping expensive trie traversals for absent state.
Mean state read latency falls by **436x** for account lookups and **177x** for storage lookups.

![Void read latency: disk vs bitmap](results/25410001-25416000/void-skip.png)

The optimization comes at almost no cost. Recording void entries increases BAL size by only 0.4%.

![BAL size: baseline vs void-marked](results/25410001-25416000/bal-size.png)

## Appendix A: Analysis

**The sample.** 6,000 mainnet blocks (25410001–25416000).

**The client.** The baseline arm is geth built from the `glamsterdam-devnet-6` branch, with EIP-7928 BAL
enabled on the Fusaka fork and no other Amsterdam EIPs. Execution and gas usage therefore remain identical
to mainnet, and the BAL reflects real access patterns.

The export command adds a `--with-bal` flag that writes each block's recomputed BAL
as a sidecar, producing a stream of `[block, BAL]`. The state reader adds a timer metric for every
disk read, split by whether it finds data or proves absence.

The void-bitmap arm branches from the same baseline. Its BAL carries the void bitmaps, producing `[block, EmptyBAL]`.
During import, reads marked absent are answered from the bitmap instead of traversing the trie.

**The commands.** Export requires the archival state-history index:

```sh
geth --datadir <snapshot> --state.scheme path --gcmode archive \
  export --with-bal blocks.rlp 25410001 25416000
```

Import replays the sample:

```sh
geth --datadir <snapshot> --state.scheme path import --with-bal blocks.rlp
```

Geth's trie prefetcher was enabled during the run.

**Beetle.** A small harness, [**beetle**](https://github.com/raxhvl/pokebal/tree/main/analysis/mapping-the-void/beetle), automates export, import, and analysis.
Each run uses a disposable copy-on-write clone of the snapshot. This adds a small amount
of disk I/O latency, but both arms pay the same cost, so it cancels out in the comparison.
Absolute latencies may therefore differ slightly from a production deployment,
while the reported speedups remain unaffected.

**Hardware.**

* OS: Debian GNU/Linux 13 (trixie)
* Kernel: Linux 6.12.95+deb13-cloud-amd64
* Virtualization: kvm (QEMU)
* CPU: 16 core vCPU @ 2.0GHz
* Memory: 32G
* Disk: QEMU HARDDISK (2TB)
