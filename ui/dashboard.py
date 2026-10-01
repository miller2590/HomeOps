from __future__ import annotations

from datetime import date

from nicegui import ui

from services.maintenance_service import MaintenanceService


class DashboardView:
    """UI component that summarizes maintenance workload and recent activity."""

    def __init__(self, service: MaintenanceService) -> None:
        self.service = service

        task_columns = [
            {"name": "name", "label": "Task", "field": "name", "align": "left"},
            {
                "name": "category",
                "label": "Category",
                "field": "category",
                "align": "left",
            },
            {
                "name": "next_due",
                "label": "Next Due",
                "field": "next_due",
                "align": "left",
            },
        ]

        recent_columns = [
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

        with ui.column().classes("w-full gap-4"):
            ui.label("Dashboard").classes("text-h5")

            with ui.row().classes("w-full gap-4"):
                with ui.card().classes("w-56"):
                    ui.label("Total Active Tasks").classes("text-subtitle2")
                    self.total_active_label = ui.label("0").classes("text-h5")

                with ui.card().classes("w-56"):
                    ui.label("Overdue").classes("text-subtitle2")
                    self.overdue_label = ui.label("0").classes("text-h5")

                with ui.card().classes("w-56"):
                    ui.label("Due Soon (30 Days)").classes("text-subtitle2")
                    self.due_soon_label = ui.label("0").classes("text-h5")

            ui.label("Overdue Tasks").classes("text-h6")
            self.overdue_table = ui.table(
                columns=task_columns,
                rows=[],
                row_key="task_id",
                pagination=5,
            ).classes("w-full")

            ui.label("Tasks Due Soon").classes("text-h6")
            self.due_soon_table = ui.table(
                columns=task_columns,
                rows=[],
                row_key="task_id",
                pagination=5,
            ).classes("w-full")

            ui.label("Recently Completed").classes("text-h6")
            self.recent_history_table = ui.table(
                columns=recent_columns,
                rows=[],
                row_key="history_id",
                pagination=5,
            ).classes("w-full")

        self.refresh()

    def refresh(self) -> None:
        today = date.today()
        tasks = self.service.get_active_tasks()

        overdue_rows = []
        due_soon_rows = []

        for task in tasks:
            row = {
                "task_id": task.task_id,
                "name": task.name,
                "category": task.category or "",
                "next_due": self._format_date(task.next_due),
            }
            status = self.service.get_task_status(task, today)
            if status == "Overdue":
                overdue_rows.append(row)
            elif status == "Due Soon":
                due_soon_rows.append(row)

        recent_history = self.service.get_history(limit=5)
        recent_rows = [
            {
                "history_id": entry["history_id"],
                "task_name": entry["task_name"],
                "completed_date": self._format_date(entry["completed_date"]),
                "notes": entry["notes"] or "",
            }
            for entry in recent_history
        ]

        self.total_active_label.text = str(len(tasks))
        self.overdue_label.text = str(len(overdue_rows))
        self.due_soon_label.text = str(len(due_soon_rows))

        self.total_active_label.update()
        self.overdue_label.update()
        self.due_soon_label.update()

        self.overdue_table.rows = overdue_rows
        self.overdue_table.update()

        self.due_soon_table.rows = due_soon_rows
        self.due_soon_table.update()

        self.recent_history_table.rows = recent_rows
        self.recent_history_table.update()

    @staticmethod
    def _format_date(value: object) -> str:
        if isinstance(value, date):
            return value.isoformat()
        return ""

