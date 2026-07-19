# AGENTS.md — Personal Journey

Guidance for AI agents and contributors working in this repository.

## Project Overview

**Personal Journey** is a local desktop application with three core features:

- **Routine** — design separate weekday and weekend schedules on a 24-hour clock.
- **Tracker** — record binary daily progress against weekly goals.
- **Journal** — create, read, edit, and delete written entries.

It is a single-user, local, offline application. No login, no cloud sync, no
external services. It is developed both as a real personal tool and as a
portfolio project to practice desktop development, relational data modeling,
CRUD operations, and clean application structure.

## Tech Stack

- **Language:** Python
- **GUI:** PySide6 (Qt for Python)
- **Database:** SQLite (local file-based persistence)

> Note: earlier planning documents referenced MySQL. The project has since
> standardized on **SQLite** as the single source of truth for persistence.
> `README.md` and `docs/` are being migrated to reflect this.

## Project Structure

```
personal-journey/
├─ src/
│  ├─ main.py                  # Application entry point
│  ├─ db.py                    # SQLite schema and connections
│  ├─ journal_repository.py    # Journal persistence
│  ├─ tracker_repository.py    # Tracker persistence and history
│  ├─ routine_repository.py    # Routine persistence
│  ├─ week_utils.py            # Tracker week calculations
│  └─ ui/
│     ├─ main_window.py        # Main window and outer tabs
│     ├─ journal_tab.py        # Journal UI
│     ├─ tracker_tab.py        # Tracker tab orchestration
│     ├─ tracker_page.py       # Individual tracker UI
│     ├─ tracker_overall_page.py
│     ├─ tracker_dialog.py
│     ├─ routine_tab.py        # Routine controls and lists
│     └─ routine_clock.py      # 24-hour chart rendering
├─ tests/                      # Repository and UI regression tests
├─ data/
│  └─ personal_journey.db      # Private local data; Git-ignored
├─ docs/
│  └─ scope-alpha-0.1.md       # Historical first-milestone scope
├─ requirements.txt
└─ README.md
```

## Architecture

The application uses a deliberately simple separation of concerns:

- **UI layer** (PySide6 widgets) should handle presentation and user interaction.
- **Repository layer** should validate data and perform SQLite operations.
- **Database module** should own connections, schema initialization, and migrations.

SQLite is the implemented source of truth. Do not reintroduce in-memory mock data
or place SQL directly in UI classes. Prefer clarity over cleverness; add
abstractions only when they solve a concrete problem.

## Current Product Rules

- **journal entries:** `id`, `title`, `content`, `created_at`, `updated_at`
- **trackers:** identity, editable name/description, lifecycle, weekly target history
- **tracker daily statuses:** one green or red status per tracker and date
- **routine blocks:** schedule, name, minute-precise start/end, color, layer order

Rules:

- Journal titles default to the creation date/time and remain editable.
- Tracker weeks run Monday through Sunday, starting with Week 0 on 2026-07-13.
- Future tracker dates are blocked; green counts as completed, red/gray do not.
- Tracker names may duplicate because database IDs define identity.
- Archived trackers disappear from the current week but remain in completed history.
- Routine has independent Weekday and Weekend schedules.
- Routine times use minute precision, may cross midnight, and may overlap; the
  most recently saved overlapping block is drawn on top.
- Routine names may duplicate and colors use `#RRGGBB` values.

## Privacy and Local Data

- `data/personal_journey.db` contains personal user data and must never be committed.
- SQLite sidecars (`*.db-*`) are also private and Git-ignored.
- `AGENTS.local.md` contains private machine-local guidance and must never be committed.
- Tests must replace `db.DB_PATH` with a temporary database and must not mutate the
  personal database.

## Conventions

- **English everywhere** — file names, identifiers, comments, docs, and database
  table/column names.
- **Clarity first** — favor simple, readable structure over premature abstraction.
- **Progressive growth** — each change adds one clear, limited improvement.

## Git Workflow

- Commit **one logical, self-contained change** at a time; each commit should
  leave the app in a working state.
- If a commit message needs the word "and", it is probably two commits.
- Use **imperative mood** messages: `Add ...`, `Fix ...`, `Refactor ...`.

## How We Work

- Iterative development with review checkpoints ("pitstops") to confirm
  understanding before moving on.
- Momentum first, polish at checkpoints — *done is better than perfect-not-done*.
- Explanations are expected to be concrete and, where useful, line-by-line.

## Running the App

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux:    source .venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

Run the complete test suite with:

```bash
python -m unittest discover -s tests
```

## Current Status

The current local-use milestone is feature-complete for its defined scope.
Routine, Tracker, and Journal all use SQLite persistence and support their intended
CRUD flows. The suite currently contains **26 passing tests**, including Journal
and Routine UI regression coverage.

Optional next work includes database backup/recovery, friendly SQLite failure
messages, Tracker UI regression tests, packaging, and migration of outdated public
documentation. Do not assume a new feature is needed before real daily use reveals
a concrete requirement.
