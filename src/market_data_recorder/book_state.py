from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .hashing import generate_orderbook_hash
from .models import BookSnapshot, PriceChangeEntry, PriceLevel


@dataclass(slots=True)
class BookValidation:
    is_valid: bool
    observed_hash: str | None = None


class BookState:
    def __init__(self, snapshot: BookSnapshot):
        self.market = snapshot.market
        self.asset_id = snapshot.asset_id
        self.timestamp = snapshot.timestamp
        self.min_order_size = snapshot.min_order_size
        self.tick_size = snapshot.tick_size
        self.neg_risk = snapshot.neg_risk
        self.last_trade_price = snapshot.last_trade_price
        self._bids: dict[str, str] = {level.price: level.size for level in snapshot.bids}
        self._asks: dict[str, str] = {level.price: level.size for level in snapshot.asks}

    @classmethod
    def from_snapshot(cls, snapshot: BookSnapshot) -> "BookState":
        return cls(snapshot)

    def replace(self, snapshot: BookSnapshot) -> None:
        self.market = snapshot.market
        self.asset_id = snapshot.asset_id
        self.timestamp = snapshot.timestamp
        self.min_order_size = snapshot.min_order_size
        self.tick_size = snapshot.tick_size
        self.neg_risk = snapshot.neg_risk
        self.last_trade_price = snapshot.last_trade_price
        self._bids = {level.price: level.size for level in snapshot.bids}
        self._asks = {level.price: level.size for level in snapshot.asks}

    def apply_price_change(self, change: PriceChangeEntry, timestamp: str) -> None:
        book_side = self._bids if change.side == "BUY" else self._asks
        if Decimal(change.size) == Decimal("0"):
            book_side.pop(change.price, None)
        else:
            book_side[change.price] = change.size
        self.timestamp = timestamp

    def set_tick_size(self, new_tick_size: str, timestamp: str) -> None:
        self.tick_size = new_tick_size
        self.timestamp = timestamp

    def set_last_trade_price(self, price: str, timestamp: str) -> None:
        self.last_trade_price = price
        self.timestamp = timestamp

    def best_bid(self) -> str | None:
        if not self._bids:
            return None
        return max(self._bids, key=Decimal)

    def best_ask(self) -> str | None:
        if not self._asks:
            return None
        return min(self._asks, key=Decimal)

    def as_snapshot(self) -> BookSnapshot:
        snapshot = BookSnapshot(
            asset_id=self.asset_id,
            market=self.market,
            bids=self._sorted_levels(self._bids, reverse=True),
            asks=self._sorted_levels(self._asks, reverse=False),
            timestamp=self.timestamp,
            hash="",
            min_order_size=self.min_order_size,
            tick_size=self.tick_size,
            neg_risk=self.neg_risk,
            last_trade_price=self.last_trade_price,
        )
        snapshot.hash = generate_orderbook_hash(snapshot)
        return snapshot

    def validate_hash(self, expected_hash: str | None) -> BookValidation:
        if expected_hash is None:
            return BookValidation(is_valid=True, observed_hash=None)
        observed_hash = self.as_snapshot().hash
        return BookValidation(
            is_valid=observed_hash == expected_hash,
            observed_hash=observed_hash,
        )

    @staticmethod
    def _sorted_levels(levels: dict[str, str], reverse: bool) -> list[PriceLevel]:
        return [
            PriceLevel(price=price, size=levels[price])
            for price in sorted(levels, key=Decimal, reverse=reverse)
        ]
