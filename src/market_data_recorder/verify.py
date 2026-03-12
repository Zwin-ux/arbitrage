from __future__ import annotations

import json

from .book_state import BookState
from .hashing import generate_orderbook_hash
from .models import (
    BestBidAskEvent,
    BookSnapshot,
    HealthIssue,
    LastTradePriceEvent,
    PriceChangeEvent,
    TickSizeChangeEvent,
    VerificationReport,
)
from .storage import DuckDBStorage


class RecorderVerifier:
    def __init__(self, storage: DuckDBStorage):
        self._storage = storage

    def verify(self) -> VerificationReport:
        report = VerificationReport()
        report.issues.extend(self._verify_snapshots(report))
        report.issues.extend(self._verify_stream(report))
        return report

    def _verify_snapshots(self, report: VerificationReport) -> list[HealthIssue]:
        issues: list[HealthIssue] = []
        for (
            snapshot_id,
            _recorded_at,
            _source,
            market,
            asset_id,
            timestamp,
            expected_hash,
            min_order_size,
            tick_size,
            neg_risk,
            last_trade_price,
        ) in self._storage.fetch_book_snapshots():
            bid_levels = []
            ask_levels = []
            for side, _index, price, size in self._storage.fetch_book_levels(snapshot_id):
                level = {"price": price, "size": size}
                if side == "BUY":
                    bid_levels.append(level)
                else:
                    ask_levels.append(level)
            snapshot = BookSnapshot.model_validate(
                {
                    "asset_id": asset_id,
                    "market": market,
                    "timestamp": timestamp,
                    "hash": expected_hash,
                    "bids": bid_levels,
                    "asks": ask_levels,
                    "min_order_size": min_order_size,
                    "tick_size": tick_size,
                    "neg_risk": neg_risk,
                    "last_trade_price": last_trade_price,
                }
            )
            observed_hash = generate_orderbook_hash(snapshot)
            if observed_hash != expected_hash:
                report.snapshot_hash_failures += 1
                issues.append(
                    HealthIssue(
                        issue_type="snapshot_hash_mismatch",
                        market=market,
                        asset_id=asset_id,
                        message="Stored snapshot hash does not round-trip.",
                        observed_hash=observed_hash,
                        expected_hash=expected_hash,
                        timestamp=timestamp,
                    )
                )
        return issues

    def _verify_stream(self, report: VerificationReport) -> list[HealthIssue]:
        issues: list[HealthIssue] = []
        books: dict[str, BookState] = {}
        for _, _, _, event_type, market, asset_id, payload_json in self._storage.fetch_raw_messages():
            payload = json.loads(payload_json)
            if event_type == "book":
                book_event = BookSnapshot.model_validate(payload)
                books[book_event.asset_id] = BookState.from_snapshot(book_event)
                continue
            if event_type == "price_change":
                price_change_event = PriceChangeEvent.model_validate(payload)
                for change in price_change_event.price_changes:
                    book = books.get(change.asset_id)
                    if book is None:
                        report.unknown_books += 1
                        issues.append(
                            HealthIssue(
                                issue_type="missing_book_for_price_change",
                                market=market,
                                asset_id=change.asset_id,
                                message="Cannot verify price_change without a prior book snapshot.",
                                expected_hash=change.hash,
                                timestamp=price_change_event.timestamp,
                            )
                        )
                        continue
                    book.apply_price_change(change, price_change_event.timestamp)
                    validation = book.validate_hash(change.hash)
                    if not validation.is_valid:
                        report.stream_hash_failures += 1
                        issues.append(
                            HealthIssue(
                                issue_type="price_change_hash_mismatch",
                                market=market,
                                asset_id=change.asset_id,
                                message="Stream replay hash mismatch.",
                                observed_hash=validation.observed_hash,
                                expected_hash=change.hash,
                                timestamp=price_change_event.timestamp,
                            )
                        )
                continue
            if event_type == "best_bid_ask":
                best_bid_ask_event = BestBidAskEvent.model_validate(payload)
                book = books.get(best_bid_ask_event.asset_id)
                if book is not None and (
                    book.best_bid() != best_bid_ask_event.best_bid
                    or book.best_ask() != best_bid_ask_event.best_ask
                ):
                    report.best_bid_ask_failures += 1
                    issues.append(
                        HealthIssue(
                            issue_type="best_bid_ask_mismatch",
                            market=best_bid_ask_event.market,
                            asset_id=best_bid_ask_event.asset_id,
                            message="Stream replay best bid/ask mismatch.",
                            timestamp=best_bid_ask_event.timestamp,
                        )
                    )
                continue
            if event_type == "last_trade_price":
                last_trade_event = LastTradePriceEvent.model_validate(payload)
                if last_trade_event.asset_id in books:
                    books[last_trade_event.asset_id].set_last_trade_price(
                        last_trade_event.price, last_trade_event.timestamp
                    )
                continue
            if event_type == "tick_size_change":
                tick_size_event = TickSizeChangeEvent.model_validate(payload)
                if tick_size_event.asset_id in books:
                    books[tick_size_event.asset_id].set_tick_size(
                        tick_size_event.new_tick_size, tick_size_event.timestamp
                    )
                continue
            if event_type in {"new_market", "market_resolved"}:
                continue
        return issues
