"""World Liberty Fi (WLFI) integration.

World Liberty Fi is a DeFi protocol whose large on-chain trades and governance
announcements regularly move crypto prices and create correlated opportunities
in Polymarket prediction markets.  This module provides:

* ``WLFI_MARKET_KEYWORDS`` – a curated keyword list for surfacing WLFI-related
  prediction markets from a Gamma discovery snapshot.
* ``WLFI_BENCHMARK_SYMBOLS`` – pre-configured crypto benchmark symbol presets
  for WLFI and USD1 that can be synced via the existing benchmark infrastructure.
* ``WLFIMarketScanner`` – lightweight helper that filters a
  :class:`~market_data_recorder.models.DiscoverySnapshot` or queries the Gamma
  API directly for markets matching any WLFI keyword.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .models import DiscoveredMarket, DiscoverySnapshot

if TYPE_CHECKING:
    from .clients.gamma import GammaClient


# ---------------------------------------------------------------------------
# Configuration constants
# ---------------------------------------------------------------------------

#: Keywords used to filter Polymarket events and markets related to
#: World Liberty Fi, its governance token (WLFI), or its USD-pegged
#: stablecoin (USD1).
WLFI_MARKET_KEYWORDS: list[str] = [
    "world liberty",
    "worldliberty",
    "worldlibertyfi",
    "wlfi",
    "usd1",
]

#: Pre-configured (symbol, instrument_type) pairs for syncing WLFI-related
#: price history via the existing benchmark infrastructure
#: (``market-data-recorder benchmark sync``).
WLFI_BENCHMARK_SYMBOLS: list[tuple[str, str]] = [
    ("WLFI-USD", "crypto"),
    ("USD1-USD", "crypto"),
]


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

class WLFIMarketScanner:
    """Surfaces WLFI-related markets from Polymarket.

    Usage – filter an existing discovery snapshot::

        from market_data_recorder.models import DiscoverySnapshot
        from market_data_recorder.wlfi import WLFIMarketScanner

        scanner = WLFIMarketScanner()
        related = scanner.scan(snapshot)

    Usage – live search via the Gamma API::

        from market_data_recorder.clients.gamma import GammaClient
        from market_data_recorder.wlfi import WLFIMarketScanner

        scanner = WLFIMarketScanner()
        results = asyncio.run(scanner.fetch(gamma_client))
    """

    def __init__(self, keywords: list[str] | None = None) -> None:
        self._keywords = [k.lower() for k in (keywords or WLFI_MARKET_KEYWORDS)]

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def scan(self, snapshot: DiscoverySnapshot) -> list[DiscoveredMarket]:
        """Return markets from *snapshot* that match any WLFI keyword.

        The match is case-insensitive and checks the event title, market
        question, market slug, and event slug.
        """
        matched: list[DiscoveredMarket] = []
        for item in snapshot.items:
            if self._item_matches(item):
                matched.append(item)
        return matched

    async def fetch(
        self,
        gamma_client: GammaClient,
        *,
        limit: int = 100,
        max_pages: int | None = 5,
    ) -> list[DiscoveredMarket]:
        """Discover markets live from the Gamma API and return WLFI-related ones.

        This performs a full paginated discovery (capped by *max_pages*) and
        then applies :meth:`scan` to the result.  Use this when no local
        snapshot is available or when you need up-to-date data.
        """
        snapshot = await gamma_client.discover_markets(
            limit=limit,
            order="volume_24hr",
            ascending=False,
            max_pages=max_pages,
        )
        return self.scan(snapshot)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _item_matches(self, item: DiscoveredMarket) -> bool:
        candidates = [
            item.event.title or "",
            item.event.slug or "",
            item.market.question or "",
            item.market.slug or "",
        ]
        text = " ".join(candidates).lower()
        return any(kw in text for kw in self._keywords)
