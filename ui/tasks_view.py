from __future__ import annotations

from datetime import date
from typing import Callable

from nicegui import ui

from services.maintenance_service import MaintenanceService
from services.validation_service import ValidationError
from ui.task_form import TaskFormDialog


class TasksView:
    """UI component for listing and managing maintenance tasks."""

    def __init__(
        self,
        service: MaintenanceService,
        on_data_changed: Callable[[], None] | None = None,
    ) -> None:
        self.service = service
        self.on_data_changed = on_data_changed
        self.task_form = TaskFormDialog(service, self._handle_data_changed)

        columns = [
            {"name": "name", "label": "Task", "field": "name", "align": "left"},
            {
                "name": "category",
                "label": "Category",
                "field": "category",
                "align": "left",
            },
            {
                "name": "frequency_days",
                "label": "Frequency",
                "field": "frequency_days",
                "align": "left",
            },
            {
                "name": "last_completed",
                "label": "Last Completed",
                "field": "last_completed",
                "align": "left",
            },
            {
                "name": "next_due",
                "label": "Next Due",
                "field": "next_due",
                "align": "left",
            },
            {"name": "status", "label": "Status", "field": "status", "align": "left"},
        ]

        with ui.column().classes("w-full gap-3"):
            ui.label("Maintenance Tasks").classes("text-h5")
            with ui.row().classes("items-center gap-2"):
                ui.button("Add Task", on_click=lambda: self.task_form.open()).props(
                    "color=primary"
                )
                ui.button("Edit", on_click=self._edit_selected_task)
                ui.button("Mark Complete", on_click=self._open_mark_complete_dialog)
                ui.button("Delete", on_click=self._open_delete_dialog).props("color=negative")

            self.table = ui.table(
                columns=columns,
                rows=[],
                row_key="task_id",
                selection="single",
                pagination=10,
            ).classes("w-full")

        self.refresh()

    def refresh(self) -> None:
        tasks = self.service.get_active_tasks()
        rows = []

        for task in tasks:
            rows.append(
                {
                    "task_id": task.task_id,
                    "name": task.name,
                    "category": task.category or "",
                    "frequency_days": task.frequency_days,
                    "last_completed": self._format_date(task.last_completed),
                    "next_due": self._format_date(task.next_due),
                    "status": self.service.get_task_status(task),
                }
            )

        self.table.rows = rows
        self.table.selected = []
        self.table.update()

    def _selected_row(self) -> dict | None:
        if not self.table.selected:
            ui.notify("Select a maintenance task first.", type="warning")
            return None
        return self.table.selected[0]

    def _edit_selected_task(self) -> None:
        selected_row = self._selected_row()
        if selected_row is None:
            return

        try:
            task = self.service.get_task(selected_row["task_id"])
            self.task_form.open(task)
        except ValidationError as exc:
            ui.notify(str(exc), type="negative")
            self.refresh()

    def _open_mark_complete_dialog(self) -> None:
        selected_row = self._selected_row()
        if selected_row is None:
            return

        dialog = ui.dialog()
        with dialog, ui.card().classes("w-[480px] gap-3"):
            ui.label(f"Mark Complete: {selected_row['name']}").classes("text-h6")

            completed_input = ui.input(
                "Completed Date (YYYY-MM-DD)",
                value=date.today().isoformat(),
                placeholder="YYYY-MM-DD",
            )
            completed_input.classes("w-full")

            notes_input = ui.textarea("Notes")
            notes_input.props("maxlength=1000 autogrow")
            notes_input.classes("w-full")

            with ui.row().classes("justify-end w-full"):
                ui.button("Cancel", on_click=dialog.close).props("flat")
                ui.button(
                    "Save",
                    on_click=lambda: self._mark_complete(
                        selected_row["task_id"],
                        completed_input.value,
                        notes_input.value,
                        dialog,
                    ),
                ).props("color=primary")

        dialog.open()

    def _mark_complete(
        self,
        task_id: int,
        completed_date: str | date | None,
        notes: str | None,
        dialog: ui.dialog,
    ) -> None:
        try:
            self.service.mark_task_complete(task_id, completed_date, notes)
            ui.notify("Maintenance completion saved.", type="positive")
            dialog.close()
            self._handle_data_changed()
        except ValidationError as exc:
            ui.notify(str(exc), type="negative")
        except RuntimeError as exc:
            ui.notify(f"Unable to mark task complete: {exc}", type="negative")

    def _open_delete_dialog(self) -> None:
        selected_row = self._selected_row()
        if selected_row is None:
            return

        dialog = ui.dialog()
        with dialog, ui.card().classes("w-[420px] gap-3"):
            ui.label("Deactivate Maintenance Task").classes("text-h6")
            ui.label(
                f"Are you sure you want to deactivate '{selected_row['name']}'?"
            ).classes("text-body2")

            with ui.row().classes("justify-end w-full"):
                ui.button("Cancel", on_click=dialog.close).props("flat")
                ui.button(
                    "Deactivate",
                    on_click=lambda: self._delete_selected_task(
                        selected_row["task_id"],
                        dialog,
                    ),
                ).props("color=negative")

        dialog.open()

    def _delete_selected_task(self, task_id: int, dialog: ui.dialog) -> None:
        try:
            self.service.delete_task(task_id)
            ui.notify("Maintenance task deactivated.", type="positive")
            dialog.close()
            self._handle_data_changed()
        except ValidationError as exc:
            ui.notify(str(exc), type="negative")
        except RuntimeError as exc:
            ui.notify(f"Unable to deactivate task: {exc}", type="negative")

    def _handle_data_changed(self) -> None:
        self.refresh()
        if self.on_data_changed is not None:
            self.on_data_changed()

    @staticmethod
    def _format_date(value: date | None) -> str:
        return value.isoformat() if value else ""

