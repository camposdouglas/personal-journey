# Personal Journey

Personal Journey is a single-user, offline desktop application for organizing a
daily routine, tracking weekly habits, and writing journal entries. It is both a
personal tool and a learning project focused on PySide6, SQLite, CRUD operations,
relational data modeling, and maintainable desktop application structure.

## Features

### Routine

- Separate Weekday and Weekend schedules.
- A 24-hour radial clock with minute-precise blocks.
- Cross-midnight and overlapping blocks.
- Custom names and `#RRGGBB` colors.
- Create, view, edit, and delete persistent routine blocks.
- Later-saved overlapping blocks appear on top.

### Tracker

- Custom trackers with duplicate names supported through hidden database IDs.
- Weekly goals from one to seven occurrences.
- Monday-to-Sunday navigation and completed-week history.
- Green, red, and gray daily states; only green counts toward progress.
- Future dates are blocked.
- Editable names, descriptions, and current-week goals.
- Archiving removes a tracker from the current week while preserving completed
  history.
- An Overall page summarizes progress for every tracker in the selected week.

### Journal

- Create, read, edit, and delete entries.
- Automatically generated, editable date-and-time titles.
- Creation and update timestamps.
- Plain-text content preservation.
- Protection against accidentally discarding active edits.

## Technology

- Python
- PySide6 (Qt for Python)
- SQLite
- Python `unittest`

The application requires no login, cloud account, network connection, or external
service.

## Project Structure

```text
personal-journey/
├── src/
│   ├── main.py
│   ├── db.py
│   ├── journal_repository.py
│   ├── tracker_repository.py
│   ├── routine_repository.py
│   ├── week_utils.py
│   └── ui/
├── tests/
├── data/
├── docs/
├── requirements.txt
└── README.md
```

PySide6 widgets handle presentation and interaction. Repository modules contain
validation and persistence logic, while `db.py` owns SQLite connections and schema
initialization.

## Setup and Run

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Linux:

```bash
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

Install dependencies and launch the application:

```bash
pip install -r requirements.txt
python src/main.py
```

## Tests

Run the complete test suite from the repository root:

```bash
python -m unittest discover -s tests
```

The current suite contains 26 repository and UI regression tests. UI tests run
headlessly and use temporary SQLite databases.

## Local Data and Privacy

Personal data is stored in:

```text
data/personal_journey.db
```

The database and its SQLite sidecar files are excluded from Git. Cloning this
repository therefore provides the application code but not the user's journal,
tracker, or routine data.

Because Git does not back up the database, copy it only while the application is
closed or use SQLite's backup API when backup support is added.

## Status

The current local-use milestone is feature-complete for its defined scope. The
application is ready for daily use.

Potential future work includes database backup and recovery, friendly SQLite error
messages, Tracker UI regression tests, and standalone packaging. New features
should be driven by experience using the application rather than added
speculatively.

The original Alpha 0.1 plan is preserved as a historical document in
[`docs/scope-alpha-0.1.md`](docs/scope-alpha-0.1.md).
