from __future__ import annotations

from datetime import datetime, timezone

import httpx
import structlog

from ..models import DiscoveredMarket, DiscoverySnapshot, PolymarketEvent


class GammaClient:
    def __init__(
        self,
        base_url: str,
        client: httpx.AsyncClient | None = None,
    ):
        self._base_url = base_url.rstrip("/")
        self._client = client or httpx.AsyncClient(timeout=30.0)
        self._owns_client = client is None
        self._logger = structlog.get_logger(self.__class__.__name__)

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def fetch_events(
        self,
        *,
        limit: int,
        offset: int,
        active: bool,
        closed: bool,
        order: str,
        ascending: bool,
    ) -> list[PolymarketEvent]:
        params: dict[str, str | int] = {
            "limit": limit,
            "offset": offset,
            "active": str(active).lower(),
            "closed": str(closed).lower(),
            "order": order,
            "ascending": str(ascending).lower(),
        }
        response = await self._client.get(f"{self._base_url}/events", params=params)
        if response.status_code == 422 and order:
            self._logger.warning(
                "gamma_order_rejected_retrying_without_order",
                order=order,
                response_text=response.text,
            )
            params.pop("order", None)
            params.pop("ascending", None)
            response = await self._client.get(f"{self._base_url}/events", params=params)
        response.raise_for_status()
        payload = response.json()
        return [PolymarketEvent.model_validate(item) for item in payload]

    async def discover_markets(
        self,
        *,
        limit: int,
        order: str,
        ascending: bool,
        max_pages: int | None = None,
    ) -> DiscoverySnapshot:
        offset = 0
        page_number = 0
        items: list[DiscoveredMarket] = []
        while True:
            if max_pages is not None and page_number >= max_pages:
                break
            page = await self.fetch_events(
                limit=limit,
                offset=offset,
                active=True,
                closed=False,
                order=order,
                ascending=ascending,
            )
            if not page:
                break
            for event in page:
                for market in event.markets:
                    if not market.enable_order_book:
                        continue
                    if market.closed:
                        continue
                    if not market.clob_token_ids:
                        continue
                    items.append(DiscoveredMarket(event=event, market=market))
            if len(page) < limit:
                break
            offset += limit
            page_number += 1
        self._logger.info("discovered_markets", markets=len(items))
        return DiscoverySnapshot(
            discovered_at=datetime.now(timezone.utc),
            items=items,
        )
