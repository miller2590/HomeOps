from __future__ import annotations

from datetime import date

from nicegui import ui

from services.maintenance_service import MaintenanceService


class HistoryView:
    """UI component that lists maintenance completion history."""

    def __init__(self, service: MaintenanceService) -> None:
        self.service = service

        columns = [
            {
                "name": "task_name",
                "label": "Maintenance Item",
                "field": "task_name",
                "align": "left",
            },
            {
                "name": "completed_date",
                "label": "Completed Date",
                "field": "completed_date",
                "align": "left",
            },
            {"name": "notes", "label": "Notes", "field": "notes", "align": "left"},
        ]

        with ui.column().classes("w-full gap-3"):
            ui.label("Maintenance History").classes("text-h5")
            self.table = ui.table(
                columns=columns,
                rows=[],
                row_key="history_id",
                pagination=10,
            ).classes("w-full")

        self.refresh()

    def refresh(self) -> None:
        history = self.service.get_history()
        rows = [
            {
                "history_id": entry["history_id"],
                "task_name": entry["task_name"],
                "completed_date": self._format_date(entry["completed_date"]),
                "notes": entry["notes"] or "",
            }
            for entry in history
        ]

        self.table.rows = rows
        self.table.update()

    @staticmethod
    def _format_date(value: object) -> str:
        if isinstance(value, date):
            return value.isoformat()
        return ""

