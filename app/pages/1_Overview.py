"""Overview page with monthly metrics."""
import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import query_df
from filters import get_filters
from ui_helpers import format_currency, safe_metric

st.title("Overview")
filters = get_filters()

monthly_df = query_df(
    """
    SELECT month, active_customers, orders, revenue, repeat_rate
    FROM vw_monthly_metrics
    WHERE month BETWEEN :start_date AND :end_date
    ORDER BY month
    """,
    {
        "start_date": filters["start_date"],
        "end_date": filters["end_date"],
    },
)

if monthly_df.empty:
    st.warning("No monthly metrics found for the selected date range.")
else:
    total_revenue = monthly_df["revenue"].sum()
    total_orders = monthly_df["orders"].sum()
    avg_active = monthly_df["active_customers"].mean()

    col1, col2, col3 = st.columns(3)
    with col1:
        safe_metric("Total Revenue", format_currency(total_revenue))
    with col2:
        safe_metric("Total Orders", int(total_orders))
    with col3:
        safe_metric("Avg Monthly Active", int(avg_active))

    revenue_fig = px.line(
        monthly_df,
        x="month",
        y="revenue",
        title="Monthly Revenue",
        markers=True,
    )
    revenue_fig.update_layout(yaxis_title="Revenue")

    active_fig = px.line(
        monthly_df,
        x="month",
        y="active_customers",
        title="Monthly Active Customers",
        markers=True,
    )
    active_fig.update_layout(yaxis_title="Active Customers")

    st.plotly_chart(revenue_fig, use_container_width=True)
    st.plotly_chart(active_fig, use_container_width=True)
