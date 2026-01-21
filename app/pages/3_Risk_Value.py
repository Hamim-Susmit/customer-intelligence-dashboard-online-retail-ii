"""Risk & Value page with churn/CLV insights."""
import plotly.express as px
import streamlit as st

from app.db import query_df
from app.filters import get_filters
from app.ui_helpers import empty_state

st.title("Risk & Value")
filters = get_filters()

predictions_check = query_df(
    """
    SELECT COUNT(*) AS cnt
    FROM vw_customer_master
    WHERE churn_prob IS NOT NULL AND clv IS NOT NULL
    """
)

if predictions_check["cnt"].iloc[0] == 0:
    empty_state(
        "Churn probability and CLV predictions are not available yet. "
        "Create the optional `customer_predictions` table and insert predictions "
        "to enable this view."
    )
else:
    risk_df = query_df(
        """
        SELECT
            customer_id,
            country,
            segment,
            monetary_revenue,
            churn_prob,
            clv,
            (churn_prob * clv) AS priority_score
        FROM vw_customer_master
        WHERE churn_prob IS NOT NULL
          AND clv IS NOT NULL
          AND churn_prob >= :churn_min
          AND clv >= :clv_min
        ORDER BY priority_score DESC
        """,
        {
            "churn_min": filters["churn_min"],
            "clv_min": filters["clv_min"],
        },
    )

    if filters["country"] != "All":
        risk_df = risk_df[risk_df["country"] == filters["country"]]
    if filters["segment"] != "All":
        risk_df = risk_df[risk_df["segment"] == filters["segment"]]

    if risk_df.empty:
        st.warning("No customers meet the current risk filters.")
    else:
        scatter_fig = px.scatter(
            risk_df,
            x="churn_prob",
            y="clv",
            size="priority_score",
            color="segment",
            hover_data=["customer_id", "country", "monetary_revenue"],
            title="Churn Probability vs CLV",
        )
        scatter_fig.update_layout(xaxis_title="Churn Probability", yaxis_title="CLV")

        st.plotly_chart(scatter_fig, use_container_width=True)

        top_df = risk_df.sort_values("priority_score", ascending=False).head(50)
        st.subheader("Top 50 Priority Customers")
        st.dataframe(top_df, use_container_width=True)
