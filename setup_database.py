"""Script to run SQL setup files in order."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def setup_database():
    """Run all SQL setup files in order."""
    # Load environment variables
    load_dotenv()
    db_url = os.getenv("SUPABASE_DB_URL")
    
    if not db_url:
        print("❌ Error: SUPABASE_DB_URL is not set. Add it to your .env file.")
        sys.exit(1)
    
    # SQL files to run in order
    sql_files = [
        "sql/01_vw_customer_master.sql",
        "sql/02_vw_segment_kpis.sql",
        "sql/03_vw_monthly_metrics.sql",
        "sql/04_vw_top_at_risk.sql",
        "sql/05_optional_predictions_table.sql",
    ]
    
    # Create database engine
    try:
        engine = create_engine(db_url, pool_pre_ping=True)
        print("✅ Connected to Supabase database")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        sys.exit(1)
    
    # Execute each SQL file
    for sql_file in sql_files:
        file_path = Path(sql_file)
        
        if not file_path.exists():
            print(f"⚠️  Skipping {sql_file} (file not found)")
            continue
        
        try:
            with open(file_path, "r") as f:
                sql_content = f.read()
            
            # Split by semicolon to handle multiple statements
            statements = [s.strip() for s in sql_content.split(";") if s.strip()]
            
            with engine.connect() as connection:
                for statement in statements:
                    if statement:
                        connection.execute(text(statement))
                        connection.commit()
            
            print(f"✅ Successfully executed {sql_file}")
        
        except Exception as e:
            print(f"❌ Error executing {sql_file}: {e}")
            # Continue with next file instead of exiting
            continue
    
    print("\n🎉 Database setup complete!")


if __name__ == "__main__":
    setup_database()
