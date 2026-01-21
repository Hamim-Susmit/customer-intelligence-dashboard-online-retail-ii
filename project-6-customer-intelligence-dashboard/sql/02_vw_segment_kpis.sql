-- View: vw_segment_kpis
-- Aggregated KPIs by segment.

CREATE OR REPLACE VIEW vw_segment_kpis AS
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
),
customer_master AS (
    SELECT * FROM vw_customer_master
)
SELECT
    segment,
    COUNT(*) AS customers,
    SUM(monetary_revenue) AS revenue,
    AVG(monetary_revenue) AS avg_revenue_per_customer,
    AVG(recency_days) AS avg_recency_days,
    AVG(frequency_orders) AS avg_orders,
    AVG(return_rate) AS avg_return_rate,
    AVG(churn_prob) AS avg_churn_prob,
    AVG(clv) AS avg_clv
FROM customer_master
GROUP BY segment
ORDER BY revenue DESC;
