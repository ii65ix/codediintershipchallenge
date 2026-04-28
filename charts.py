"""Plotly chart builders for habit analytics."""

from __future__ import annotations

import pandas as pd
import plotly.express as px


def build_trend_chart(dataframe: pd.DataFrame):
    """Build a line chart for daily completed habits."""
    if dataframe.empty:
        return None

    trend_df = dataframe.copy()
    trend_df["date"] = pd.to_datetime(trend_df["date"]).dt.date
    trend_df = (
        trend_df.groupby("date", as_index=False)["status"]
        .sum()
        .rename(columns={"status": "completed"})
        .sort_values("date")
    )

    figure = px.line(
        trend_df,
        x="date",
        y="completed",
        title="Habits Completed Over Time",
        markers=True,
    )
    figure.update_layout(xaxis_title="Date", yaxis_title="Completed Habits")
    return figure


def build_habit_completion_chart(dataframe: pd.DataFrame):
    """Build a bar chart for completion rate per habit."""
    if dataframe.empty:
        return None

    habit_df = dataframe.copy()
    grouped = (
        habit_df.groupby("name", as_index=False)["status"]
        .mean()
        .rename(columns={"name": "habit", "status": "completion_rate"})
    )
    grouped["completion_rate"] = grouped["completion_rate"] * 100
    grouped = grouped.sort_values("completion_rate", ascending=False)

    figure = px.bar(
        grouped,
        x="habit",
        y="completion_rate",
        title="Completion Rate Per Habit",
        text=grouped["completion_rate"].round(1).astype(str) + "%",
    )
    figure.update_layout(xaxis_title="Habit", yaxis_title="Completion Rate (%)")
    return figure
