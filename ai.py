"""AI and fallback insight generation for habit data."""

from __future__ import annotations

import os

import pandas as pd
from openai import OpenAI


def _rule_based_insights(dataframe: pd.DataFrame) -> str:
    """Generate deterministic insights when no API key is available."""
    if dataframe.empty:
        return "No habit data yet. Add entries for personalized insights."

    df = dataframe.copy()
    df["date"] = pd.to_datetime(df["date"])
    total = len(df)
    rate = (df["status"].sum() / total) * 100 if total else 0

    weekday_df = df[df["date"].dt.weekday < 5]
    weekend_df = df[df["date"].dt.weekday >= 5]
    weekday_rate = (
        (weekday_df["status"].sum() / len(weekday_df)) * 100 if len(weekday_df) else 0
    )
    weekend_rate = (
        (weekend_df["status"].sum() / len(weekend_df)) * 100 if len(weekend_df) else 0
    )

    latest_week_start = df["date"].max() - pd.Timedelta(days=6)
    this_week = df[df["date"] >= latest_week_start]
    prev_week = df[df["date"] < latest_week_start].tail(len(this_week))

    this_rate = (
        (this_week["status"].sum() / len(this_week)) * 100 if len(this_week) else 0
    )
    prev_rate = (
        (prev_week["status"].sum() / len(prev_week)) * 100 if len(prev_week) else 0
    )

    insights = [f"Overall completion rate is {rate:.1f}% across {total} entries."]
    if weekday_rate >= weekend_rate:
        insights.append("You are more consistent on weekdays than weekends.")
    else:
        insights.append("You tend to perform better on weekends than weekdays.")

    if len(this_week) >= 3 and len(prev_week) >= 3:
        if this_rate < prev_rate:
            insights.append("Your completion rate dropped this week. Consider lighter goals.")
        elif this_rate > prev_rate:
            insights.append("Great momentum: your completion rate improved this week.")

    top_habit = (
        df.groupby("name", as_index=False)["status"].mean().sort_values(
            "status", ascending=False
        )
    )
    if not top_habit.empty:
        best = top_habit.iloc[0]
        insights.append(
            f"Most consistent habit: {best['name']} ({best['status'] * 100:.1f}% success)."
        )

    return " ".join(insights)


def generate_ai_insights(dataframe: pd.DataFrame) -> str:
    """
    Generate AI insights from habit data.

    Uses OpenAI when OPENAI_API_KEY is set, otherwise falls back to rule-based insights.
    """
    if dataframe.empty:
        return "No habit data yet. Add entries to receive insights."

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _rule_based_insights(dataframe)

    try:
        client = OpenAI(api_key=api_key)
        summary_df = dataframe.copy()
        summary_df["date"] = pd.to_datetime(summary_df["date"]).dt.strftime("%Y-%m-%d")
        csv_data = summary_df[["name", "date", "status"]].to_csv(index=False)

        prompt = (
            "You are a habit coach. Analyze the habit completion dataset and provide 4-6 "
            "concise, practical insights. Mention consistency patterns, recent trend changes, "
            "and one actionable suggestion.\n\nDataset CSV:\n"
            f"{csv_data}"
        )

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            temperature=0.3,
        )
        return response.output_text.strip() or _rule_based_insights(dataframe)
    except Exception:
        return _rule_based_insights(dataframe)
