"""Main Streamlit entrypoint for Smart Habit Tracker with AI Insights."""

from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

from ai import generate_ai_insights
from charts import build_habit_completion_chart, build_trend_chart
from database import (
    create_table,
    delete_habit,
    fetch_habits,
    get_connection,
    insert_habit,
    update_habit,
)
from utils import compute_metrics, format_habits_for_display, validate_habit_input


@st.cache_resource
def _init_connection():
    """Initialize and cache DB connection per app session."""
    conn = get_connection()
    create_table(conn)
    return conn


def _render_add_habit_form(conn) -> None:
    """Render the habit creation form."""
    st.header("Add Habit")
    with st.form("add_habit_form", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            name = st.text_input("Habit Name", placeholder="e.g., Morning Run")
        with col2:
            habit_date = st.date_input("Date", value=date.today())

        status_toggle = st.toggle("Done", value=True)
        submitted = st.form_submit_button("Add Habit", type="primary")

        if submitted:
            is_valid, message = validate_habit_input(name, habit_date)
            if not is_valid:
                st.error(message)
                return
            try:
                insert_habit(conn, name=name, habit_date=habit_date, status=int(status_toggle))
                st.success("Habit saved successfully.")
            except Exception as exc:
                st.error(f"Could not save habit. Please try again. ({exc})")


def _render_filters():
    """Render date range and name filters."""
    st.header("Filters")
    filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 2])

    with filter_col1:
        start_date = st.date_input("Start Date", value=date.today() - timedelta(days=30))
    with filter_col2:
        end_date = st.date_input("End Date", value=date.today())
    with filter_col3:
        name_filter = st.text_input("Habit Name Filter", placeholder="Type to search...")

    if start_date > end_date:
        st.warning("Start date cannot be after end date. Filters reset to default range.")
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()

    return start_date, end_date, name_filter


def _render_metrics(filtered_df):
    total, completion_rate = compute_metrics(filtered_df)
    m1, m2 = st.columns(2)
    m1.metric("Total Habits", total)
    m2.metric("Completion Rate", f"{completion_rate:.1f}%")


def _render_data_table(filtered_df):
    st.header("Habit History")
    if filtered_df.empty:
        st.info("No records found for current filters.")
        return
    st.dataframe(
        format_habits_for_display(filtered_df),
        use_container_width=True,
        hide_index=True,
    )


def _render_manage_habits(conn, filtered_df):
    """Render update/delete controls for existing habits."""
    st.header("Manage Habits")
    if filtered_df.empty:
        st.info("No habits available to edit or delete.")
        return

    options = filtered_df.copy()
    options["date"] = options["date"].dt.date
    options["label"] = options.apply(
        lambda row: f"#{int(row['id'])} | {row['name']} | {row['date']} | "
        f"{'Done' if int(row['status']) == 1 else 'Not Done'}",
        axis=1,
    )

    selected_label = st.selectbox(
        "Choose habit record",
        options["label"].tolist(),
    )
    selected_row = options.loc[options["label"] == selected_label].iloc[0]
    selected_id = int(selected_row["id"])

    with st.form("edit_habit_form"):
        col1, col2 = st.columns([2, 1])
        with col1:
            updated_name = st.text_input("Habit Name (Edit)", value=str(selected_row["name"]))
        with col2:
            updated_date = st.date_input("Date (Edit)", value=selected_row["date"])
        updated_status = st.toggle("Done (Edit)", value=bool(int(selected_row["status"])))
        submit_update = st.form_submit_button("Update Habit", type="primary")

        if submit_update:
            is_valid, message = validate_habit_input(updated_name, updated_date)
            if not is_valid:
                st.error(message)
            else:
                try:
                    update_habit(
                        conn,
                        habit_id=selected_id,
                        name=updated_name,
                        habit_date=updated_date,
                        status=int(updated_status),
                    )
                    st.success("Habit updated successfully.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not update habit. ({exc})")

    confirm_delete = st.checkbox("Confirm delete selected habit")
    if st.button("Delete Habit", type="secondary"):
        if not confirm_delete:
            st.warning("Please confirm deletion first.")
            return
        try:
            delete_habit(conn, selected_id)
            st.success("Habit deleted successfully.")
            st.rerun()
        except Exception as exc:
            st.error(f"Could not delete habit. ({exc})")


def _render_charts(filtered_df):
    st.header("Trend Analysis")
    if filtered_df.empty:
        st.info("Add habits to view analytics charts.")
        return

    chart_col1, chart_col2 = st.columns(2)
    trend_fig = build_trend_chart(filtered_df)
    habit_fig = build_habit_completion_chart(filtered_df)

    with chart_col1:
        if trend_fig:
            st.plotly_chart(trend_fig, use_container_width=True)
    with chart_col2:
        if habit_fig:
            st.plotly_chart(habit_fig, use_container_width=True)


def _render_ai_section(filtered_df):
    st.header("AI Insights")
    if st.button("Generate Insights"):
        with st.spinner("Analyzing your habits..."):
            try:
                insight = generate_ai_insights(filtered_df)
                st.success(insight)
            except Exception as exc:
                st.error(f"Could not generate insights right now. ({exc})")


def main() -> None:
    st.set_page_config(
        page_title="Smart Habit Tracker with AI Insights",
        page_icon="✅",
        layout="wide",
    )
    st.title("Smart Habit Tracker with AI Insights")
    st.caption("Track habits daily, analyze progress, and receive practical AI insights.")

    conn = _init_connection()
    _render_add_habit_form(conn)
    st.divider()

    start_date, end_date, name_filter = _render_filters()

    try:
        filtered_df = fetch_habits(
            conn,
            start_date=start_date,
            end_date=end_date,
            habit_name=name_filter,
        )
    except Exception as exc:
        st.error(f"Failed to load habit data from database. ({exc})")
        return

    _render_metrics(filtered_df)
    st.divider()
    _render_data_table(filtered_df)
    st.divider()
    _render_manage_habits(conn, filtered_df)
    st.divider()
    _render_charts(filtered_df)
    st.divider()
    _render_ai_section(filtered_df)


if __name__ == "__main__":
    main()
