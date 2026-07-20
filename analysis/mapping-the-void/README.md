# Mapping the void

## TL;DR

**Over a quarter** of a typical block's execution time is spent chasing data that does not exist.
These lookups are **over five times slower** because proving a value is absent requires descending
to the bottom of the trie and coming back empty-handed.

Marking absent entries in Block Access Lists (BAL) increases their size by only **0.4%** and
avoids most of this work.

## The void

A block with a median state access pattern is shown below.

![Void heatmap of the median block](results/25410001-25416000/void-heatmap.png)

Notice the large number of lookups that return void (marked red) - dominated by missing storage
slots, while missing accounts are comparatively rare.

This pattern is consistent across blocks. On average, **6%** of account lookups and **35%** of
storage lookups return void (Appendix A).

![Void vs total accessed per block](results/25410001-25416000/void-trend.png)

The next question is whether these failed lookups are cheap.

## The cost of proving absence

Reading a void is decisively slower than reading real data — modestly for accounts (1.8x),
dramatically for storage (5.1x). Proving a slot is absent means descending the trie to the
bottom and coming back empty-handed; fetching an existing slot short-circuits as soon as
it's found.

![Read latency: existing vs void](results/25410001-25416000/cost-of-void.png)
