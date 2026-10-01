from __future__ import annotations

from datetime import date


class ValidationError(ValueError):
    """Raised when user input fails validation checks."""


class ValidationService:
    """Reusable validation rules for HomeOps input values."""

    NAME_MAX_LENGTH = 100
    CATEGORY_MAX_LENGTH = 50
    NOTES_MAX_LENGTH = 1000

    @staticmethod
    def validate_task_name(name: str) -> str:
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("Task name is required.")

        cleaned_name = name.strip()
        if len(cleaned_name) > ValidationService.NAME_MAX_LENGTH:
            raise ValidationError(
                f"Task name must be {ValidationService.NAME_MAX_LENGTH} characters or fewer."
            )

        return cleaned_name

    @staticmethod
    def validate_frequency_days(frequency_days: int | float | str) -> int:
        if frequency_days is None or frequency_days == "":
            raise ValidationError("Frequency in days is required.")

        if isinstance(frequency_days, float) and not frequency_days.is_integer():
            raise ValidationError("Frequency in days must be a whole number greater than 0.")

        try:
            normalized_frequency = int(frequency_days)
        except (TypeError, ValueError) as exc:
            raise ValidationError("Frequency in days must be an integer greater than 0.") from exc

        if normalized_frequency <= 0:
            raise ValidationError("Frequency in days must be greater than 0.")

        return normalized_frequency

    @staticmethod
    def validate_optional_date(value: date | str | None, field_name: str) -> date | None:
        if value is None or value == "":
            return None

        if isinstance(value, date):
            return value

        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError as exc:
                raise ValidationError(
                    f"{field_name} must be a valid date in YYYY-MM-DD format."
                ) from exc

        raise ValidationError(f"{field_name} must be a valid date.")

    @staticmethod
    def validate_optional_text(
        value: str | None,
        field_name: str,
        max_length: int,
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()
        if not cleaned_value:
            return None

        if len(cleaned_value) > max_length:
            raise ValidationError(f"{field_name} must be {max_length} characters or fewer.")

        return cleaned_value

    @staticmethod
    def validate_task_id(task_id: int | str) -> int:
        try:
            normalized_task_id = int(task_id)
        except (TypeError, ValueError) as exc:
            raise ValidationError("A valid task ID is required.") from exc

        if normalized_task_id <= 0:
            raise ValidationError("Task ID must be greater than 0.")

        return normalized_task_id

    @staticmethod
    def ensure_task_exists(task_id: int, exists: bool) -> None:
        if not exists:
            raise ValidationError(f"Task with ID {task_id} was not found.")

