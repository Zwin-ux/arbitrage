from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Any

import structlog

from .book_state import BookState
from .hashing import generate_orderbook_hash
from .models import (
    BestBidAskEvent,
    BookSnapshot,
    HealthIssue,
    LastTradePriceEvent,
    MarketLifecycleEvent,
    PriceChangeEvent,
    ProcessingResult,
    TickSizeChangeEvent,
)
from .storage import DuckDBStorage
from .utils import dedupe_preserve_order


class EventProcessor:
    def __init__(self, storage: DuckDBStorage):
        self._storage = storage
        self._books: dict[str, BookState] = {}
        self._logger = structlog.get_logger(self.__class__.__name__)

    @property
    def tracked_asset_ids(self) -> list[str]:
        return list(self._books)

    def get_stale_asset_ids(
        self,
        *,
        now_ms: int,
        stale_after_ms: int,
    ) -> list[str]:
        stale_assets: list[str] = []
        for asset_id, book in self._books.items():
            try:
                last_ts = int(book.timestamp)
            except ValueError:
                continue
            if now_ms - last_ts >= stale_after_ms:
                stale_assets.append(asset_id)
        return stale_assets

    def apply_bootstrap(
        self,
        snapshots: Iterable[BookSnapshot],
        *,
        source: str,
        recorded_at: datetime,
    ) -> None:
        for snapshot in snapshots:
            self._storage.store_raw_message(
                source=source,
                event_type="book",
                market=snapshot.market,
                asset_id=snapshot.asset_id,
                payload=snapshot.model_dump(mode="json"),
                recorded_at=recorded_at,
            )
            self._storage.store_book_snapshot(
                snapshot,
                source=source,
                recorded_at=recorded_at,
            )
            self._books[snapshot.asset_id] = BookState.from_snapshot(snapshot)

    def handle_message(
        self,
        payload: dict[str, Any],
        *,
        recorded_at: datetime,
    ) -> ProcessingResult:
        event_type = payload.get("event_type")
        if event_type is None:
            return ProcessingResult()
        if event_type == "book":
            book_event = BookSnapshot.model_validate(payload)
            return self._handle_book(book_event, recorded_at=recorded_at)
        if event_type == "price_change":
            price_change_event = PriceChangeEvent.model_validate(payload)
            return self._handle_price_change(price_change_event, recorded_at=recorded_at)
        if event_type == "tick_size_change":
            tick_size_event = TickSizeChangeEvent.model_validate(payload)
            return self._handle_tick_size_change(tick_size_event, recorded_at=recorded_at)
        if event_type == "last_trade_price":
            last_trade_event = LastTradePriceEvent.model_validate(payload)
            return self._handle_last_trade(last_trade_event, recorded_at=recorded_at)
        if event_type == "best_bid_ask":
            best_bid_ask_event = BestBidAskEvent.model_validate(payload)
            return self._handle_best_bid_ask(best_bid_ask_event, recorded_at=recorded_at)
        if event_type in {"new_market", "market_resolved"}:
            lifecycle_event = MarketLifecycleEvent.model_validate(payload)
            return self._handle_market_lifecycle(lifecycle_event, recorded_at=recorded_at)
        self._logger.warning("unknown_event_type", event_type=event_type)
        return ProcessingResult()

    def _handle_book(
        self,
        event: BookSnapshot,
        *,
        recorded_at: datetime,
    ) -> ProcessingResult:
        enriched_event = self._enrich_book_event(event)
        self._storage.store_raw_message(
            source="websocket",
            event_type=event.event_type,
            market=event.market,
            asset_id=event.asset_id,
            payload=event.model_dump(mode="json"),
            recorded_at=recorded_at,
        )
        computed_hash = (
            generate_orderbook_hash(enriched_event)
            if self._can_validate_book_hash(enriched_event)
            else None
        )
        issues: list[HealthIssue] = []
        if computed_hash is not None and computed_hash != enriched_event.hash:
            issues.append(
                HealthIssue(
                    issue_type="snapshot_hash_mismatch",
                    market=event.market,
                    asset_id=event.asset_id,
                    message="Computed snapshot hash does not match the server hash.",
                    observed_hash=computed_hash,
                    expected_hash=enriched_event.hash,
                    timestamp=event.timestamp,
                )
            )
        self._storage.store_book_snapshot(
            enriched_event,
            source="websocket",
            recorded_at=recorded_at,
        )
        self._books[event.asset_id] = BookState.from_snapshot(enriched_event)
        for issue in issues:
            self._storage.store_health_issue(issue, recorded_at=recorded_at)
        return ProcessingResult(health_issues=issues)

    def _enrich_book_event(self, event: BookSnapshot) -> BookSnapshot:
        if self._can_validate_book_hash(event):
            return event
        prior_book = self._books.get(event.asset_id)
        if prior_book is None:
            return event
        prior_snapshot = prior_book.as_snapshot()
        enriched_event = event.model_copy(deep=True)
        if enriched_event.min_order_size is None:
            enriched_event.min_order_size = prior_snapshot.min_order_size
        if enriched_event.tick_size is None:
            enriched_event.tick_size = prior_snapshot.tick_size
        if enriched_event.neg_risk is None:
            enriched_event.neg_risk = prior_snapshot.neg_risk
        if enriched_event.last_trade_price is None:
            enriched_event.last_trade_price = prior_snapshot.last_trade_price
        return enriched_event

    @staticmethod
    def _can_validate_book_hash(event: BookSnapshot) -> bool:
        return (
            event.min_order_size is not None
            and event.tick_size is not None
            and event.neg_risk is not None
            and event.last_trade_price is not None
        )

    def _handle_price_change(
        self,
        event: PriceChangeEvent,
        *,
        recorded_at: datetime,
    ) -> ProcessingResult:
        self._storage.store_raw_message(
            source="websocket",
            event_type=event.event_type,
            market=event.market,
            asset_id=None,
            payload=event.model_dump(mode="json"),
            recorded_at=recorded_at,
        )
        self._storage.store_price_change(event, recorded_at=recorded_at)
        backfill_asset_ids: list[str] = []
        issues: list[HealthIssue] = []
        for change in event.price_changes:
            book = self._books.get(change.asset_id)
            if book is None:
                issues.append(
                    HealthIssue(
                        issue_type="missing_book_for_price_change",
                        market=event.market,
                        asset_id=change.asset_id,
                        message="Received a price change before the recorder had a local book.",
                        expected_hash=change.hash,
                        timestamp=event.timestamp,
                    )
                )
                backfill_asset_ids.append(change.asset_id)
                continue
            book.apply_price_change(change, event.timestamp)
            validation = book.validate_hash(change.hash)
            best_bid = book.best_bid()
            best_ask = book.best_ask()
            if not validation.is_valid:
                issues.append(
                    HealthIssue(
                        issue_type="price_change_hash_mismatch",
                        market=event.market,
                        asset_id=change.asset_id,
                        message="Local book diverged from the price change hash.",
                        observed_hash=validation.observed_hash,
                        expected_hash=change.hash,
                        timestamp=event.timestamp,
                    )
                )
                backfill_asset_ids.append(change.asset_id)
            elif (
                change.best_bid is not None
                and best_bid is not None
                and change.best_bid != best_bid
            ) or (
                change.best_ask is not None
                and best_ask is not None
                and change.best_ask != best_ask
            ):
                issues.append(
                    HealthIssue(
                        issue_type="best_bid_ask_mismatch",
                        market=event.market,
                        asset_id=change.asset_id,
                        message="Local best bid/ask diverged from the change event.",
                        timestamp=event.timestamp,
                    )
                )
                backfill_asset_ids.append(change.asset_id)
        for issue in issues:
            self._storage.store_health_issue(issue, recorded_at=recorded_at)
        return ProcessingResult(
            backfill_asset_ids=dedupe_preserve_order(backfill_asset_ids),
            health_issues=issues,
        )

    def _handle_tick_size_change(
        self,
        event: TickSizeChangeEvent,
        *,
        recorded_at: datetime,
    ) -> ProcessingResult:
        self._storage.store_raw_message(
            source="websocket",
            event_type=event.event_type,
            market=event.market,
            asset_id=event.asset_id,
            payload=event.model_dump(mode="json"),
            recorded_at=recorded_at,
        )
        self._storage.store_tick_size_change(event, recorded_at=recorded_at)
        if event.asset_id in self._books:
            self._books[event.asset_id].set_tick_size(event.new_tick_size, event.timestamp)
        return ProcessingResult()

    def _handle_last_trade(
        self,
        event: LastTradePriceEvent,
        *,
        recorded_at: datetime,
    ) -> ProcessingResult:
        self._storage.store_raw_message(
            source="websocket",
            event_type=event.event_type,
            market=event.market,
            asset_id=event.asset_id,
            payload=event.model_dump(mode="json"),
            recorded_at=recorded_at,
        )
        self._storage.store_last_trade_price(event, recorded_at=recorded_at)
        if event.asset_id in self._books:
            self._books[event.asset_id].set_last_trade_price(event.price, event.timestamp)
        return ProcessingResult()

    def _handle_best_bid_ask(
        self,
        event: BestBidAskEvent,
        *,
        recorded_at: datetime,
    ) -> ProcessingResult:
        self._storage.store_raw_message(
            source="websocket",
            event_type=event.event_type,
            market=event.market,
            asset_id=event.asset_id,
            payload=event.model_dump(mode="json"),
            recorded_at=recorded_at,
        )
        self._storage.store_best_bid_ask(event, recorded_at=recorded_at)
        book = self._books.get(event.asset_id)
        issues: list[HealthIssue] = []
        backfill_asset_ids: list[str] = []
        if book is not None and (
            book.best_bid() != event.best_bid or book.best_ask() != event.best_ask
        ):
            issues.append(
                HealthIssue(
                    issue_type="best_bid_ask_mismatch",
                    market=event.market,
                    asset_id=event.asset_id,
                    message="best_bid_ask event disagreed with local book.",
                    timestamp=event.timestamp,
                )
            )
            backfill_asset_ids.append(event.asset_id)
        for issue in issues:
            self._storage.store_health_issue(issue, recorded_at=recorded_at)
        return ProcessingResult(
            backfill_asset_ids=backfill_asset_ids,
            health_issues=issues,
        )

    def _handle_market_lifecycle(
        self,
        event: MarketLifecycleEvent,
        *,
        recorded_at: datetime,
    ) -> ProcessingResult:
        self._storage.store_raw_message(
            source="websocket",
            event_type=event.event_type,
            market=event.market,
            asset_id=None,
            payload=event.model_dump(mode="json"),
            recorded_at=recorded_at,
        )
        self._storage.store_market_lifecycle(event, recorded_at=recorded_at)
        if event.event_type == "new_market":
            return ProcessingResult(new_asset_ids=event.assets_ids)
        if event.event_type == "market_resolved":
            return ProcessingResult(resolved_asset_ids=event.assets_ids)
        return ProcessingResult()
