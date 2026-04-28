"""Helper utilities for the Streamlit habit tracker app."""

from __future__ import annotations

from datetime import date
from typing import Tuple

import pandas as pd


def validate_habit_input(name: str, habit_date: date | None) -> Tuple[bool, str]:
    """Validate user habit form input."""
    if not name or not name.strip():
        return False, "Habit name cannot be empty."
    if habit_date is None:
        return False, "Please select a valid date."
    return True, ""


def compute_metrics(dataframe: pd.DataFrame) -> tuple[int, float]:
    """Compute total records and completion rate percentage."""
    if dataframe.empty:
        return 0, 0.0
    total = int(len(dataframe))
    completion_rate = float((dataframe["status"].sum() / total) * 100)
    return total, completion_rate


def format_habits_for_display(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Prepare a clean table for UI display."""
    if dataframe.empty:
        return dataframe
    display_df = dataframe.copy()
    display_df["date"] = pd.to_datetime(display_df["date"]).dt.date
    display_df["status"] = display_df["status"].map({1: "Done", 0: "Not Done"})
    return display_df.rename(
        columns={"id": "ID", "name": "Habit", "date": "Date", "status": "Status"}
    )
