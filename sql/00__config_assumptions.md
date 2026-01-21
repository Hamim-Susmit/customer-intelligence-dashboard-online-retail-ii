# SQL Configuration Assumptions

This project expects a **single fact table** with order-line level data. The default
assumptions match the Online Retail II dataset and are used in each SQL view.

## Default Fact Table + Columns
**Table**: `fact_orders`

**Columns**:
- `invoice_no`
- `invoice_date`
- `customer_id`
- `country`
- `stock_code`
- `description`
- `quantity`
- `unit_price`

## How to Adapt for Different Schemas
If your base table or column names differ, update them in **one place per SQL file**:

1. Open each SQL file in `sql/`.
2. At the very top of each file, find the `CONFIG` CTE.
3. Replace `fact_orders` and/or the column names with your actual table/column names.

Everything else (the Streamlit app) reads from the views and will continue to work
as long as the views are created successfully.

## Optional Predictions
If you have churn probability and CLV predictions, create the optional
`customer_predictions` table by running `sql/05_optional_predictions_table.sql`.
The views are written to **gracefully handle empty predictions**.
