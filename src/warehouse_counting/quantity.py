"""Explicit, honest quantity rules for visible cartons and pallets."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CountSummary:
    loose_cartons: int
    pallets: int
    pallet_cartons: int | None
    total_cartons: int | None
    complete: bool


def summarize_counts(
    *, loose_cartons: int, pallets: int, cartons_per_pallet: int | None = None
) -> CountSummary:
    if loose_cartons < 0 or pallets < 0:
        raise ValueError("counts cannot be negative")
    if cartons_per_pallet is not None and cartons_per_pallet <= 0:
        raise ValueError("cartons_per_pallet must be positive")
    pallet_cartons = (
        None if cartons_per_pallet is None else pallets * cartons_per_pallet
    )
    total_cartons = (
        None if pallet_cartons is None else loose_cartons + pallet_cartons
    )
    return CountSummary(
        loose_cartons=loose_cartons,
        pallets=pallets,
        pallet_cartons=pallet_cartons,
        total_cartons=total_cartons,
        complete=total_cartons is not None,
    )
