# Smart Habit Tracker with AI Insights

A production-ready Streamlit application for tracking daily habits, analyzing progress with data visualizations, and generating AI-powered coaching insights.

## Features

- Habit tracking with daily status (`Done` / `Not Done`)
- Structured habit history table with filters
- Date range and habit name filtering
- Metrics: total habits and completion rate
- Data science analytics with Plotly:
  - Line chart for completed habits over time
  - Bar chart for completion rate per habit
- AI insights:
  - OpenAI-based analysis when API key is available
  - Rule-based fallback when API key is missing

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

## AI Usage

- Uses OpenAI when `OPENAI_API_KEY` is set.
- Falls back to rule-based insights if API key is missing.
# codediintershipchallenge
