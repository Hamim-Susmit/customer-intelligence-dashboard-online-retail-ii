"""Segments page with KPI breakdowns."""
import plotly.express as px
import streamlit as st

from app.db import query_df
from app.filters import get_filters

st.title("Segments")
filters = get_filters()

segment_df = query_df("SELECT * FROM vw_segment_kpis ORDER BY revenue DESC")

if filters["segment"] != "All":
    segment_df = segment_df[segment_df["segment"] == filters["segment"]]

if segment_df.empty:
    st.warning("No segment data available for the current filters.")
else:
    revenue_fig = px.bar(
        segment_df,
        x="segment",
        y="revenue",
        title="Revenue by Segment",
        text_auto=True,
    )
    customers_fig = px.bar(
        segment_df,
        x="segment",
        y="customers",
        title="Customers by Segment",
        text_auto=True,
    )

    st.plotly_chart(revenue_fig, use_container_width=True)
    st.plotly_chart(customers_fig, use_container_width=True)

    st.dataframe(segment_df, use_container_width=True)
