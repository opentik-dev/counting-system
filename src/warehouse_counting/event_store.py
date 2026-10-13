"""SQLite persistence for immutable crossing events."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .domain import CrossingEvent


class EventStore:
    def __init__(self, database: str | Path) -> None:
        self.connection = sqlite3.connect(database)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS crossing_events (
                event_id TEXT PRIMARY KEY,
                camera_id TEXT NOT NULL,
                track_id INTEGER NOT NULL,
                object_type TEXT NOT NULL,
                direction TEXT NOT NULL CHECK (direction IN ('IN', 'OUT')),
                timestamp TEXT NOT NULL,
                confidence REAL NOT NULL,
                evidence_ref TEXT
            )
            """
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def save(self, event: CrossingEvent) -> None:
        self.connection.execute(
            """
            INSERT INTO crossing_events
            (event_id, camera_id, track_id, object_type, direction, timestamp,
             confidence, evidence_ref)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(event.event_id),
                event.camera_id,
                event.track_id,
                event.object_type,
                event.direction,
                event.timestamp.isoformat(),
                event.confidence,
                event.evidence_ref,
            ),
        )
        self.connection.commit()

    def save_many(self, events: Iterable[CrossingEvent]) -> None:
        for event in events:
            self.save(event)

    def get(self, event_id: str) -> sqlite3.Row | None:
        return self.connection.execute(
            "SELECT * FROM crossing_events WHERE event_id = ?", (event_id,)
        ).fetchone()

    def totals(
        self, *, start: datetime | None = None, end: datetime | None = None
    ) -> dict[tuple[str, str], int]:
        clauses: list[str] = []
        values: list[str] = []
        if start is not None:
            clauses.append("timestamp >= ?")
            values.append(start.isoformat())
        if end is not None:
            clauses.append("timestamp < ?")
            values.append(end.isoformat())
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        rows = self.connection.execute(
            """
            SELECT object_type, direction, COUNT(*) AS count
            FROM crossing_events
            """
            + where
            + " GROUP BY object_type, direction",
            values,
        ).fetchall()
        return {(row["object_type"], row["direction"]): row["count"] for row in rows}
