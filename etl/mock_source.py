"""In-memory fake orders API for the demo and benchmark: simulates real
network latency per request (via asyncio.sleep) so the benchmark's timing
comparison means something, without needing an actual server.

Offset-based pagination like this is what makes concurrent fetching possible
at all: every page's offset is computable in advance from the total count,
so there's no need to wait for page N's response before requesting page N+1.
"""
from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass


@dataclass
class Page:
    items: list[dict]


class MockOrdersSource:
    def __init__(self, total_items: int = 3000, page_size: int = 100, latency_s: float = 0.05, seed: int = 7):
        self.total_items = total_items
        self.page_size = page_size
        self.latency_s = latency_s
        self._rng = random.Random(seed)  # noqa: S311 -- deterministic mock data, not a security use

    @property
    def page_count(self) -> int:
        return (self.total_items + self.page_size - 1) // self.page_size

    async def fetch_page(self, page_index: int) -> Page:
        await asyncio.sleep(self.latency_s)  # stands in for real network round-trip time
        offset = page_index * self.page_size
        end = min(offset + self.page_size, self.total_items)
        items = [
            {"id": f"order-{i}", "total": round(self._rng.uniform(20, 800), 2)}
            for i in range(offset, end)
        ]
        return Page(items=items)
