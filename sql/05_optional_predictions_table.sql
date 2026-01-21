-- Optional table: customer_predictions
-- Create this table if you have churn probability and CLV predictions.

CREATE TABLE IF NOT EXISTS customer_predictions (
    customer_id TEXT PRIMARY KEY,
    churn_prob NUMERIC,
    clv NUMERIC
);

-- Example inserts (replace with your predictions):
-- INSERT INTO customer_predictions (customer_id, churn_prob, clv)
-- VALUES
--   ('12345', 0.82, 1250.50),
--   ('67890', 0.35, 600.00);
