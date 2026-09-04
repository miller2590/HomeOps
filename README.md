# HomeOps

HomeOps is a simple home maintenance tracker built with Python, SQLite, and NiceGUI.

The application is designed to help homeowners keep track of recurring maintenance tasks, completion history, and upcoming due dates.

## Features

* Add, edit, and delete maintenance items
* Set recurring maintenance intervals
* Track completed maintenance
* Automatically calculate next due dates
* View upcoming and overdue tasks
* Store maintenance data using SQLite
* Simple web-based interface using NiceGUI

## Tech Stack

* Python
* NiceGUI
* SQLite
* Git / GitHub

## Project Structure

```text
homeops/
├── assets/
├── database/
├── models/
├── services/
├── ui/
├── main.py
└── README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/homeops.git
cd homeops
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment:

**Windows**

```bash
.venv\Scripts\activate
```

**macOS/Linux**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running HomeOps

```bash
python main.py
```

NiceGUI will start the application and provide a local URL in the terminal.

## Project Scope

The initial version of HomeOps focuses on the core maintenance workflow:

1. Create a maintenance item
2. Define its maintenance interval
3. Track when it is completed
4. Calculate the next due date
5. Store and display maintenance history

Features such as notifications, multiple properties, cloud synchronization, receipt storage, and user accounts are outside the initial project scope.

## Future Improvements

Possible future additions include:

* Maintenance reminders
* Multiple properties
* Receipt and document storage
* Maintenance cost tracking
* Vehicle maintenance
* Data backup and export

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
