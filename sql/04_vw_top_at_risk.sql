-- View: vw_top_at_risk
-- Top customers by churn_prob * clv. Returns 0 rows when predictions are missing.

CREATE OR REPLACE VIEW vw_top_at_risk AS
WITH
-- CONFIG: update base table and column names here if your schema differs.
config AS (
    SELECT
        invoice_no,
        invoice_date::date AS invoice_date,
        customer_id,
        country,
        stock_code,
        description,
        quantity,
        unit_price
    FROM fact_orders
)
SELECT
    customer_id,
    country,
    monetary_revenue,
    recency_days,
    frequency_orders,
    segment,
    churn_prob,
    clv,
    (churn_prob * clv) AS priority_score
FROM vw_customer_master
WHERE churn_prob IS NOT NULL
  AND clv IS NOT NULL
ORDER BY priority_score DESC
LIMIT 200;
