# Architecture

```text
detector/tracker (future adapter)
          |
          v
TrackObservation -> CrossingCounter -> CrossingEvent -> EventStore(SQLite)
                                      |
                                      v
                               CountSummary/ledger
```

`TrackObservation` is the only boundary a detector or tracker must implement.
The counter applies line geometry, confidence and class filters, direction, and
one-event-per-track locking. `EventStore` persists immutable events and exposes
filtered totals. `quantity.py` applies explicit pallet-capacity rules; it never
infers hidden carton quantities.
