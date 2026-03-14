from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from .models import ArbitrageLeg, ArbitrageOpportunity
from .storage import DuckDBStorage


def _format_decimal(value: Decimal) -> str:
    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered or "0"


class ArbitrageAnalyzer:
    def __init__(self, storage: DuckDBStorage):
        self._storage = storage

    def find_opportunities(
        self,
        *,
        min_edge: str = "0",
        market_ids: list[str] | None = None,
    ) -> list[ArbitrageOpportunity]:
        minimum_edge = Decimal(min_edge)
        grouped_rows: dict[str, list[tuple[str, str | None, str, str, str]]] = defaultdict(list)
        for market, asset_id, outcome, timestamp, best_bid, best_ask in self._storage.fetch_latest_best_bid_ask():
            if market_ids is not None and market not in market_ids:
                continue
            grouped_rows[str(market)].append(
                (
                    str(asset_id),
                    None if outcome is None else str(outcome),
                    str(timestamp),
                    str(best_bid),
                    str(best_ask),
                )
            )

        opportunities: list[ArbitrageOpportunity] = []
        for market, rows in grouped_rows.items():
            if len(rows) < 2:
                continue
            timestamp = max(row[2] for row in rows)
            legs = [
                ArbitrageLeg(
                    asset_id=asset_id,
                    outcome=outcome,
                    best_bid=best_bid,
                    best_ask=best_ask,
                )
                for asset_id, outcome, _timestamp, best_bid, best_ask in rows
            ]
            buy_total = sum([Decimal(leg.best_ask) for leg in legs], Decimal("0"))
            buy_profit = Decimal("1") - buy_total
            if buy_profit >= minimum_edge:
                opportunities.append(
                    ArbitrageOpportunity(
                        market=market,
                        strategy="buy_all_outcomes",
                        timestamp=timestamp,
                        total_price=_format_decimal(buy_total),
                        guaranteed_profit=_format_decimal(buy_profit),
                        outcome_count=len(legs),
                        legs=legs,
                    )
                )
            sell_total = sum([Decimal(leg.best_bid) for leg in legs], Decimal("0"))
            sell_profit = sell_total - Decimal("1")
            if sell_profit >= minimum_edge:
                opportunities.append(
                    ArbitrageOpportunity(
                        market=market,
                        strategy="sell_all_outcomes",
                        timestamp=timestamp,
                        total_price=_format_decimal(sell_total),
                        guaranteed_profit=_format_decimal(sell_profit),
                        outcome_count=len(legs),
                        legs=legs,
                    )
                )

        opportunities.sort(
            key=lambda opportunity: Decimal(opportunity.guaranteed_profit),
            reverse=True,
        )
        return opportunities
