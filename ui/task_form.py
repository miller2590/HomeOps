from __future__ import annotations

from datetime import date
from typing import Callable

from nicegui import ui

from models.maintenance_task import MaintenanceTask
from services.maintenance_service import MaintenanceService
from services.validation_service import ValidationError


class TaskFormDialog:
    """Reusable add/edit form for maintenance tasks."""

    def __init__(self, service: MaintenanceService, on_saved: Callable[[], None]) -> None:
        self.service = service
        self.on_saved = on_saved

    def open(self, task: MaintenanceTask | None = None) -> None:
        is_edit = task is not None
        task_name = task.name if task else ""
        category = task.category if task and task.category else ""
        frequency_days = task.frequency_days if task else 90
        last_completed = self._format_date(task.last_completed) if task else ""
        notes = task.notes if task and task.notes else ""

        dialog = ui.dialog()
        with dialog, ui.card().classes("w-[540px] gap-3"):
            ui.label("Edit Maintenance Task" if is_edit else "Add Maintenance Task").classes(
                "text-h6"
            )

            name_input = ui.input("Task Name", value=task_name)
            name_input.props("maxlength=100")
            name_input.classes("w-full")

            category_input = ui.input("Category", value=category)
            category_input.props("maxlength=50")
            category_input.classes("w-full")

            frequency_input = ui.number(
                "Frequency in Days",
                value=frequency_days,
                min=1,
                step=1,
                precision=0,
            )
            frequency_input.classes("w-full")

            last_completed_input = ui.input(
                "Last Completed (YYYY-MM-DD)",
                value=last_completed,
                placeholder="YYYY-MM-DD",
            )
            last_completed_input.classes("w-full")

            notes_input = ui.textarea("Notes", value=notes)
            notes_input.props("maxlength=1000 autogrow")
            notes_input.classes("w-full")

            with ui.row().classes("justify-end w-full"):
                ui.button("Cancel", on_click=dialog.close).props("flat")
                ui.button(
                    "Save",
                    on_click=lambda: self._save(
                        dialog,
                        task,
                        name_input.value or "",
                        category_input.value,
                        frequency_input.value,
                        last_completed_input.value,
                        notes_input.value,
                    ),
                ).props("color=primary")

        dialog.open()

    def _save(
        self,
        dialog: ui.dialog,
        task: MaintenanceTask | None,
        name: str,
        category: str | None,
        frequency_days: int | float | str,
        last_completed: str | date | None,
        notes: str | None,
    ) -> None:
        try:
            if task is None:
                self.service.create_task(
                    name=name,
                    category=category,
                    frequency_days=frequency_days,
                    last_completed=last_completed,
                    notes=notes,
                )
                ui.notify("Maintenance task added.", type="positive")
            else:
                self.service.update_task(
                    task_id=task.task_id or 0,
                    name=name,
                    category=category,
                    frequency_days=frequency_days,
                    last_completed=last_completed,
                    notes=notes,
                )
                ui.notify("Maintenance task updated.", type="positive")

            dialog.close()
            self.on_saved()
        except ValidationError as exc:
            ui.notify(str(exc), type="negative")
        except RuntimeError as exc:
            ui.notify(f"Unable to save task: {exc}", type="negative")

    @staticmethod
    def _format_date(value: date | None) -> str:
        return value.isoformat() if value else ""

