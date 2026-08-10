"""Real async client for an offset-paginated vendor API. Bounded concurrency
via a semaphore, same idea as the demo's mock source: fetch many pages at
once instead of waiting for each one to finish before starting the next.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass

import httpx


@dataclass
class Page:
    items: list[dict]


class OrdersAPIClient:
    def __init__(self, base_url: str, max_concurrent: int = 5, timeout: float = 30):
        self.base_url = base_url
        self._client = httpx.AsyncClient(timeout=timeout)
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def get_total_count(self) -> int:
        resp = await self._client.get(f"{self.base_url}/orders/count")
        resp.raise_for_status()
        return resp.json()["count"]

    async def fetch_page(self, page_index: int, page_size: int) -> Page:
        async with self._semaphore:
            resp = await self._client.get(
                f"{self.base_url}/orders",
                params={"offset": page_index * page_size, "limit": page_size},
            )
            resp.raise_for_status()
            return Page(items=resp.json()["items"])

    async def aclose(self) -> None:
        await self._client.aclose()
