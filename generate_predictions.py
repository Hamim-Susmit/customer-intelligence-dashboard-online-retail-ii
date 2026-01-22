run """Script to generate and insert churn probability and CLV predictions."""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import pandas as pd
import numpy as np


def generate_predictions():
    """Generate churn probability and CLV predictions for all customers."""
    
    load_dotenv()
    db_url = os.getenv("SUPABASE_DB_URL")
    
    if not db_url:
        print("❌ Error: SUPABASE_DB_URL is not set. Add it to your .env file.")
        return False
    
    try:
        engine = create_engine(db_url, pool_pre_ping=True)
        print("✅ Connected to Supabase database")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return False
    
    # Get customer RFM metrics to base predictions on
    print("\n📊 Fetching customer RFM metrics...")
    try:
        rfm_df = pd.read_sql(
            """
            SELECT 
                customer_id,
                recency_days,
                frequency_orders,
                monetary_revenue
            FROM vw_customer_master
            WHERE customer_id IS NOT NULL
            """,
            engine
        )
        print(f"✅ Retrieved {len(rfm_df)} customers")
    except Exception as e:
        print(f"❌ Error fetching customer data: {e}")
        return False
    
    # Generate predictions based on RFM
    print("\n🤖 Generating predictions...")
    
    # Vectorized prediction generation (much faster)
    rfm_df['customer_id'] = rfm_df['customer_id'].astype(str).str.strip()
    rfm_df['recency_days'] = rfm_df['recency_days'].fillna(0).astype(float)
    rfm_df['frequency_orders'] = rfm_df['frequency_orders'].fillna(0).astype(float)
    rfm_df['monetary_revenue'] = rfm_df['monetary_revenue'].fillna(0).astype(float)
    
    # Churn probability: Higher recency = higher churn risk
    # Higher frequency and monetary = lower churn risk
    recency_norm = rfm_df['recency_days'] / rfm_df['recency_days'].max()
    frequency_norm = rfm_df['frequency_orders'] / rfm_df['frequency_orders'].max()
    monetary_norm = rfm_df['monetary_revenue'] / rfm_df['monetary_revenue'].max()
    
    rfm_df['churn_prob'] = np.minimum(0.95, np.maximum(0.05,
        (recency_norm * 0.6) - (frequency_norm * 0.2) - (monetary_norm * 0.2)
    )).round(4)
    
    # CLV (Customer Lifetime Value): Based on monetary and frequency
    # Higher monetary and frequency = higher CLV
    # Recent customers = higher potential CLV
    rfm_df['clv'] = (rfm_df['monetary_revenue'] * (1 + (rfm_df['frequency_orders'] * 0.2)) * 
                     (1 - (recency_norm * 0.3))).clip(lower=50).round(2)
    
    predictions_df = rfm_df[['customer_id', 'churn_prob', 'clv']].copy()
    
    print(f"✅ Generated {len(predictions_df)} predictions")
    print(f"   - Avg churn probability: {predictions_df['churn_prob'].mean():.2%}")
    print(f"   - Avg CLV: ${predictions_df['clv'].mean():,.2f}")
    print(f"   - Min CLV: ${predictions_df['clv'].min():,.2f}")
    print(f"   - Max CLV: ${predictions_df['clv'].max():,.2f}")
    
    # Insert into database
    print("\n📤 Inserting predictions into database...")
    try:
        # First truncate existing data
        with engine.connect() as connection:
            connection.execute(text("TRUNCATE customer_predictions"))
            connection.commit()
        
        # Then insert new data
        predictions_df.to_sql('customer_predictions', engine, if_exists='append', index=False)
        print(f"✅ Successfully inserted {len(predictions_df)} predictions")
        return True
    except Exception as e:
        print(f"❌ Error inserting predictions: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Generating customer predictions...\n")
    
    success = generate_predictions()
    
    if success:
        print("\n🎉 Predictions generated successfully!")
        print("\n📌 Next step:")
        print("   Refresh your Streamlit app at http://localhost:8503")
        print("   The Risk & Value page should now show churn and CLV insights!")
    else:
        print("\n❌ Prediction generation failed. Please check the errors above.")
