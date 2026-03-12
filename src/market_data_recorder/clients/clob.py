from __future__ import annotations

from collections.abc import Sequence

import httpx

from ..models import BookSnapshot
from ..utils import chunked, dedupe_preserve_order


class ClobClient:
    def __init__(
        self,
        base_url: str,
        client: httpx.AsyncClient | None = None,
    ):
        self._base_url = base_url.rstrip("/")
        self._client = client or httpx.AsyncClient(timeout=30.0)
        self._owns_client = client is None

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def get_book(self, asset_id: str) -> BookSnapshot:
        response = await self._client.get(
            f"{self._base_url}/book",
            params={"token_id": asset_id},
        )
        response.raise_for_status()
        return BookSnapshot.model_validate(response.json())

    async def get_books(self, asset_ids: Sequence[str]) -> list[BookSnapshot]:
        response = await self._client.post(
            f"{self._base_url}/books",
            json=[{"token_id": asset_id} for asset_id in asset_ids],
        )
        response.raise_for_status()
        return [BookSnapshot.model_validate(item) for item in response.json()]

    async def get_books_batched(
        self,
        asset_ids: Sequence[str],
        *,
        batch_size: int,
    ) -> list[BookSnapshot]:
        results: list[BookSnapshot] = []
        unique_asset_ids = dedupe_preserve_order(asset_ids)
        for batch in chunked(unique_asset_ids, batch_size):
            results.extend(await self.get_books(batch))
        return results
