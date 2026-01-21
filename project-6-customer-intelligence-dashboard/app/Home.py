"""Home page for the Customer Intelligence Decision System."""
import streamlit as st

st.set_page_config(page_title="Customer Intelligence Dashboard", layout="wide")

st.title("Customer Intelligence Decision System")

st.markdown(
    """
This multi-page Streamlit dashboard connects to your Supabase Postgres database and
presents customer intelligence insights using pre-built SQL views.

**Navigation**
- **Overview**: Monthly revenue and active customer trends.
- **Segments**: Segment-level KPIs and comparisons.
- **Risk & Value**: Churn/CLV insights (enabled when predictions exist).
- **Customer Drilldown**: Search and explore customer-level metrics.
"""
)

st.success("Use the sidebar to navigate between pages.")
