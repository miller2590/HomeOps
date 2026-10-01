from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class MaintenanceTask:
    """Represents a row in the maintenance_tasks table."""

    task_id: int | None
    name: str
    category: str | None
    frequency_days: int
    last_completed: date | None
    next_due: date | None
    notes: str | None
    active: int = 1

