# Mapping the void

## TL;DR

**Over a quarter** of a typical block's execution time is spent chasing data that does not exist.
These lookups are **over five times slower** because proving a value is absent requires descending
to the bottom of the trie and coming back empty-handed.

Marking absent entries in Block Access Lists (BAL) increases their size by only **0.4%** and
avoids most of this work.
