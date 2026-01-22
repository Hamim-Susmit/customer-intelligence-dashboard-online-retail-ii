"""Sidebar filters shared across pages."""
from __future__ import annotations

from datetime import date

import streamlit as st

from db import query_df


def get_filters() -> dict:
    """Render sidebar filters and return selections."""
    st.sidebar.header("Filters")

    dates_df = query_df(
        """
        SELECT
            MIN(last_order_date) AS min_date,
            MAX(last_order_date) AS max_date
        FROM vw_customer_master
        """
    )
    min_date = dates_df["min_date"].iloc[0] if not dates_df.empty else None
    max_date = dates_df["max_date"].iloc[0] if not dates_df.empty else None

    default_start = min_date or date(2010, 1, 1)
    default_end = max_date or date.today()

    start_date, end_date = st.sidebar.date_input(
        "Last order date range",
        value=(default_start, default_end),
    )

    countries_df = query_df(
        "SELECT DISTINCT country FROM vw_customer_master WHERE country IS NOT NULL ORDER BY country"
    )
    countries = ["All"] + countries_df["country"].dropna().tolist()
    country = st.sidebar.selectbox("Country", options=countries)

    segments_df = query_df(
        "SELECT DISTINCT segment FROM vw_customer_master WHERE segment IS NOT NULL ORDER BY segment"
    )
    segments = ["All"] + segments_df["segment"].dropna().tolist()
    segment = st.sidebar.selectbox("Segment", options=segments)

    churn_min = st.sidebar.slider("Min churn probability", 0.0, 1.0, 0.0, 0.05)
    clv_min = st.sidebar.number_input("Min CLV", min_value=0.0, value=0.0, step=50.0)

    return {
        "start_date": start_date,
        "end_date": end_date,
        "country": country,
        "segment": segment,
        "churn_min": churn_min,
        "clv_min": clv_min,
    }
