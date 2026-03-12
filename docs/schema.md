# Schema

## `events`

Gamma event metadata captured during discovery.

## `markets`

Gamma market metadata captured during discovery.

## `tokens`

Outcome token mapping per market.

## `raw_messages`

Append-only raw payload log for both REST bootstraps and websocket messages.

Columns:

- `sequence`: insertion order
- `recorded_at`: recorder timestamp
- `source`: `bootstrap`, `reconnect`, `resync`, `websocket`, and similar
- `event_type`: normalized event kind
- `market`
- `asset_id`
- `payload_json`

## `book_snapshots`

One row per full orderbook snapshot.

## `book_levels`

Price levels for each snapshot, normalized by side and level index.

## `price_changes`

Incremental price-level changes from the websocket `price_change` event.

## `last_trade_prices`

Trade prints from the websocket `last_trade_price` event.

## `best_bid_ask`

Top-of-book updates from the websocket `best_bid_ask` event.

## `tick_size_changes`

Tick-size changes from the websocket `tick_size_change` event.

## `market_lifecycle`

`new_market` and `market_resolved` lifecycle messages.

## `health_events`

Recorder-generated incidents:

- snapshot hash mismatches
- price-change hash mismatches
- best-bid/ask mismatches
- missing-book-on-change
- stale-book forced resyncs
