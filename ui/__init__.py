from __future__ import annotations

from nicegui import ui

from services.maintenance_service import MaintenanceService
from ui.dashboard import DashboardView
from ui.history_view import HistoryView
from ui.tasks_view import TasksView


def setup_ui(service: MaintenanceService) -> None:
	"""Register HomeOps pages and top-level navigation."""

	@ui.page("/")
	def home() -> None:
		with ui.header(elevated=True).classes("items-center justify-between"):
			ui.label("HomeOps").classes("text-h6")

		with ui.column().classes("w-full p-4 gap-4"):
			with ui.tabs().props("inline-label").classes("w-full") as tabs:
				dashboard_tab = ui.tab("Dashboard")
				tasks_tab = ui.tab("Maintenance Tasks")
				history_tab = ui.tab("History")

			with ui.tab_panels(tabs, value=dashboard_tab).classes("w-full"):
				with ui.tab_panel(dashboard_tab):
					dashboard_view = DashboardView(service)

				with ui.tab_panel(history_tab):
					history_view = HistoryView(service)

				def refresh_other_views() -> None:
					dashboard_view.refresh()
					history_view.refresh()

				with ui.tab_panel(tasks_tab):
					TasksView(service, on_data_changed=refresh_other_views)



__all__ = ["setup_ui"]

