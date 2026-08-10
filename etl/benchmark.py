"""Measures the actual speedup from concurrent fetching against the same
mock source, so the claim in the README is something you can run, not just
read. Real production numbers on a real vendor API were higher (18x); this
demo's ratio depends on the simulated latency and page count below.
"""
from __future__ import annotations

import argparse
import asyncio
import time

from .mock_source import MockOrdersSource
from .pipeline import concurrent_fetch, sequential_fetch


async def run(total_items: int, page_size: int, latency_s: float, max_concurrent: int) -> None:
    source = MockOrdersSource(total_items=total_items, page_size=page_size, latency_s=latency_s)
    print(f"{source.page_count} pages, {latency_s * 1000:.0f}ms simulated latency per page")

    start = time.perf_counter()
    sequential_items = await sequential_fetch(source)
    sequential_s = time.perf_counter() - start

    start = time.perf_counter()
    concurrent_items = await concurrent_fetch(source, max_concurrent=max_concurrent)
    concurrent_s = time.perf_counter() - start

    assert sorted(i["id"] for i in sequential_items) == sorted(i["id"] for i in concurrent_items), (
        "sequential and concurrent fetch must return the same rows"
    )

    print(f"sequential:  {sequential_s:.2f}s")
    print(f"concurrent:  {concurrent_s:.2f}s  (max_concurrent={max_concurrent})")
    print(f"speedup:     {sequential_s / concurrent_s:.1f}x")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--total-items", type=int, default=3000)
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--latency-ms", type=float, default=50)
    parser.add_argument("--max-concurrent", type=int, default=10)
    args = parser.parse_args()

    asyncio.run(
        run(args.total_items, args.page_size, args.latency_ms / 1000, args.max_concurrent)
    )


if __name__ == "__main__":
    main()
