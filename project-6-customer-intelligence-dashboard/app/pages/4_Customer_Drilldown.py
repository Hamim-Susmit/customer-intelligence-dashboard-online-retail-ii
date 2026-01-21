"""Customer drilldown page."""
import streamlit as st

from app.db import query_df
from app.filters import get_filters
from app.ui_helpers import empty_state, format_currency

st.title("Customer Drilldown")
filters = get_filters()

customer_id_input = st.text_input("Search customer_id")

if customer_id_input:
    detail_df = query_df(
        """
        SELECT *
        FROM vw_customer_master
        WHERE customer_id = :customer_id
        """,
        {"customer_id": customer_id_input},
    )
    if detail_df.empty:
        empty_state("No customer found for the provided customer_id.")
    else:
        customer = detail_df.iloc[0]
        st.subheader(f"Customer {customer['customer_id']}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Country", customer.get("country", "-"))
            st.metric("Segment", customer.get("segment", "-"))
        with col2:
            st.metric("Recency (days)", int(customer.get("recency_days", 0)))
            st.metric("Orders", int(customer.get("frequency_orders", 0)))
        with col3:
            st.metric("Revenue", format_currency(customer.get("monetary_revenue")))
            st.metric("Avg Order Value", format_currency(customer.get("avg_order_value")))

st.subheader("Filtered Customers")

base_query = """
    SELECT *
    FROM vw_customer_master
    WHERE last_order_date BETWEEN :start_date AND :end_date
"""
params = {
    "start_date": filters["start_date"],
    "end_date": filters["end_date"],
}

if filters["country"] != "All":
    base_query += " AND country = :country"
    params["country"] = filters["country"]

if filters["segment"] != "All":
    base_query += " AND segment = :segment"
    params["segment"] = filters["segment"]

base_query += " ORDER BY monetary_revenue DESC LIMIT 1000"

customers_df = query_df(base_query, params)

if customers_df.empty:
    empty_state("No customers found for the selected filters.")
else:
    st.dataframe(customers_df, use_container_width=True)
