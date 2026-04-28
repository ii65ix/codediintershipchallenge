"""SQLite database utilities for habit tracking."""

from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd

DEFAULT_DB_PATH = Path("habits.db")


def get_connection(db_path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Create and return a SQLite connection."""
    connection = sqlite3.connect(db_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def create_table(connection: sqlite3.Connection) -> None:
    """Create the habits table if it does not exist."""
    query = """
    CREATE TABLE IF NOT EXISTS habits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        date TEXT NOT NULL,
        status INTEGER NOT NULL CHECK(status IN (0, 1))
    );
    """
    with connection:
        connection.execute(query)


def insert_habit(
    connection: sqlite3.Connection,
    name: str,
    habit_date: date,
    status: int,
) -> None:
    """Insert one habit record into the database."""
    query = "INSERT INTO habits(name, date, status) VALUES (?, ?, ?);"
    with connection:
        connection.execute(query, (name.strip(), habit_date.isoformat(), int(status)))


def fetch_habits(
    connection: sqlite3.Connection,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    habit_name: str = "",
) -> pd.DataFrame:
    """
    Fetch habits with optional filters.

    Results are sorted by latest date first, then latest id first.
    """
    base_query = "SELECT id, name, date, status FROM habits WHERE 1=1"
    params: list[object] = []

    if start_date:
        base_query += " AND date >= ?"
        params.append(start_date.isoformat())
    if end_date:
        base_query += " AND date <= ?"
        params.append(end_date.isoformat())
    if habit_name.strip():
        base_query += " AND LOWER(name) LIKE ?"
        params.append(f"%{habit_name.strip().lower()}%")

    base_query += " ORDER BY date DESC, id DESC;"

    rows = connection.execute(base_query, params).fetchall()
    dataframe = pd.DataFrame(rows, columns=["id", "name", "date", "status"])
    if not dataframe.empty:
        dataframe["date"] = pd.to_datetime(dataframe["date"])
        dataframe["status"] = dataframe["status"].astype(int)
    return dataframe


def update_habit(
    connection: sqlite3.Connection,
    habit_id: int,
    name: str,
    habit_date: date,
    status: int,
) -> None:
    """Update an existing habit record by id."""
    query = "UPDATE habits SET name = ?, date = ?, status = ? WHERE id = ?;"
    with connection:
        connection.execute(query, (name.strip(), habit_date.isoformat(), int(status), habit_id))


def delete_habit(connection: sqlite3.Connection, habit_id: int) -> None:
    """Delete one habit record by id."""
    query = "DELETE FROM habits WHERE id = ?;"
    with connection:
        connection.execute(query, (habit_id,))
