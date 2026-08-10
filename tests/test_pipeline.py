"""Smoke tests, not a full suite. Run directly: python tests/test_pipeline.py"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from etl.mock_source import MockOrdersSource
from etl.pipeline import concurrent_fetch, sequential_fetch


def test_sequential_and_concurrent_return_identical_rows():
    source = MockOrdersSource(total_items=250, page_size=50, latency_s=0)

    sequential_items = asyncio.run(sequential_fetch(source))
    concurrent_items = asyncio.run(concurrent_fetch(source, max_concurrent=5))

    assert len(sequential_items) == 250
    assert sorted(i["id"] for i in sequential_items) == sorted(i["id"] for i in concurrent_items)


def test_concurrent_fetch_is_faster_with_simulated_latency():
    import time

    source = MockOrdersSource(total_items=200, page_size=20, latency_s=0.01)

    start = time.perf_counter()
    asyncio.run(sequential_fetch(source))
    sequential_s = time.perf_counter() - start

    start = time.perf_counter()
    asyncio.run(concurrent_fetch(source, max_concurrent=10))
    concurrent_s = time.perf_counter() - start

    assert concurrent_s < sequential_s


if __name__ == "__main__":
    test_sequential_and_concurrent_return_identical_rows()
    test_concurrent_fetch_is_faster_with_simulated_latency()
    print("all tests passed")
