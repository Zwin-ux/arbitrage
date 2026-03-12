from __future__ import annotations

import hashlib
import json

from .models import BookSnapshot


def generate_orderbook_hash(snapshot: BookSnapshot) -> str:
    """Matches the field order used by the official py-clob-client."""
    payload = {
        "market": snapshot.market,
        "asset_id": snapshot.asset_id,
        "timestamp": snapshot.timestamp,
        "hash": "",
        "bids": [level.model_dump() for level in snapshot.bids],
        "asks": [level.model_dump() for level in snapshot.asks],
        "min_order_size": snapshot.min_order_size,
        "tick_size": snapshot.tick_size,
        "neg_risk": snapshot.neg_risk,
        "last_trade_price": snapshot.last_trade_price,
    }
    serialized = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha1(serialized.encode("utf-8")).hexdigest()
