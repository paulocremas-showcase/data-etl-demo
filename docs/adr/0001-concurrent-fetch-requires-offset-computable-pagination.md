# 1. Concurrent fetch requires offset-computable pagination

Date: 2026-08-22

## Status

Accepted

## Context

Fetching a paginated API sequentially, one page after the next, is correct
but slow: each page waits on the previous one's round trip even though the
pages don't depend on each other's *content*, only on knowing what to ask
for next.

Concurrent fetching (`etl/pipeline.py`'s `concurrent_fetch`) removes that
wait by computing every page's offset up front and requesting all pages at
once, bounded by a semaphore. That only works if the offset for page N can
be computed from N alone, before any page has been fetched.

This was ported from one system where it measured a large, reproducible
speedup (see `etl/benchmark.py` and the README) into a second, related
system on the assumption that the same pattern would help there too. It
didn't: that second API used cursor-based pagination behind an unindexed
filter, so requesting pages out of order forced the server to re-scan from
the start each time, and concurrent fetching measured 1.6 to 2.8x *slower*,
not faster.

## Decision

Concurrent fetch is applied only when a page's request can be fully
constructed from its index, with no dependency on a previous page's
response. `sequential_fetch` and `concurrent_fetch` are required to return
identical rows (enforced by both the test suite and `benchmark.py`'s own
assertion) precisely so this substitution is checked, not assumed, every
time it's made.

## Consequences

- The pattern is not a default reached for on every extraction pipeline; it
  requires actively confirming the API's pagination shape first.
- The "recognize a proven pattern and generalize it" instinct that produced
  the win here also produced the regression on the other API. The fix isn't
  to stop generalizing, it's to verify correctness *and* measure before
  switching a live pipeline over, every time, not just the first time.
- Reverting a pattern that doesn't generalize to a specific case is treated
  as a normal outcome to disclose, not a failure to hide.
