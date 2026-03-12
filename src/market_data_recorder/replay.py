from __future__ import annotations

import json
from pathlib import Path

from .book_state import BookState
from .models import (
    BestBidAskEvent,
    BookSnapshot,
    LastTradePriceEvent,
    PriceChangeEvent,
    ReplaySummary,
    TickSizeChangeEvent,
)
from .storage import DuckDBStorage


class ReplayEngine:
    def __init__(self, storage: DuckDBStorage):
        self._storage = storage

    def replay_summary(self, *, limit: int | None = None) -> ReplaySummary:
        summary = ReplaySummary()
        books: dict[str, BookState] = {}
        for _, _, _, event_type, _, _, payload_json in self._storage.fetch_raw_messages(limit=limit):
            payload = json.loads(payload_json)
            summary.raw_messages += 1
            if event_type == "book":
                book_event = BookSnapshot.model_validate(payload)
                books[book_event.asset_id] = BookState.from_snapshot(book_event)
                summary.book_messages += 1
            elif event_type == "price_change":
                price_change_event = PriceChangeEvent.model_validate(payload)
                for change in price_change_event.price_changes:
                    if change.asset_id in books:
                        books[change.asset_id].apply_price_change(
                            change, price_change_event.timestamp
                        )
                summary.price_change_messages += 1
            elif event_type == "last_trade_price":
                last_trade_event = LastTradePriceEvent.model_validate(payload)
                if last_trade_event.asset_id in books:
                    books[last_trade_event.asset_id].set_last_trade_price(
                        last_trade_event.price, last_trade_event.timestamp
                    )
                summary.last_trade_messages += 1
            elif event_type == "best_bid_ask":
                BestBidAskEvent.model_validate(payload)
                summary.best_bid_ask_messages += 1
            elif event_type == "tick_size_change":
                tick_size_event = TickSizeChangeEvent.model_validate(payload)
                if tick_size_event.asset_id in books:
                    books[tick_size_event.asset_id].set_tick_size(
                        tick_size_event.new_tick_size, tick_size_event.timestamp
                    )
                summary.tick_size_messages += 1
            elif event_type in {"new_market", "market_resolved"}:
                summary.lifecycle_messages += 1
        summary.final_books = len(books)
        return summary

    def export_jsonl(self, output_path: Path, *, limit: int | None = None) -> int:
        count = 0
        with output_path.open("w", encoding="utf-8") as handle:
            for _, recorded_at, source, event_type, market, asset_id, payload_json in self._storage.fetch_raw_messages(
                limit=limit
            ):
                handle.write(
                    json.dumps(
                        {
                            "recorded_at": recorded_at.isoformat(),
                            "source": source,
                            "event_type": event_type,
                            "market": market,
                            "asset_id": asset_id,
                            "payload": json.loads(payload_json),
                        }
                    )
                )
                handle.write("\n")
                count += 1
        return count
