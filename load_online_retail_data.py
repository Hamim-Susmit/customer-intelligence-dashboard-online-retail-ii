"""Script to load Online Retail II XLSX data into fact_orders table."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import pandas as pd


def find_xlsx_file():
    """Find Online Retail II XLSX file in the data folder."""
    project_dir = Path(__file__).parent
    data_raw_dir = project_dir / "data" / "raw"
    
    # Look in data/raw directory first
    if data_raw_dir.exists():
        for xlsx_file in data_raw_dir.glob("*.xlsx"):
            print(f"Found XLSX file: {xlsx_file.name}")
            return xlsx_file
    
    # Fallback to project root
    for xlsx_file in project_dir.glob("*.xlsx"):
        print(f"Found XLSX file: {xlsx_file.name}")
        return xlsx_file
    
    print("❌ No XLSX file found")
    print("   Please place your Online Retail II XLSX file in:")
    print(f"   {data_raw_dir}")
    return None


def load_online_retail_data(xlsx_path):
    """Load Online Retail II data from XLSX into fact_orders table."""
    
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
        id SERIAL PRIMARY KEY,
        invoice_no VARCHAR(10),
        invoice_date TIMESTAMP,
        customer_id VARCHAR(10),
        country VARCHAR(50),
        stock_code VARCHAR(20),
        description VARCHAR(100),
        quantity INTEGER,
        unit_price NUMERIC(10, 2)
    );
    
    CREATE INDEX idx_fact_orders_customer_id ON fact_orders(customer_id);
    CREATE INDEX idx_fact_orders_invoice_date ON fact_orders(invoice_date);
    CREATE INDEX idx_fact_orders_invoice_no ON fact_orders(invoice_no);
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
    
    # Read XLSX file
    print(f"\n📊 Reading data from {xlsx_path.name}...")
    try:
        df = pd.read_excel(xlsx_path)
        print(f"✅ Loaded {len(df):,} rows from XLSX")
    except Exception as e:
        print(f"❌ Error reading XLSX file: {e}")
        return False
    
    # Display column names
    print(f"\n📋 Columns in XLSX file:")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i}. {col}")
    
    # Map columns (Online Retail II standard column names)
    column_mapping = {
        'Invoice': 'invoice_no',
        'StockCode': 'stock_code',
        'Description': 'description',
        'Quantity': 'quantity',
        'InvoiceDate': 'invoice_date',
        'Price': 'unit_price',
        'Customer ID': 'customer_id',
        'Country': 'country',
    }
    
    # Try to match columns (case-insensitive)
    df_cols_lower = {col.lower(): col for col in df.columns}
    matched_mapping = {}
    
    for standard_col, target_col in column_mapping.items():
        lower_standard = standard_col.lower()
        if lower_standard in df_cols_lower:
            matched_mapping[df_cols_lower[lower_standard]] = target_col
        else:
            print(f"⚠️  Warning: Could not find column matching '{standard_col}'")
    
    if not matched_mapping:
        print("❌ Could not match any columns from XLSX to expected schema")
        print("   Expected columns: InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country")
        return False
    
    # Rename columns
    df_mapped = df[list(matched_mapping.keys())].rename(columns=matched_mapping)
    
    # Clean data
    print("\n🧹 Cleaning data...")
    
    # Convert types
    if 'invoice_date' in df_mapped.columns:
        df_mapped['invoice_date'] = pd.to_datetime(df_mapped['invoice_date'])
    
    if 'quantity' in df_mapped.columns:
        df_mapped['quantity'] = pd.to_numeric(df_mapped['quantity'], errors='coerce').fillna(0).astype(int)
    
    if 'unit_price' in df_mapped.columns:
        df_mapped['unit_price'] = pd.to_numeric(df_mapped['unit_price'], errors='coerce').fillna(0)
    
    if 'customer_id' in df_mapped.columns:
        df_mapped['customer_id'] = df_mapped['customer_id'].astype(str)
    
    # Remove null invoice_no
    df_mapped = df_mapped[df_mapped['invoice_no'].notna()]
    
    # Remove negative quantities (cancelled orders)
    if 'quantity' in df_mapped.columns:
        df_mapped = df_mapped[df_mapped['quantity'] > 0]
    
    print(f"✅ Cleaned data: {len(df_mapped):,} valid records")
    print(f"   - Customers: {df_mapped['customer_id'].nunique():,}")
    print(f"   - Invoices: {df_mapped['invoice_no'].nunique():,}")
    print(f"   - Countries: {df_mapped['country'].nunique()}")
    
    # Insert data
    print("\n📤 Uploading to database...")
    try:
        df_mapped.to_sql('fact_orders', engine, if_exists='append', index=False, method='multi', chunksize=1000)
        print(f"✅ Successfully inserted {len(df_mapped):,} records into fact_orders")
        return True
    except Exception as e:
        print(f"❌ Error inserting data: {e}")
        return False


def create_predictions_table():
    """Create optional customer_predictions table."""
    
    load_dotenv()
    db_url = os.getenv("SUPABASE_DB_URL")
    
    if not db_url:
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
    print("🚀 Loading Online Retail II data...\n")
    
    xlsx_file = find_xlsx_file()
    if not xlsx_file:
        sys.exit(1)
    
    success = load_online_retail_data(xlsx_file)
    
    if success:
        create_predictions_table()
        print("\n🎉 Data loading complete!")
        print("\n📌 Next steps:")
        print("   1. Run: python setup_database.py")
        print("   2. Refresh your Streamlit app at http://localhost:8503")
    else:
        print("\n❌ Data loading failed. Please check the errors above.")
        sys.exit(1)
