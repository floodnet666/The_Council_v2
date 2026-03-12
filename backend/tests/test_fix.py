import polars as pl
import os
from engines.data_engine import DataEngine

def test_zip_code_crash():
    # Create a simulated confusing CSV
    csv_path = "confusing_zips.csv"
    with open(csv_path, "w") as f:
        f.write("Store Name,Zip Code,Amount\n")
        f.write("Store A,90210,100.50\n")
        f.write("Store B,90211,200.75\n")
        # Line 1001 (exceeding initial infer_schema_length)
        for i in range(1000):
            f.write(f"Store {i},10000,50.0\n")
        f.write("Store C,712-2,300.25\n") # This would cause i64 crash if inferred early
    
    engine = DataEngine()
    success = engine.load_data(csv_path)
    
    if success:
        print("Successfully loaded data without crashing!")
        print("Metadata:", engine.metadata)
        # Verify Zip Code is String
        schema = engine.df.collect_schema()
        print(f"Zip Code Type: {schema['Zip Code']}")
    else:
        print("Failed to load data.")
    
    # Clean up
    if os.path.exists(csv_path):
        os.remove(csv_path)

if __name__ == "__main__":
    test_zip_code_crash()
