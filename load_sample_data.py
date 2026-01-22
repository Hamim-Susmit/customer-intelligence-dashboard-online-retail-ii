"""Script to create and populate fact_orders table with sample data."""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import pandas as pd
from datetime import datetime, timedelta
import random


def create_and_populate_fact_orders():
    """Create fact_orders table and populate with sample Online Retail II data."""
    
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
    
    # Create fact_orders table
    create_table_sql = """
    DROP TABLE IF EXISTS fact_orders CASCADE;
    
    CREATE TABLE fact_orders (
        invoice_no VARCHAR(10) NOT NULL,
        invoice_date TIMESTAMP NOT NULL,
        customer_id VARCHAR(10),
        country VARCHAR(50),
        stock_code VARCHAR(20),
        description VARCHAR(100),
        quantity INTEGER,
        unit_price NUMERIC(10, 2),
        PRIMARY KEY (invoice_no, stock_code, customer_id)
    );
    
    CREATE INDEX idx_fact_orders_customer_id ON fact_orders(customer_id);
    CREATE INDEX idx_fact_orders_invoice_date ON fact_orders(invoice_date);
    """
    
    try:
        with engine.connect() as connection:
            for statement in create_table_sql.split(';'):
                if statement.strip():
                    connection.execute(text(statement))
                    connection.commit()
        print("✅ Created fact_orders table")
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False
    
    # Generate sample data (Online Retail II style)
    print("📊 Generating sample data...")
    
    countries = ['United Kingdom', 'Netherlands', 'EIRE', 'Germany', 'France', 'Sweden',
                 'Switzerland', 'Spain', 'Poland', 'Italy', 'Belgium', 'Norway', 'Finland',
                 'Cyprus', 'Japan', 'USA', 'Australia', 'Canada']
    
    stock_codes = [f'SKU{i:05d}' for i in range(1, 101)]
    descriptions = [f'Product {i}' for i in range(1, 101)]
    
    records = []
    start_date = datetime(2010, 1, 1)
    end_date = datetime(2011, 12, 31)
    
    num_customers = 500
    num_invoices = 5000
    
    customer_ids = [f'C{i:06d}' for i in range(1, num_customers + 1)]
    
    for invoice_idx in range(num_invoices):
        invoice_no = f'INV{invoice_idx:08d}'
        invoice_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        customer_id = random.choice(customer_ids)
        country = random.choice(countries)
        
        # 1-5 items per invoice
        num_items = random.randint(1, 5)
        for _ in range(num_items):
            stock_code = random.choice(stock_codes)
            description = f'Product {stock_codes.index(stock_code) + 1}'
            quantity = random.randint(1, 20)
            unit_price = round(random.uniform(1.0, 100.0), 2)
            
            records.append({
                'invoice_no': invoice_no,
                'invoice_date': invoice_date,
                'customer_id': customer_id,
                'country': country,
                'stock_code': stock_code,
                'description': description,
                'quantity': quantity,
                'unit_price': unit_price
            })
    
    df = pd.DataFrame(records)
    
    # Insert data
    try:
        df.to_sql('fact_orders', engine, if_exists='append', index=False)
        print(f"✅ Inserted {len(df):,} order records into fact_orders")
        print(f"   - Customers: {df['customer_id'].nunique():,}")
        print(f"   - Invoices: {df['invoice_no'].nunique():,}")
        print(f"   - Countries: {df['country'].nunique()}")
        return True
    except Exception as e:
        print(f"❌ Error inserting data: {e}")
        return False


def create_predictions_table():
    """Create optional customer_predictions table."""
    
    load_dotenv()
    db_url = os.getenv("SUPABASE_DB_URL")
    
    if not db_url:
        print("❌ Error: SUPABASE_DB_URL is not set.")
        return False
    
    try:
        engine = create_engine(db_url, pool_pre_ping=True)
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return False
    
    create_predictions_sql = """
    DROP TABLE IF EXISTS customer_predictions CASCADE;
    
    CREATE TABLE customer_predictions (
        customer_id VARCHAR(10) PRIMARY KEY,
        churn_prob NUMERIC(5, 4),
        clv NUMERIC(12, 2)
    );
    """
    
    try:
        with engine.connect() as connection:
            for statement in create_predictions_sql.split(';'):
                if statement.strip():
                    connection.execute(text(statement))
                    connection.commit()
        print("✅ Created customer_predictions table (optional)")
        return True
    except Exception as e:
        print(f"❌ Error creating predictions table: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Setting up fact_orders table with sample data...\n")
    
    success = create_and_populate_fact_orders()
    
    if success:
        create_predictions_table()
        print("\n🎉 Sample data setup complete!")
        print("   Now run: python setup_database.py")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
