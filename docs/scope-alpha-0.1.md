# Personal Journey — Alpha 0.1 Scope

> **Historical document:** This file preserves the original Alpha 0.1 plan and
> no longer describes the current implementation. The project replaced MySQL
> with SQLite, expanded from Journal and Tracker to Routine, Tracker, and
> Journal, and evolved Tracker beyond the original event-type/occurrence model.
> Alpha 0.1 is complete. See `AGENTS.md` for the implemented architecture,
> product rules, privacy requirements, test baseline, and current status.

## Overview

Personal Journey is a local desktop application for personal journaling and routine tracking.

The application combines two core functions: a journal for written reflections and a tracker for recording recurring personal events. The goal of the project is to build a practical desktop application while progressively learning software development concepts such as GUI programming, relational databases, application structure, CRUD operations, and maintainable code organization.

The application is designed for a single local user. It does not include login, authentication, cloud sync, multi-user support, or data export in its initial scope.

## Project Goals

The main goal of Alpha 0.1 is to create the first functional foundation of the application.

This version should prove that the app can open as a desktop application, separate journal and tracker features into different interface areas, and persist data using a MySQL database.

Alpha 0.1 is not intended to be a complete life management system. It is the first working core of a larger application.

## Technical Direction

The application will be developed in Python.

The desktop interface will be built with PySide6.

Data will be stored in a MySQL database.

The codebase will use English for file names, function names, class names, variables, comments, documentation, and database table names.

The first versions should prioritize clarity over advanced architecture. The project may become more structured over time as the codebase grows.

## Application Structure

The application will have two main sections:

- Journal
- Tracker

These sections should be presented as separate tabs in the desktop interface.

The Journal tab is responsible for written entries.

The Tracker tab is responsible for custom routine events and their occurrences.

## Journal Scope

The Journal feature allows the user to create, read, update, and delete journal entries.

Each journal entry must have a title.

By default, the title should be generated automatically from the creation date and time. The user must be able to edit the title later.

Each journal entry should contain:

- id
- title
- content
- created_at
- updated_at

In Alpha 0.1, the Journal feature should support:

- creating a new journal entry;
- listing existing journal entries;
- opening an existing journal entry;
- editing an existing journal entry;
- deleting an existing journal entry.

## Tracker Scope

The Tracker feature allows the user to define custom events and register when those events happen.

A tracked event represents a recurring activity or personal marker, such as programming, gym, Dutch study, reading, culture, or any other custom event.

A tracked event does not measure intensity, duration, mood, quality, score, or other detailed metrics. It only records whether the event happened.

The tracker should be modeled with two concepts:

- event types;
- event occurrences.

An event type defines what can be tracked.

An event occurrence records that a specific event happened on a specific date.

Each event type should contain:

- id
- name
- created_at
- updated_at

Each event occurrence should contain:

- id
- event_type_id
- occurrence_date
- created_at

In Alpha 0.1, the Tracker feature should support:

- creating a custom event type;
- listing custom event types;
- deleting a custom event type;
- registering an occurrence for the current day;
- preventing occurrences from being registered for future dates.

Registering occurrences for past dates is part of the intended product direction, but it may be implemented after the first working tracker flow is complete.

## Date Rules

Journal entry titles are generated from the current date and time by default.

Tracker occurrences are registered for the current day by default.

The tracker may allow past dates in future versions.

The tracker must not allow future dates.

## Out of Scope for Alpha 0.1

The following features are intentionally excluded from Alpha 0.1:

- user accounts;
- login;
- password protection;
- cloud sync;
- data export;
- data import;
- encryption;
- calendar view;
- charts;
- statistics dashboard;
- streaks;
- mood tracking;
- intensity tracking;
- tags;
- search;
- filters;
- themes;
- notifications;
- mobile version;
- web version;
- AI features.

These features may be reconsidered after the core application is stable.

## Alpha 0.1 Completion Criteria

Alpha 0.1 is complete when the application can:

- open as a desktop application;
- display separate Journal and Tracker tabs;
- connect to a MySQL database;
- create, list, open, edit, and delete journal entries;
- create and list tracker event types;
- register an event occurrence for the current day;
- prevent future-dated tracker occurrences;
- store and retrieve data from MySQL;
- run locally without requiring login or external services.

## Development Principle

The project should grow progressively.

Each version should add a clear and limited improvement over the previous version.

The goal is not to build every possible feature immediately. The goal is to build a stable core, understand each layer of the application, and expand only after the current foundation is working.

## Next Step

After this scope document is created, the next step is to define the initial project structure and create the first minimal PySide6 window with two empty tabs: Journal and Tracker.
