"""
Database Explorer - Check available tables and schema
"""

import pymysql
from sqlalchemy import create_engine, inspect
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection string from environment variables
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_SSL_MODE = os.getenv('DB_SSL_MODE')

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def explore_database():
    """Explore database schema and show available tables"""
    try:
        # Create engine with connect_args to disable SSL verification
        engine = create_engine(
            DATABASE_URL,
            connect_args={
                'ssl': {'ssl_mode': DB_SSL_MODE}
            }
        )
        
        print(f"Connecting to database: {DB_HOST}:{DB_PORT}/{DB_NAME}")
        print(f"SSL Mode: {DB_SSL_MODE}\n")
        
        # Get inspector
        inspector = inspect(engine)
        
        # Get all table names
        tables = inspector.get_table_names()
        print(f"Available tables: {tables}\n")
        
        # Inspect each table
        for table in tables:
            print(f"\n{'='*70}")
            print(f"Table: {table}")
            print('='*70)
            
            # Get columns
            columns = inspector.get_columns(table)
            print("\nColumns:")
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
            
            # Get row count and sample data
            try:
                query = f"SELECT * FROM {table} LIMIT 5"
                df = pd.read_sql(query, engine)
                print(f"\nRow count (first 5): {len(df)}")
                print("\nSample data:")
                print(df.head())
            except Exception as e:
                print(f"Error reading data: {e}")
        
        engine.dispose()
        
    except Exception as e:
        print(f"Error connecting to database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    explore_database()
