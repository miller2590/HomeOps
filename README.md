# HomeOps

HomeOps is a small single-user home maintenance tracker built with Python, NiceGUI, and SQLite.

This first version supports:

- Creating recurring maintenance tasks
- Updating and deactivating tasks
- Marking tasks complete and recording history
- Automatically calculating `next_due` using `completed_date + frequency_days`
- Viewing overdue tasks, due-soon tasks, and recent completions on a dashboard

## Tech Stack

- Python
- NiceGUI
- SQLite (`sqlite3` from Python standard library)

## Project Structure

```text
HomeOps/
├── main.py
├── req.txt
├── assets/
│   └── images/
├── data/
│   └── homeops.db
├── database/
│   ├── __init__.py
│   └── database_manager.py
├── models/
│   ├── __init__.py
│   ├── maintenance_task.py
│   └── maintenance_history.py
├── services/
│   ├── __init__.py
│   ├── maintenance_service.py
│   └── validation_service.py
└── ui/
	├── __init__.py
	├── dashboard.py
	├── tasks_view.py
	├── task_form.py
	└── history_view.py
```

## Run Locally (Windows PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r req.txt
python main.py
```

When the app starts, SQLite is initialized automatically at `data/homeops.db`.

## Scope Notes

The first version intentionally excludes authentication, cloud sync, notifications, budgeting, receipts, and multi-property support.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
