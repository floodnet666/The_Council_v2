import polars as pl
import io

csv_data = """id,zip,val
1,12345,10.5
2,123-4,20.0
"""

# Test with infer_schema_length=0
try:
    df = pl.read_csv(io.StringIO(csv_data).read().encode(), infer_schema_length=0)
    print("Schema with 0:", df.schema)
except Exception as e:
    print("Error with 0:", e)

# Test scan_csv
with open("test_infer.csv", "w") as f:
    f.write(csv_data)

try:
    ldf = pl.scan_csv("test_infer.csv", infer_schema_length=0)
    print("Scan Schema with 0:", ldf.collect_schema())
except Exception as e:
    print("Scan Error with 0:", e)
