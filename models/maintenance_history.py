from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class MaintenanceHistory:
    """Represents a row in the maintenance_history table."""

    history_id: int | None
    task_id: int
    completed_date: date
    notes: str | None

