-- View: vw_customer_master
-- One row per customer with RFM-style metrics and optional churn/CLV predictions.

-- Ensure optional predictions table exists (safe if already created).
CREATE TABLE IF NOT EXISTS customer_predictions (
    customer_id TEXT PRIMARY KEY,
    churn_prob NUMERIC,
    clv NUMERIC
);

CREATE OR REPLACE VIEW vw_customer_master AS
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
        MIN(invoice_date) AS invoice_date,
        SUM(quantity * unit_price) AS order_revenue,
        SUM(CASE WHEN quantity < 0 THEN quantity * unit_price ELSE 0 END) AS return_revenue
    FROM config
    GROUP BY invoice_no, customer_id
),
customer_orders AS (
    SELECT
        customer_id,
        MIN(invoice_date) AS first_order_date,
        MAX(invoice_date) AS last_order_date,
        COUNT(DISTINCT invoice_no) AS frequency_orders,
        SUM(order_revenue) AS monetary_revenue,
        SUM(return_revenue) AS total_return_revenue
    FROM order_level
    GROUP BY customer_id
),
country_ranked AS (
    SELECT
        customer_id,
        country,
        COUNT(*) AS country_orders,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY COUNT(*) DESC, country ASC
        ) AS rn
    FROM config
    GROUP BY customer_id, country
)
SELECT
    co.customer_id,
    cr.country,
    co.first_order_date,
    co.last_order_date,
    (CURRENT_DATE - co.last_order_date) AS recency_days,
    co.frequency_orders,
    co.monetary_revenue,
    CASE
        WHEN co.frequency_orders = 0 THEN NULL
        ELSE co.monetary_revenue / co.frequency_orders
    END AS avg_order_value,
    CASE
        WHEN co.monetary_revenue = 0 THEN NULL
        ELSE ABS(co.total_return_revenue) / NULLIF(co.monetary_revenue, 0)
    END AS return_rate,
    CASE
        WHEN co.monetary_revenue >= 1000 AND (CURRENT_DATE - co.last_order_date) <= 60
            THEN 'High Value Active'
        WHEN co.monetary_revenue >= 1000 AND (CURRENT_DATE - co.last_order_date) > 60
            THEN 'High Value At Risk'
        WHEN co.monetary_revenue < 1000 AND (CURRENT_DATE - co.last_order_date) <= 60
            THEN 'Active'
        ELSE 'Dormant'
    END AS segment,
    cp.churn_prob,
    cp.clv
FROM customer_orders co
LEFT JOIN country_ranked cr
    ON co.customer_id = cr.customer_id
    AND cr.rn = 1
LEFT JOIN customer_predictions cp
    ON co.customer_id = cp.customer_id;
