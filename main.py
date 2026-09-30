"""Application entry point for HomeOps."""

from nicegui import ui as nicegui_ui

from database.database_manager import DatabaseManager
from services.maintenance_service import MaintenanceService
from ui import setup_ui


def create_service() -> MaintenanceService:
    """Create and return the core service object used by the UI."""
    database_manager = DatabaseManager()
    return MaintenanceService(database_manager)


if __name__ in {"__main__", "__mp_main__"}:
    maintenance_service = create_service()
    setup_ui(maintenance_service)
    nicegui_ui.run(title="HomeOps")
