# Personal Journey

Personal Journey is a local desktop application for personal journaling and routine tracking.

The project combines two core features: a journal for written personal entries and a tracker for recording recurring custom events. It is being developed as a practical software project to learn desktop application development, relational databases, CRUD operations, and maintainable application structure.

## Purpose

The goal of Personal Journey is to provide a simple local tool for recording personal progress over time.

The application is intentionally focused on two areas:

- writing journal entries;
- tracking whether custom personal events happened.

It is not intended to be a social app, cloud service, productivity platform, or analytics-heavy life management system.

## Core Features

The application will have two main sections:

- Journal
- Tracker

The Journal section will allow the user to create, read, edit, and delete written entries.

The Tracker section will allow the user to create custom event types and register when those events happen.

## Technical Stack

Personal Journey is planned as a desktop application built with:

- Python
- PySide6
- MySQL

The application is designed for a single local user and does not require login, cloud sync, or external services.

## Development Status

Current status: early development.

The first milestone is Alpha 0.1. Its goal is to create the first working version of the application with a desktop window, separate Journal and Tracker tabs, and MySQL persistence.

See `docs/scope-alpha-0.1.md` for the current scope.

## Alpha 0.1 Goals

Alpha 0.1 should support:

- opening the application as a desktop app;
- displaying separate Journal and Tracker tabs;
- connecting to a MySQL database;
- creating, listing, opening, editing, and deleting journal entries;
- creating and listing tracker event types;
- registering tracker event occurrences for the current day;
- preventing future-dated tracker occurrences.

## Out of Scope

The first version does not include:

- login;
- cloud sync;
- data export;
- encryption;
- calendar view;
- charts;
- statistics dashboard;
- mobile version;
- web version;
- AI features.

These features may be considered later after the core application is stable.

## Project Principle

Personal Journey will grow progressively.

The priority is to build a stable foundation before adding advanced features. Each development step should introduce a clear improvement without expanding the scope unnecessarily.
