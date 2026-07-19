# Mapping the void

## TL;DR

About a **quarter** of a typical block's execution time is spent chasing data that does not exist. These lookups are up to **five times slower** because proving a value is absent requires descending to the bottom of the trie and coming back empty-handed.

Marking absent entries in Block Access Lists (BAL) increases their size by only **X%** and avoids much of this work.
