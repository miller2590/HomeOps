from __future__ import annotations

from datetime import date, timedelta

from database.database_manager import DatabaseManager
from models.maintenance_task import MaintenanceTask
from services.validation_service import ValidationError, ValidationService


class MaintenanceService:
    """Business logic for managing maintenance tasks and history."""

    DUE_SOON_DAYS = 30

    def __init__(self, database_manager: DatabaseManager) -> None:
        self.database_manager = database_manager

    def calculate_next_due_date(self, completed_date: date, frequency_days: int) -> date:
        """Calculate the next due date from completion date and frequency."""
        return completed_date + timedelta(days=frequency_days)

    def _normalize_task_values(
        self,
        name: str,
        category: str | None,
        frequency_days: int | float | str,
        last_completed: date | str | None,
        notes: str | None,
    ) -> tuple[str, str | None, int, date | None, str | None]:
        validated_name = ValidationService.validate_task_name(name)
        validated_category = ValidationService.validate_optional_text(
            category,
            "Category",
            ValidationService.CATEGORY_MAX_LENGTH,
        )
        validated_frequency = ValidationService.validate_frequency_days(frequency_days)
        validated_last_completed = ValidationService.validate_optional_date(
            last_completed,
            "Last completed",
        )
        validated_notes = ValidationService.validate_optional_text(
            notes,
            "Notes",
            ValidationService.NOTES_MAX_LENGTH,
        )

        return (
            validated_name,
            validated_category,
            validated_frequency,
            validated_last_completed,
            validated_notes,
        )

    def create_task(
        self,
        name: str,
        category: str | None,
        frequency_days: int | float | str,
        last_completed: date | str | None = None,
        notes: str | None = None,
    ) -> MaintenanceTask:
        (
            validated_name,
            validated_category,
            validated_frequency,
            validated_last_completed,
            validated_notes,
        ) = self._normalize_task_values(
            name,
            category,
            frequency_days,
            last_completed,
            notes,
        )

        next_due = None
        if validated_last_completed is not None:
            next_due = self.calculate_next_due_date(validated_last_completed, validated_frequency)

        task = MaintenanceTask(
            task_id=None,
            name=validated_name,
            category=validated_category,
            frequency_days=validated_frequency,
            last_completed=validated_last_completed,
            next_due=next_due,
            notes=validated_notes,
            active=1,
        )
        task.task_id = self.database_manager.insert_task(task)
        return task

    def get_task(self, task_id: int | str) -> MaintenanceTask:
        validated_task_id = ValidationService.validate_task_id(task_id)
        task = self.database_manager.get_task_by_id(validated_task_id)
        ValidationService.ensure_task_exists(validated_task_id, task is not None)
        if task is None:
            raise ValidationError(f"Task with ID {validated_task_id} was not found.")
        return task

    def update_task(
        self,
        task_id: int | str,
        name: str,
        category: str | None,
        frequency_days: int | float | str,
        last_completed: date | str | None,
        notes: str | None,
    ) -> MaintenanceTask:
        validated_task_id = ValidationService.validate_task_id(task_id)
        existing_task = self.database_manager.get_task_by_id(validated_task_id)
        ValidationService.ensure_task_exists(validated_task_id, existing_task is not None)

        if existing_task is None:
            raise ValidationError(f"Task with ID {validated_task_id} was not found.")

        (
            validated_name,
            validated_category,
            validated_frequency,
            validated_last_completed,
            validated_notes,
        ) = self._normalize_task_values(
            name,
            category,
            frequency_days,
            last_completed,
            notes,
        )

        next_due = None
        if validated_last_completed is not None:
            next_due = self.calculate_next_due_date(validated_last_completed, validated_frequency)

        updated_task = MaintenanceTask(
            task_id=validated_task_id,
            name=validated_name,
            category=validated_category,
            frequency_days=validated_frequency,
            last_completed=validated_last_completed,
            next_due=next_due,
            notes=validated_notes,
            active=existing_task.active,
        )

        updated = self.database_manager.update_task(updated_task)
        ValidationService.ensure_task_exists(validated_task_id, updated)
        return updated_task

    def delete_task(self, task_id: int | str) -> None:
        validated_task_id = ValidationService.validate_task_id(task_id)
        task_exists = self.database_manager.task_exists(validated_task_id)
        ValidationService.ensure_task_exists(validated_task_id, task_exists)

        deleted = self.database_manager.delete_task(validated_task_id)
        ValidationService.ensure_task_exists(validated_task_id, deleted)

    def get_tasks(self) -> list[MaintenanceTask]:
        return self.database_manager.get_tasks(active_only=None)

    def get_active_tasks(self) -> list[MaintenanceTask]:
        return self.database_manager.get_tasks(active_only=True)

    def mark_task_complete(
        self,
        task_id: int | str,
        completed_date: date | str | None = None,
        notes: str | None = None,
    ) -> MaintenanceTask:
        validated_task_id = ValidationService.validate_task_id(task_id)
        task = self.database_manager.get_task_by_id(validated_task_id)
        ValidationService.ensure_task_exists(validated_task_id, task is not None)

        if task is None:
            raise ValidationError(f"Task with ID {validated_task_id} was not found.")

        validated_completed_date = ValidationService.validate_optional_date(
            completed_date,
            "Completed date",
        ) or date.today()
        validated_notes = ValidationService.validate_optional_text(
            notes,
            "Notes",
            ValidationService.NOTES_MAX_LENGTH,
        )

        next_due = self.calculate_next_due_date(validated_completed_date, task.frequency_days)
        self.database_manager.record_task_completion(
            validated_task_id,
            validated_completed_date,
            next_due,
            validated_notes,
        )

        task.last_completed = validated_completed_date
        task.next_due = next_due
        return task

    def get_history(
        self,
        task_id: int | str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, object]]:
        validated_task_id = None
        if task_id is not None:
            validated_task_id = ValidationService.validate_task_id(task_id)
            task_exists = self.database_manager.task_exists(validated_task_id)
            ValidationService.ensure_task_exists(validated_task_id, task_exists)

        history_records = self.database_manager.get_history(validated_task_id, limit)
        task_name_lookup = {
            task.task_id: task.name
            for task in self.get_tasks()
            if task.task_id is not None
        }

        return [
            {
                "history_id": history.history_id,
                "task_id": history.task_id,
                "task_name": task_name_lookup.get(history.task_id, f"Task {history.task_id}"),
                "completed_date": history.completed_date,
                "notes": history.notes,
            }
            for history in history_records
        ]

    def get_task_status(self, task: MaintenanceTask, today: date | None = None) -> str:
        comparison_day = today or date.today()

        if task.next_due is None:
            return "Unscheduled"
        if task.next_due < comparison_day:
            return "Overdue"
        if task.next_due <= comparison_day + timedelta(days=self.DUE_SOON_DAYS):
            return "Due Soon"
        return "Current"

