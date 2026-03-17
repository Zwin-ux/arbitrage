from __future__ import annotations

import json
import uuid
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

import duckdb

from .models import (
    BestBidAskEvent,
    BookSnapshot,
    DiscoveredMarket,
    HealthIssue,
    LastTradePriceEvent,
    MarketLifecycleEvent,
    PriceChangeEvent,
    TickSizeChangeEvent,
)


class DuckDBStorage:
    def __init__(self, path: Path, *, read_only: bool = False):
        self._path = path
        self._read_only = read_only
        if not read_only and str(path) != ":memory:":
            path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = duckdb.connect(str(path), read_only=read_only)
        if read_only:
            self._raw_sequence = 0
        else:
            self._initialize_schema()
            self._raw_sequence = self._read_next_sequence()

    def close(self) -> None:
        self._connection.close()

    def _read_next_sequence(self) -> int:
        current = self._connection.execute(
            "SELECT COALESCE(MAX(sequence), 0) + 1 FROM raw_messages"
        ).fetchone()
        assert current is not None
        return int(current[0])

    def _initialize_schema(self) -> None:
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
              event_id TEXT,
              ticker TEXT,
              slug TEXT,
              title TEXT,
              active BOOLEAN,
              closed BOOLEAN,
              recorded_at TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS markets (
              market_id TEXT,
              condition_id TEXT,
              event_id TEXT,
              question TEXT,
              slug TEXT,
              active BOOLEAN,
              closed BOOLEAN,
              accepting_orders BOOLEAN,
              enable_order_book BOOLEAN,
              neg_risk BOOLEAN,
              fees_enabled BOOLEAN,
              order_min_size DOUBLE,
              order_price_min_tick_size DOUBLE,
              recorded_at TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS tokens (
              asset_id TEXT,
              market_id TEXT,
              condition_id TEXT,
              outcome_index INTEGER,
              outcome TEXT,
              recorded_at TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS raw_messages (
              sequence BIGINT,
              message_id TEXT,
              recorded_at TIMESTAMP,
              source TEXT,
              event_type TEXT,
              market TEXT,
              asset_id TEXT,
              payload_json TEXT
            );

            CREATE TABLE IF NOT EXISTS book_snapshots (
              snapshot_id TEXT,
              recorded_at TIMESTAMP,
              source TEXT,
              market TEXT,
              asset_id TEXT,
              timestamp TEXT,
              hash TEXT,
              min_order_size TEXT,
              tick_size TEXT,
              neg_risk BOOLEAN,
              last_trade_price TEXT
            );

            CREATE TABLE IF NOT EXISTS book_levels (
              snapshot_id TEXT,
              side TEXT,
              level_index INTEGER,
              price TEXT,
              size TEXT
            );

            CREATE TABLE IF NOT EXISTS price_changes (
              recorded_at TIMESTAMP,
              market TEXT,
              asset_id TEXT,
              event_timestamp TEXT,
              side TEXT,
              price TEXT,
              size TEXT,
              hash TEXT,
              best_bid TEXT,
              best_ask TEXT
            );

            CREATE TABLE IF NOT EXISTS last_trade_prices (
              recorded_at TIMESTAMP,
              market TEXT,
              asset_id TEXT,
              event_timestamp TEXT,
              price TEXT,
              side TEXT,
              size TEXT,
              fee_rate_bps TEXT
            );

            CREATE TABLE IF NOT EXISTS best_bid_ask (
              recorded_at TIMESTAMP,
              market TEXT,
              asset_id TEXT,
              event_timestamp TEXT,
              best_bid TEXT,
              best_ask TEXT,
              spread TEXT
            );

            CREATE TABLE IF NOT EXISTS tick_size_changes (
              recorded_at TIMESTAMP,
              market TEXT,
              asset_id TEXT,
              event_timestamp TEXT,
              old_tick_size TEXT,
              new_tick_size TEXT
            );

            CREATE TABLE IF NOT EXISTS market_lifecycle (
              recorded_at TIMESTAMP,
              event_type TEXT,
              market TEXT,
              market_id TEXT,
              question TEXT,
              slug TEXT,
              description TEXT,
              assets_ids_json TEXT,
              outcomes_json TEXT,
              winning_asset_id TEXT,
              winning_outcome TEXT,
              event_message_json TEXT,
              event_timestamp TEXT
            );

            CREATE TABLE IF NOT EXISTS health_events (
              recorded_at TIMESTAMP,
              issue_type TEXT,
              market TEXT,
              asset_id TEXT,
              message TEXT,
              observed_hash TEXT,
              expected_hash TEXT,
              event_timestamp TEXT
            );

            CREATE TABLE IF NOT EXISTS benchmark_instruments (
              symbol TEXT,
              name TEXT,
              instrument_type TEXT,
              exchange TEXT,
              currency TEXT,
              source_provider TEXT,
              updated_at TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS benchmark_bars (
              symbol TEXT,
              instrument_type TEXT,
              interval TEXT,
              recorded_at TIMESTAMP,
              open DOUBLE,
              high DOUBLE,
              low DOUBLE,
              close DOUBLE,
              volume DOUBLE,
              source_provider TEXT
            );

            CREATE TABLE IF NOT EXISTS benchmark_quotes (
              symbol TEXT,
              instrument_type TEXT,
              quoted_at TIMESTAMP,
              price DOUBLE,
              bid DOUBLE,
              ask DOUBLE,
              source_provider TEXT
            );

            CREATE TABLE IF NOT EXISTS market_benchmark_links (
              link_id TEXT,
              profile_id TEXT,
              market_slug TEXT,
              market_id TEXT,
              symbol TEXT,
              instrument_type TEXT,
              interval_preference TEXT,
              mapping_confidence INTEGER,
              notes TEXT,
              created_at TIMESTAMP,
              updated_at TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS benchmark_audits (
              audit_id TEXT,
              profile_id TEXT,
              market_slug TEXT,
              run_id TEXT,
              session_id TEXT,
              symbol TEXT,
              instrument_type TEXT,
              interval_used TEXT,
              verdict TEXT,
              coverage_state TEXT,
              underlying_move_bps INTEGER,
              session_edge_bps INTEGER,
              edge_vs_benchmark_bps INTEGER,
              stale BOOLEAN,
              alignment_seconds INTEGER,
              note TEXT,
              observed_at TIMESTAMP
            );
            """
        )

    def store_discovery_snapshot(
        self,
        items: Sequence[DiscoveredMarket],
        *,
        recorded_at: datetime | None = None,
    ) -> None:
        timestamp = recorded_at or datetime.now(timezone.utc)
        event_rows_by_id: dict[str, list[Any]] = {}
        market_rows: list[list[Any]] = []
        token_rows: list[list[Any]] = []
        for item in items:
            event = item.event
            market = item.market
            event_rows_by_id[event.event_id] = [
                event.event_id,
                event.ticker,
                event.slug,
                event.title,
                event.active,
                event.closed,
                timestamp,
            ]
            market_rows.append(
                [
                    market.market_id,
                    market.condition_id,
                    event.event_id,
                    market.question,
                    market.slug,
                    market.active,
                    market.closed,
                    market.accepting_orders,
                    market.enable_order_book,
                    market.neg_risk,
                    market.fees_enabled,
                    market.order_min_size,
                    market.order_price_min_tick_size,
                    timestamp,
                ]
            )
            for index, asset_id in enumerate(market.clob_token_ids):
                outcome = market.outcomes[index] if index < len(market.outcomes) else None
                token_rows.append(
                    [
                        asset_id,
                        market.market_id,
                        market.condition_id,
                        index,
                        outcome,
                        timestamp,
                    ]
                )
        self._connection.execute("DELETE FROM events")
        self._connection.execute("DELETE FROM markets")
        self._connection.execute("DELETE FROM tokens")
        self._connection.executemany(
            "INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?)",
            list(event_rows_by_id.values()),
        )
        self._connection.executemany(
            "INSERT INTO markets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            market_rows,
        )
        self._connection.executemany(
            "INSERT INTO tokens VALUES (?, ?, ?, ?, ?, ?)",
            token_rows,
        )

    def store_raw_message(
        self,
        *,
        source: str,
        event_type: str,
        market: str | None,
        asset_id: str | None,
        payload: dict[str, Any],
        recorded_at: datetime | None = None,
    ) -> None:
        timestamp = recorded_at or datetime.now(timezone.utc)
        self._connection.execute(
            """
            INSERT INTO raw_messages VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                self._raw_sequence,
                str(uuid.uuid4()),
                timestamp,
                source,
                event_type,
                market,
                asset_id,
                json.dumps(payload, separators=(",", ":")),
            ],
        )
        self._raw_sequence += 1

    def store_book_snapshot(
        self,
        snapshot: BookSnapshot,
        *,
        source: str,
        recorded_at: datetime | None = None,
    ) -> None:
        timestamp = recorded_at or datetime.now(timezone.utc)
        snapshot_id = str(uuid.uuid4())
        self._connection.execute(
            """
            INSERT INTO book_snapshots VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                snapshot_id,
                timestamp,
                source,
                snapshot.market,
                snapshot.asset_id,
                snapshot.timestamp,
                snapshot.hash,
                snapshot.min_order_size,
                snapshot.tick_size,
                snapshot.neg_risk,
                snapshot.last_trade_price,
            ],
        )
        for side, levels in (("BUY", snapshot.bids), ("SELL", snapshot.asks)):
            for index, level in enumerate(levels):
                self._connection.execute(
                    """
                    INSERT INTO book_levels VALUES (?, ?, ?, ?, ?)
                    """,
                    [
                        snapshot_id,
                        side,
                        index,
                        level.price,
                        level.size,
                    ],
                )

    def store_price_change(
        self,
        event: PriceChangeEvent,
        *,
        recorded_at: datetime | None = None,
    ) -> None:
        timestamp = recorded_at or datetime.now(timezone.utc)
        for change in event.price_changes:
            self._connection.execute(
                """
                INSERT INTO price_changes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    timestamp,
                    event.market,
                    change.asset_id,
                    event.timestamp,
                    change.side,
                    change.price,
                    change.size,
                    change.hash,
                    change.best_bid,
                    change.best_ask,
                ],
            )

    def store_last_trade_price(
        self,
        event: LastTradePriceEvent,
        *,
        recorded_at: datetime | None = None,
    ) -> None:
        timestamp = recorded_at or datetime.now(timezone.utc)
        self._connection.execute(
            """
            INSERT INTO last_trade_prices VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                timestamp,
                event.market,
                event.asset_id,
                event.timestamp,
                event.price,
                event.side,
                event.size,
                event.fee_rate_bps,
            ],
        )

    def store_best_bid_ask(
        self,
        event: BestBidAskEvent,
        *,
        recorded_at: datetime | None = None,
    ) -> None:
        timestamp = recorded_at or datetime.now(timezone.utc)
        self._connection.execute(
            """
            INSERT INTO best_bid_ask VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                timestamp,
                event.market,
                event.asset_id,
                event.timestamp,
                event.best_bid,
                event.best_ask,
                event.spread,
            ],
        )

    def store_tick_size_change(
        self,
        event: TickSizeChangeEvent,
        *,
        recorded_at: datetime | None = None,
    ) -> None:
        timestamp = recorded_at or datetime.now(timezone.utc)
        self._connection.execute(
            """
            INSERT INTO tick_size_changes VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                timestamp,
                event.market,
                event.asset_id,
                event.timestamp,
                event.old_tick_size,
                event.new_tick_size,
            ],
        )

    def store_market_lifecycle(
        self,
        event: MarketLifecycleEvent,
        *,
        recorded_at: datetime | None = None,
    ) -> None:
        timestamp = recorded_at or datetime.now(timezone.utc)
        self._connection.execute(
            """
            INSERT INTO market_lifecycle VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                timestamp,
                event.event_type,
                event.market,
                event.id,
                event.question,
                event.slug,
                event.description,
                json.dumps(event.assets_ids),
                json.dumps(event.outcomes),
                event.winning_asset_id,
                event.winning_outcome,
                json.dumps(event.event_message or {}),
                event.timestamp,
            ],
        )

    def store_health_issue(
        self,
        issue: HealthIssue,
        *,
        recorded_at: datetime | None = None,
    ) -> None:
        timestamp = recorded_at or datetime.now(timezone.utc)
        self._connection.execute(
            """
            INSERT INTO health_events VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                timestamp,
                issue.issue_type,
                issue.market,
                issue.asset_id,
                issue.message,
                issue.observed_hash,
                issue.expected_hash,
                issue.timestamp,
            ],
        )

    def fetch_raw_messages(self, *, limit: int | None = None) -> list[tuple[Any, ...]]:
        if limit is None:
            return self._connection.execute(
                """
                SELECT sequence, recorded_at, source, event_type, market, asset_id, payload_json
                FROM raw_messages
                ORDER BY sequence
                """
            ).fetchall()
        return self._connection.execute(
            """
            SELECT sequence, recorded_at, source, event_type, market, asset_id, payload_json
            FROM raw_messages
            ORDER BY sequence
            LIMIT ?
            """,
            [limit],
        ).fetchall()

    def fetch_book_snapshots(self) -> list[tuple[Any, ...]]:
        return self._connection.execute(
            """
            SELECT snapshot_id, recorded_at, source, market, asset_id, timestamp, hash, min_order_size,
                   tick_size, neg_risk, last_trade_price
            FROM book_snapshots
            ORDER BY recorded_at
            """
        ).fetchall()

    def fetch_book_levels(self, snapshot_id: str) -> list[tuple[Any, ...]]:
        return self._connection.execute(
            """
            SELECT side, level_index, price, size
            FROM book_levels
            WHERE snapshot_id = ?
            ORDER BY side, level_index
            """,
            [snapshot_id],
        ).fetchall()

    def fetch_latest_best_bid_ask(self) -> list[tuple[Any, ...]]:
        return self._connection.execute(
            """
            WITH ranked AS (
              SELECT
                market,
                asset_id,
                event_timestamp,
                best_bid,
                best_ask,
                ROW_NUMBER() OVER (
                  PARTITION BY market, asset_id
                  ORDER BY recorded_at DESC, event_timestamp DESC
                ) AS row_number
              FROM best_bid_ask
            )
            SELECT
              ranked.market,
              ranked.asset_id,
              tokens.outcome,
              ranked.event_timestamp,
              ranked.best_bid,
              ranked.best_ask
            FROM ranked
            LEFT JOIN tokens
              ON tokens.market_id = ranked.market
             AND tokens.asset_id = ranked.asset_id
            WHERE ranked.row_number = 1
            ORDER BY ranked.market, ranked.asset_id
            """
        ).fetchall()

    def fetch_dashboard_summary(self) -> tuple[int, int, int, datetime | None, tuple[Any, ...] | None]:
        counts = self._connection.execute(
            """
            SELECT
              (SELECT COUNT(*) FROM raw_messages),
              (SELECT COUNT(*) FROM book_snapshots),
              (SELECT COUNT(*) FROM health_events)
            """
        ).fetchone()
        assert counts is not None
        latest_message = self._connection.execute(
            """
            SELECT recorded_at
            FROM raw_messages
            ORDER BY recorded_at DESC
            LIMIT 1
            """
        ).fetchone()
        latest_issue = self._connection.execute(
            """
            SELECT issue_type, message, recorded_at
            FROM health_events
            ORDER BY recorded_at DESC
            LIMIT 1
            """
        ).fetchone()
        latest_recorded_at = cast(datetime | None, latest_message[0] if latest_message else None)
        return (
            int(counts[0]),
            int(counts[1]),
            int(counts[2]),
            latest_recorded_at,
            latest_issue,
        )

    def fetch_latest_market_quotes(self) -> list[tuple[Any, ...]]:
        return self._connection.execute(
            """
            WITH latest_best_bid_ask AS (
              SELECT
                asset_id,
                market,
                recorded_at,
                best_bid,
                best_ask,
                ROW_NUMBER() OVER (PARTITION BY asset_id ORDER BY recorded_at DESC) AS row_num
              FROM best_bid_ask
            )
            SELECT
              token.asset_id,
              token.market_id,
              COALESCE(market.question, token.market_id),
              COALESCE(market.slug, token.market_id),
              COALESCE(token.outcome, 'Outcome'),
              COALESCE(market.neg_risk, FALSE),
              COALESCE(market.fees_enabled, FALSE),
              latest.best_bid,
              latest.best_ask,
              latest.recorded_at
            FROM latest_best_bid_ask AS latest
            INNER JOIN tokens AS token ON token.asset_id = latest.asset_id
            LEFT JOIN markets AS market ON market.market_id = token.market_id
            WHERE latest.row_num = 1
            ORDER BY latest.recorded_at DESC, token.market_id, token.outcome_index
            """
        ).fetchall()
