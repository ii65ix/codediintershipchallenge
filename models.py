"""Application data models for the habit tracker."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class HabitEntry:
    """Represents a single habit completion record."""

    id: Optional[int]
    name: str
    date: date
    status: int
