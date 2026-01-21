-- View: vw_monthly_metrics
-- Monthly active customers, orders, revenue, and repeat rate.

CREATE OR REPLACE VIEW vw_monthly_metrics AS
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
order_level AS (
    SELECT
        invoice_no,
        customer_id,
        DATE_TRUNC('month', MIN(invoice_date))::date AS month,
        SUM(quantity * unit_price) AS order_revenue
    FROM config
    GROUP BY invoice_no, customer_id
),
customer_monthly_orders AS (
    SELECT
        month,
        customer_id,
        COUNT(*) AS monthly_orders
    FROM order_level
    GROUP BY month, customer_id
)
SELECT
    ol.month,
    COUNT(DISTINCT ol.customer_id) AS active_customers,
    COUNT(DISTINCT ol.invoice_no) AS orders,
    SUM(ol.order_revenue) AS revenue,
    AVG(CASE WHEN cmo.monthly_orders > 1 THEN 1.0 ELSE 0.0 END) AS repeat_rate
FROM order_level ol
LEFT JOIN customer_monthly_orders cmo
    ON ol.month = cmo.month
    AND ol.customer_id = cmo.customer_id
GROUP BY ol.month
ORDER BY ol.month;
