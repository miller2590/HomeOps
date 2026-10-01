from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path

from models import MaintenanceHistory, MaintenanceTask


class DatabaseManager:
    """Handle all SQLite operations for HomeOps."""

    def __init__(self, db_path: Path | None = None) -> None:
        project_root = Path(__file__).resolve().parent.parent
        self.db_path = db_path or project_root / "data" / "homeops.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @contextmanager
    def _managed_connection(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _to_db_date(value: date | None) -> str | None:
        return value.isoformat() if value else None

    @staticmethod
    def _from_db_date(value: str | None) -> date | None:
        return date.fromisoformat(value) if value else None

    @staticmethod
    def _row_to_task(row: sqlite3.Row) -> MaintenanceTask:
        return MaintenanceTask(
            task_id=row["task_id"],
            name=row["name"],
            category=row["category"],
            frequency_days=row["frequency_days"],
            last_completed=DatabaseManager._from_db_date(row["last_completed"]),
            next_due=DatabaseManager._from_db_date(row["next_due"]),
            notes=row["notes"],
            active=row["active"],
        )

    @staticmethod
    def _row_to_history(row: sqlite3.Row) -> MaintenanceHistory:
        return MaintenanceHistory(
            history_id=row["history_id"],
            task_id=row["task_id"],
            completed_date=DatabaseManager._from_db_date(row["completed_date"]),
            notes=row["notes"],
        )

    def initialize_database(self) -> None:
        """Create database tables if they do not already exist."""
        create_tasks_table = """
            CREATE TABLE IF NOT EXISTS maintenance_tasks (
                task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                frequency_days INTEGER NOT NULL,
                last_completed DATE,
                next_due DATE,
                notes TEXT,
                active INTEGER NOT NULL DEFAULT 1
            )
        """

        create_history_table = """
            CREATE TABLE IF NOT EXISTS maintenance_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                completed_date DATE NOT NULL,
                notes TEXT,
                FOREIGN KEY(task_id) REFERENCES maintenance_tasks(task_id)
            )
        """

        try:
            with self._managed_connection() as connection:
                connection.execute(create_tasks_table)
                connection.execute(create_history_table)
        except sqlite3.Error as exc:
            raise RuntimeError("Failed to initialize the HomeOps database.") from exc

    def insert_task(self, task: MaintenanceTask) -> int:
        query = """
            INSERT INTO maintenance_tasks (
                name, category, frequency_days, last_completed, next_due, notes, active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        parameters = (
            task.name,
            task.category,
            task.frequency_days,
            self._to_db_date(task.last_completed),
            self._to_db_date(task.next_due),
            task.notes,
            task.active,
        )

        try:
            with self._managed_connection() as connection:
                cursor = connection.execute(query, parameters)
                last_row_id = cursor.lastrowid
                if last_row_id is None:
                    raise RuntimeError("Failed to retrieve ID for saved maintenance task.")
                return int(last_row_id)
        except sqlite3.Error as exc:
            raise RuntimeError("Failed to save maintenance task.") from exc

    def get_task_by_id(self, task_id: int) -> MaintenanceTask | None:
        query = """
            SELECT
                task_id, name, category, frequency_days, last_completed, next_due, notes, active
            FROM maintenance_tasks
            WHERE task_id = ?
        """

        try:
            with self._managed_connection() as connection:
                row = connection.execute(query, (task_id,)).fetchone()
                return self._row_to_task(row) if row else None
        except sqlite3.Error as exc:
            raise RuntimeError("Failed to load maintenance task.") from exc

    def get_tasks(self, active_only: bool | None = None) -> list[MaintenanceTask]:
        query = """
            SELECT
                task_id, name, category, frequency_days, last_completed, next_due, notes, active
            FROM maintenance_tasks
        """
        parameters: list[int] = []

        if active_only is not None:
            query += " WHERE active = ?"
            parameters.append(1 if active_only else 0)

        query += """
            ORDER BY
                CASE WHEN next_due IS NULL THEN 1 ELSE 0 END,
                next_due ASC,
                name COLLATE NOCASE ASC
        """

        try:
            with self._managed_connection() as connection:
                rows = connection.execute(query, tuple(parameters)).fetchall()
                return [self._row_to_task(row) for row in rows]
        except sqlite3.Error as exc:
            raise RuntimeError("Failed to load maintenance tasks.") from exc

    def update_task(self, task: MaintenanceTask) -> bool:
        if task.task_id is None:
            raise ValueError("task_id is required to update a maintenance task.")

        query = """
            UPDATE maintenance_tasks
            SET
                name = ?,
                category = ?,
                frequency_days = ?,
                last_completed = ?,
                next_due = ?,
                notes = ?,
                active = ?
            WHERE task_id = ?
        """

        parameters = (
            task.name,
            task.category,
            task.frequency_days,
            self._to_db_date(task.last_completed),
            self._to_db_date(task.next_due),
            task.notes,
            task.active,
            task.task_id,
        )

        try:
            with self._managed_connection() as connection:
                cursor = connection.execute(query, parameters)
                return cursor.rowcount > 0
        except sqlite3.Error as exc:
            raise RuntimeError("Failed to update maintenance task.") from exc

    def deactivate_task(self, task_id: int) -> bool:
        query = "UPDATE maintenance_tasks SET active = 0 WHERE task_id = ?"

        try:
            with self._managed_connection() as connection:
                cursor = connection.execute(query, (task_id,))
                return cursor.rowcount > 0
        except sqlite3.Error as exc:
            raise RuntimeError("Failed to deactivate maintenance task.") from exc

    def delete_task(self, task_id: int) -> bool:
        """Soft-delete by deactivating a task for this first project version."""
        return self.deactivate_task(task_id)

    def insert_history(self, history: MaintenanceHistory) -> int:
        query = """
            INSERT INTO maintenance_history (task_id, completed_date, notes)
            VALUES (?, ?, ?)
        """

        parameters = (
            history.task_id,
            self._to_db_date(history.completed_date),
            history.notes,
        )

        try:
            with self._managed_connection() as connection:
                cursor = connection.execute(query, parameters)
                last_row_id = cursor.lastrowid
                if last_row_id is None:
                    raise RuntimeError("Failed to retrieve ID for saved history record.")
                return int(last_row_id)
        except sqlite3.Error as exc:
            raise RuntimeError("Failed to save maintenance history.") from exc

    def record_task_completion(
        self,
        task_id: int,
        completed_date: date,
        next_due: date,
        notes: str | None,
    ) -> None:
        """Save completion history and update the task in one transaction."""
        history_query = """
            INSERT INTO maintenance_history (task_id, completed_date, notes)
            VALUES (?, ?, ?)
        """
        task_query = """
            UPDATE maintenance_tasks
            SET last_completed = ?, next_due = ?
            WHERE task_id = ?
        """

        try:
            with self._managed_connection() as connection:
                connection.execute(
                    history_query,
                    (task_id, self._to_db_date(completed_date), notes),
                )
                cursor = connection.execute(
                    task_query,
                    (
                        self._to_db_date(completed_date),
                        self._to_db_date(next_due),
                        task_id,
                    ),
                )
                if cursor.rowcount == 0:
                    raise RuntimeError("Task was not found while marking complete.")
        except sqlite3.Error as exc:
            raise RuntimeError("Failed to mark maintenance task complete.") from exc

    def get_history(
        self,
        task_id: int | None = None,
        limit: int | None = None,
    ) -> list[MaintenanceHistory]:
        query = """
            SELECT history_id, task_id, completed_date, notes
            FROM maintenance_history
        """
        parameters: list[int] = []

        if task_id is not None:
            query += " WHERE task_id = ?"
            parameters.append(task_id)

        query += " ORDER BY completed_date DESC, history_id DESC"

        if limit is not None:
            query += " LIMIT ?"
            parameters.append(limit)

        try:
            with self._managed_connection() as connection:
                rows = connection.execute(query, tuple(parameters)).fetchall()
                return [self._row_to_history(row) for row in rows]
        except sqlite3.Error as exc:
            raise RuntimeError("Failed to load maintenance history.") from exc

    def task_exists(self, task_id: int) -> bool:
        query = "SELECT 1 FROM maintenance_tasks WHERE task_id = ?"

        try:
            with self._managed_connection() as connection:
                row = connection.execute(query, (task_id,)).fetchone()
                return row is not None
        except sqlite3.Error as exc:
            raise RuntimeError("Failed to check maintenance task.") from exc

