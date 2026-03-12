import polars as pl
import os

# Create a sample CSV that might trigger this
csv_path = "test_crash.csv"
with open(csv_path, "w") as f:
    f.write("A,B\n")
    f.write("1,10\n")
    f.write("2,20\n")
    # Exceed infer_schema_length (if it was default 100)
    for i in range(200):
        f.write(f"{i},100\n")
    f.write("999,712-2\n")

print("Testing scan_csv with infer_schema_length=0...")
try:
    ldf = pl.scan_csv(csv_path, infer_schema_length=0)
    schema = ldf.collect_schema()
    print("Schema detected:", schema)
    
    # Trigger actual read
    print("Collecting...")
    df = ldf.collect()
    print("Successfully collected!")
    print(df.tail())
except Exception as e:
    print("Caught error:", e)

if os.path.exists(csv_path):
    os.remove(csv_path)
