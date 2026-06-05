import time
import os
import sys

# Add current path to resolve imports
sys.path.append(os.getcwd())

from engines.data_engine import DataEngine

file_path = r"e:\The_Council_v2\backend\uploads\Liquor_Sales.csv"

start = time.time()
print(f"Loading data from {file_path}...")
de = DataEngine()
de.load_data(file_path)
print(f"Loaded in {time.time() - start:.2f}s")

if de.df is None:
    print("DataFrame failed to load!")
    sys.exit(1)

# Inspect date format detected
print(f"Metadata Tech Dtypes: {de.metadata.get('technical_dtypes')}")

query = """
SELECT "Category Name", SUM("Bottles Sold") as total_garrafas
FROM data 
GROUP BY "Category Name"
LIMIT 10
"""

try:
    print("\n--- Testing Polars SQL ---")
    sub_start = time.time()
    res = de.ctx.execute(query).collect(streaming=True)
    print(f"Polars SQL Success in {time.time() - sub_start:.2f}s")
    print(res.head())
except Exception as e:
    print(f"Polars SQL Failed: {e}")

try:
    print("\n--- Testing DuckDB Direct ---")
    import duckdb
    sub_start = time.time()
    con = duckdb.connect()
    clean_path = file_path.replace("\\", "/")
    # DuckDB can read CSV direct with exact schema inference or streaming
    csv_query = f"""
    SELECT "Category Name", SUM("Bottles Sold") 
    FROM read_csv_auto('{clean_path}', types={{'Bottles Sold': 'BIGINT'}}, sample_size=100000) 
    GROUP BY 1
    LIMIT 10
    """
    res_duck = con.execute(csv_query).fetchdf()
    print(f"DuckDB Direct CSV Success in {time.time() - sub_start:.2f}s")
    print(res_duck.head())
except Exception as e:
    print(f"DuckDB Failed: {e}")
