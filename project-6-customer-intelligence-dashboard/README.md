# Project 6: Customer Intelligence Decision System

A portfolio-grade, multi-page Streamlit dashboard powered by Supabase Postgres views. It delivers
customer insights (RFM-style KPIs, segments, monthly trends) and optionally integrates churn
probability + CLV predictions.

## Architecture
**Supabase Postgres views → Streamlit queries → Plotly charts**

1. SQL views in `sql/` reshape order-line data into analytics-ready aggregates.
2. Streamlit pages read the views using SQLAlchemy + psycopg2.
3. Plotly renders interactive charts for exploration.

## Repository Structure
```
project-6-customer-intelligence-dashboard/
  sql/
  app/
  reports/
  .env.example
  .gitignore
  requirements.txt
  README.md
```

## SQL Setup (Supabase)
Run the SQL files in order using the Supabase SQL editor:
1. `sql/00__config_assumptions.md` (reference only)
2. `sql/01_vw_customer_master.sql`
3. `sql/02_vw_segment_kpis.sql`
4. `sql/03_vw_monthly_metrics.sql`
5. `sql/04_vw_top_at_risk.sql`
6. `sql/05_optional_predictions_table.sql` (optional, if you have predictions)

> **Important:** If your fact table or column names differ from the defaults, update the
> `CONFIG` CTE at the top of each SQL file (see `sql/00__config_assumptions.md`).

## Optional Predictions
To enable churn probability and CLV insights on the **Risk & Value** page:
1. Run `sql/05_optional_predictions_table.sql`.
2. Insert predictions into `customer_predictions`.
3. The Risk & Value page will automatically activate when predictions exist.

## How to Run the App (Linux)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Add your Supabase connection string
cp .env.example .env

streamlit run app/Home.py
```

## Environment Variables
Create a `.env` file in the project root:
```
SUPABASE_DB_URL=postgresql+psycopg2://USER:PASSWORD@HOST:5432/DATABASE
```

## Screenshots
Add your screenshots in `reports/figures/` and update the placeholders below:
- Overview page: `reports/figures/overview.png`
- Segments page: `reports/figures/segments.png`
- Risk & Value page: `reports/figures/risk_value.png`
- Customer Drilldown: `reports/figures/customer_drilldown.png`

## Notes
- The app reads **only the SQL views**, so schema changes are isolated to the SQL layer.
- The Risk & Value page gracefully handles missing predictions and will show a friendly message
  if `customer_predictions` is empty or absent.
