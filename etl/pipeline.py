"""Two ways to fetch the same paginated dataset: one page at a time, or many
pages at once bounded by a semaphore. Both return the same rows; only the
wall-clock time differs. See benchmark.py for the actual measurement, and
the README for when this trades off badly instead of well.
"""
from __future__ import annotations

import asyncio

from .mock_source import MockOrdersSource


async def sequential_fetch(source: MockOrdersSource) -> list[dict]:
    items: list[dict] = []
    for page_index in range(source.page_count):
        page = await source.fetch_page(page_index)
        items.extend(page.items)
    return items


async def concurrent_fetch(source: MockOrdersSource, max_concurrent: int = 10) -> list[dict]:
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_one(page_index: int) -> list[dict]:
        async with semaphore:
            page = await source.fetch_page(page_index)
            return page.items

    pages = await asyncio.gather(*(fetch_one(i) for i in range(source.page_count)))
    items: list[dict] = []
    for page_items in pages:
        items.extend(page_items)
    return items
