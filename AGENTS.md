# AGENTS.md — Personal Journey

Guidance for AI agents and contributors working in this repository.

## Project Overview

**Personal Journey** is a local desktop application for personal journaling and
habit tracking. It has two core features:

- **Journal** — create, read, edit, and delete written entries.
- **Tracker** — define custom recurring events and record when they happen.

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
│  ├─ main.py              # Application entry point
│  └─ ui/
│     ├─ main_window.py    # Main window, tab container
│     ├─ journal_tab.py    # Journal feature UI
│     └─ tracker_tab.py    # Tracker feature UI (in progress)
├─ docs/
│  └─ scope-alpha-0.1.md   # Scope for the first milestone
├─ requirements.txt
└─ README.md
```

## Architecture Direction

The project is intentionally evolving toward a clean separation of concerns:

- **UI layer** (PySide6 widgets) should handle presentation and user interaction.
- **Data layer** (SQLite access) should handle persistence, kept separate from UI.

The current code holds entries in memory; introducing a dedicated persistence
layer so data survives restarts is the key near-term architectural step. Prefer
clarity over cleverness; the codebase should stay readable as it grows.

## Data Model (Alpha 0.1)

- **journal entries:** `id`, `title`, `content`, `created_at`, `updated_at`
- **event types:** `id`, `name`, `created_at`, `updated_at`
- **event occurrences:** `id`, `event_type_id`, `occurrence_date`, `created_at`

Rules: journal titles default to the creation date/time and are editable;
tracker occurrences default to the current day; **future-dated occurrences are
not allowed** (past dates may be supported later).

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

## Current Status

Early development. Milestone: **Alpha 0.1** — a working desktop window with
Journal and Tracker tabs, full journal CRUD, basic tracker event types and
occurrences, and SQLite persistence.
