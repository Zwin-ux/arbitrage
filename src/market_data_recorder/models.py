from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Literal, cast

from pydantic import BaseModel, ConfigDict, Field, field_validator


JsonDict = dict[str, Any]


def _parse_json_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, str):
        if not value:
            return []
        return cast(list[Any], json.loads(value))
    if isinstance(value, list):
        return value
    raise TypeError(f"Unsupported list payload: {type(value)!r}")


class PriceLevel(BaseModel):
    price: str
    size: str


class BookSnapshot(BaseModel):
    event_type: Literal["book"] = "book"
    asset_id: str
    market: str
    bids: list[PriceLevel]
    asks: list[PriceLevel]
    timestamp: str
    hash: str
    min_order_size: str | None = None
    tick_size: str | None = None
    neg_risk: bool | None = None
    last_trade_price: str | None = None


class PriceChangeEntry(BaseModel):
    asset_id: str
    price: str
    size: str
    side: Literal["BUY", "SELL"]
    hash: str | None = None
    best_bid: str | None = None
    best_ask: str | None = None


class PriceChangeEvent(BaseModel):
    event_type: Literal["price_change"]
    market: str
    price_changes: list[PriceChangeEntry]
    timestamp: str


class TickSizeChangeEvent(BaseModel):
    event_type: Literal["tick_size_change"]
    asset_id: str
    market: str
    old_tick_size: str
    new_tick_size: str
    timestamp: str


class LastTradePriceEvent(BaseModel):
    event_type: Literal["last_trade_price"]
    asset_id: str
    market: str
    price: str
    side: Literal["BUY", "SELL"]
    size: str
    fee_rate_bps: str | None = None
    timestamp: str


class BestBidAskEvent(BaseModel):
    event_type: Literal["best_bid_ask"]
    asset_id: str
    market: str
    best_bid: str
    best_ask: str
    spread: str | None = None
    timestamp: str


class MarketLifecycleEvent(BaseModel):
    model_config = ConfigDict(extra="allow")

    event_type: Literal["new_market", "market_resolved"]
    id: str
    question: str
    market: str
    slug: str
    description: str
    assets_ids: list[str]
    outcomes: list[str]
    timestamp: str
    event_message: JsonDict | None = None
    winning_asset_id: str | None = None
    winning_outcome: str | None = None


class PolymarketMarket(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    market_id: str = Field(alias="id")
    condition_id: str | None = Field(default=None, alias="conditionId")
    question: str | None = None
    slug: str | None = None
    description: str | None = None
    active: bool = False
    closed: bool = False
    accepting_orders: bool | None = Field(default=None, alias="acceptingOrders")
    enable_order_book: bool = Field(default=False, alias="enableOrderBook")
    order_price_min_tick_size: float | None = Field(
        default=None, alias="orderPriceMinTickSize"
    )
    order_min_size: float | None = Field(default=None, alias="orderMinSize")
    neg_risk: bool | None = Field(default=None, alias="negRisk")
    fees_enabled: bool | None = Field(default=None, alias="feesEnabled")
    outcomes: list[str] = Field(default_factory=list)
    clob_token_ids: list[str] = Field(default_factory=list, alias="clobTokenIds")
    outcome_prices: list[str] = Field(default_factory=list, alias="outcomePrices")

    @field_validator("outcomes", "clob_token_ids", "outcome_prices", mode="before")
    @classmethod
    def _deserialize_json_lists(cls, value: Any) -> list[Any]:
        return _parse_json_list(value)


class PolymarketEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    event_id: str = Field(alias="id")
    ticker: str | None = None
    slug: str | None = None
    title: str | None = None
    description: str | None = None
    active: bool = False
    closed: bool = False
    markets: list[PolymarketMarket] = Field(default_factory=list)


class DiscoveredMarket(BaseModel):
    event: PolymarketEvent
    market: PolymarketMarket

    @property
    def asset_ids(self) -> list[str]:
        return self.market.clob_token_ids


class DiscoverySnapshot(BaseModel):
    discovered_at: datetime
    items: list[DiscoveredMarket]

    @property
    def asset_ids(self) -> list[str]:
        ordered: list[str] = []
        for item in self.items:
            ordered.extend(item.asset_ids)
        return ordered


class SubscriptionMessage(BaseModel):
    assets_ids: list[str]
    type: Literal["market"] = "market"
    custom_feature_enabled: bool = True


class HealthIssue(BaseModel):
    issue_type: str
    market: str | None = None
    asset_id: str | None = None
    message: str
    observed_hash: str | None = None
    expected_hash: str | None = None
    timestamp: str | None = None


class ProcessingResult(BaseModel):
    new_asset_ids: list[str] = Field(default_factory=list)
    resolved_asset_ids: list[str] = Field(default_factory=list)
    backfill_asset_ids: list[str] = Field(default_factory=list)
    health_issues: list[HealthIssue] = Field(default_factory=list)


class ReplaySummary(BaseModel):
    raw_messages: int = 0
    book_messages: int = 0
    price_change_messages: int = 0
    last_trade_messages: int = 0
    best_bid_ask_messages: int = 0
    tick_size_messages: int = 0
    lifecycle_messages: int = 0
    final_books: int = 0


class VerificationReport(BaseModel):
    snapshot_hash_failures: int = 0
    stream_hash_failures: int = 0
    best_bid_ask_failures: int = 0
    unknown_books: int = 0
    issues: list[HealthIssue] = Field(default_factory=list)
