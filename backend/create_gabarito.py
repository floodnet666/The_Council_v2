import polars as pl
import json
import os
from datetime import datetime

CSV_PATH = "uploads/Liquor_Sales.csv"

def load_data():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"Missing dataset: {CSV_PATH}")
    print(f"Loading {CSV_PATH}...")
    df = pl.scan_csv(CSV_PATH, infer_schema_length=10000, ignore_errors=True)
    
    # Cast date
    try:
        df = df.with_columns(pl.col("Date").str.strptime(pl.Date, format="%m/%d/%Y", strict=False))
    except Exception as e:
        print(f"Date cast failed, using raw string: {e}")
        
    print("Collecting into memory for caching...")
    df_collected = df.collect()
    return df_collected.lazy()

def get_answer(q_id, df):
    try:
        if q_id == 1:
            return df.select(pl.len().alias("count")).collect().to_dicts()[0]["count"]
        elif q_id == 2:
            res = df.select(pl.col("Date").min().alias("min"), pl.col("Date").max().alias("max")).collect().to_dicts()[0]
            return {"min": str(res["min"]), "max": str(res["max"])}
        elif q_id == 3:
            return df.select(pl.col("Sale (Dollars)").sum()).collect().to_dicts()[0]["Sale (Dollars)"]
        elif q_id == 4:
            return [r["Store Name"] for r in df.select("Store Name").unique().limit(5).collect().to_dicts()]
        elif q_id == 5:
            res = df.filter(pl.col("Store Number") == 2191).select("Address", "City").unique().collect().to_dicts()
            return res[0] if res else "Not Found"
        elif q_id == 6:
            return df.select(pl.col("County").n_unique()).collect().to_dicts()[0]["County"]
        elif q_id == 7:
            return df.select(pl.col("State Bottle Cost").sum()).collect().to_dicts()[0]["State Bottle Cost"]
        elif q_id == 8:
            return df.select(pl.col("Volume Sold (Liters)").sum()).collect().to_dicts()[0]["Volume Sold (Liters)"]
        elif q_id == 9:
            return df.head(5).collect().to_dicts()
        elif q_id == 10:
            res = df.select(pl.col("Item Description").value_counts(sort=True).limit(1)).collect().to_dicts()
            return res[0]["Item Description"] if res else "None"
        elif q_id == 11:
            return df.filter(pl.col("Category Name").str.contains("(?i)vodka")).select(pl.col("Bottles Sold").sum()).collect().to_dicts()[0]["Bottles Sold"]
        elif q_id == 12:
            return df.filter(pl.col("City").str.to_uppercase() == "DES MOINES").select(pl.len()).collect().to_dicts()[0]["len"]
        elif q_id == 13:
            return df.select(pl.col("Bottle Volume (ml)").mean()).collect().to_dicts()[0]["Bottle Volume (ml)"]
        elif q_id == 14:
            return df.filter((pl.col("Store Name").str.contains("(?i)hy-vee")) & (pl.col("City").str.to_uppercase() == "WATERLOO")).select(pl.len()).collect().to_dicts()[0]["len"]
        elif q_id == 15:
            res = df.filter(pl.col("Vendor Number") == 260).select("Vendor Name").unique().collect().to_dicts()
            return res[0]["Vendor Name"] if res else "Not Found"
            
        # Nível 2
        elif q_id == 16:
            return df.group_by("City").agg(pl.col("Sale (Dollars)").sum().alias("total")).sort("total", descending=True).limit(10).collect().to_dicts()
        elif q_id == 17:
            res = df.group_by("Vendor Name").agg(pl.col("Bottles Sold").sum().alias("total")).sort("total", descending=True).limit(1).collect().to_dicts()
            return res[0]["Vendor Name"] if res else "None"
        elif q_id == 18:
            res = df.group_by("Store Name").agg(pl.col("Volume Sold (Gallons)").sum().alias("total")).sort("total", descending=True).limit(1).collect().to_dicts()
            return res[0]["Store Name"] if res else "None"
        elif q_id == 19:
            return df.group_by("Category Name").agg(pl.col("Sale (Dollars)").sum()).sort("Sale (Dollars)", descending=True).limit(5).collect().to_dicts()
        elif q_id == 20:
            res = df.group_by("County").agg(pl.col("State Bottle Retail").mean()).sort("State Bottle Retail", descending=True).limit(1).collect().to_dicts()
            return res[0]["County"] if res else "None"
        elif q_id == 21:
            res = df.select(pl.col("Date").dt.strftime("%Y-%m").alias("month")).group_by("month").agg(pl.len().alias("count")).sort("count", descending=True).limit(1).collect().to_dicts()
            return res[0]["month"] if res else "None"
        elif q_id == 22:
            return df.filter(pl.col("Bottle Volume (ml)") > 1000).group_by("City").agg(pl.col("Volume Sold (Liters)").sum()).limit(100).collect().to_dicts()
        elif q_id == 23:
            return df.group_by("Store Name").agg(((pl.col("State Bottle Retail") - pl.col("State Bottle Cost")) * pl.col("Bottles Sold")).sum().alias("profit")).sort("profit", descending=True).limit(3).collect().to_dicts()
        elif q_id == 24:
            res = df.group_by("City").agg(pl.col("Sale (Dollars)").mean().alias("mean_sale")).sort("mean_sale", descending=False).limit(1).collect().to_dicts()
            return res[0]["City"] if res else "None"
        elif q_id == 25:
            # Requires Date cast success
            return df.select(pl.col("Date").dt.weekday().alias("weekday")).group_by("weekday").agg(pl.len()).sort("weekday").collect().to_dicts()
        elif q_id == 26:
            dt_cutoff = datetime.strptime("2015-01-01", "%Y-%m-%d")
            return df.filter(pl.col("Date") > pl.lit(dt_cutoff).cast(pl.Date)).group_by("Category Name").agg(pl.col("Bottles Sold").sum()).collect().to_dicts()
        elif q_id == 27:
            return df.group_by("Vendor Name").agg(pl.col("Item Number").n_unique().alias("unique_items")).sort("unique_items", descending=True).limit(1).collect().to_dicts()[0]["Vendor Name"]
        elif q_id == 28:
            vodka = df.filter(pl.col("Category Name").str.contains("(?i)vodka")).select(pl.col("Sale (Dollars)").sum()).collect().to_dicts()[0]["Sale (Dollars)"]
            whiskey = df.filter(pl.col("Category Name").str.contains("(?i)whiskey|whisky")).select(pl.col("Sale (Dollars)").sum()).collect().to_dicts()[0]["Sale (Dollars)"]
            return "Vodka" if vodka > whiskey else "Whiskey"
        elif q_id == 29:
            total = df.select(pl.col("Sale (Dollars)").sum()).collect().to_dicts()[0]["Sale (Dollars)"]
            dm = df.filter(pl.col("City").str.to_uppercase() == "DES MOINES").select(pl.col("Sale (Dollars)").sum()).collect().to_dicts()[0]["Sale (Dollars)"]
            return (dm / total) * 100 if total else 0
        elif q_id == 30:
            return df.filter(pl.col("Bottles Sold") > 1000).select(pl.len()).collect().to_dicts()[0]["len"] > 0
        elif q_id == 31:
            res = df.select(pl.col("Sale (Dollars)").mean().alias("mean"), pl.col("Sale (Dollars)").min().alias("min"), pl.col("Sale (Dollars)").max().alias("max")).collect().to_dicts()[0]
            return res
        elif q_id == 32:
            return df.select((pl.col("State Bottle Retail") - pl.col("State Bottle Cost")).abs().mean()).collect().to_dicts()[0]["State Bottle Retail"]
        elif q_id == 33:
            res = df.filter(pl.col("City").str.to_uppercase() == "CEDAR RAPIDS").group_by("Item Description").agg(pl.col("Bottles Sold").sum().alias("total")).sort("total", descending=True).limit(1).collect().to_dicts()
            return res[0]["Item Description"] if res else "None"
        elif q_id == 34:
             return df.group_by("Store Name").agg(pl.col("Store Number").n_unique().alias("unique_stores")).sort("unique_stores", descending=True).limit(5).collect().to_dicts()
        elif q_id == 35:
             res = df.select(pl.col("Date").dt.strftime("%Y-%m").alias("month"), pl.col("Volume Sold (Liters)")).group_by("month").agg(pl.col("Volume Sold (Liters)").sum().alias("total")).sort("total", descending=True).limit(1).collect().to_dicts()
             return res[0]["month"] if res else "None"

        # Nível 3 & Gráficos
        elif q_id == 36:
            m1 = df.filter((pl.col("Date") >= pl.lit(datetime(2015,1,1)).cast(pl.Date)) & (pl.col("Date") <= pl.lit(datetime(2015,6,30)).cast(pl.Date))).select(pl.col("Sale (Dollars)").sum()).collect().to_dicts()[0]["Sale (Dollars)"]
            m2 = df.filter((pl.col("Date") >= pl.lit(datetime(2015,7,1)).cast(pl.Date)) & (pl.col("Date") <= pl.lit(datetime(2015,12,31)).cast(pl.Date))).select(pl.col("Sale (Dollars)").sum()).collect().to_dicts()[0]["Sale (Dollars)"]
            return {"1st_half": m1, "2nd_half": m2, "variation": (m2 - m1) / m1 if m1 else 0}
        elif q_id == 37:
            profit = (pl.col("State Bottle Retail") - pl.col("State Bottle Cost")) * pl.col("Bottles Sold")
            return df.group_by("Vendor Name").agg(profit.sum().alias("profit"), pl.col("Volume Sold (Liters)").sum().alias("liters")).filter(pl.col("liters") > 0).select("Vendor Name", (pl.col("profit")/pl.col("liters")).alias("ratio")).sort("ratio", descending=True).limit(3).collect().to_dicts()
        elif q_id == 38:
            return df.filter((pl.col("City").str.to_uppercase() == "DES MOINES") & (pl.col("Date").dt.year() == 2012)).select(pl.col("Date").dt.strftime("%Y-%m").alias("month"), "State Bottle Retail").group_by("month").agg(pl.col("State Bottle Retail").mean()).sort("month").collect().to_dicts()
        elif q_id == 39:
            q95 = df.select(pl.col("Sale (Dollars)").quantile(0.95)).collect().to_dicts()[0]["Sale (Dollars)"]
            return df.filter(pl.col("Sale (Dollars)") > q95).group_by(["County", "City"]).agg(pl.len().alias("outliers")).sort("outliers", descending=True).limit(5).collect().to_dicts()
        elif q_id == 40:
             # Correlação Pearson
             return df.select(pl.corr("State Bottle Cost", "Bottles Sold")).collect().to_dicts()[0]["State Bottle Cost"]
        elif q_id == 41:
             return df.group_by("Category Name").agg(pl.col("Sale (Dollars)").sum()).filter(pl.col("Sale (Dollars)") > 0).sort("Sale (Dollars)").limit(5).collect().to_dicts()
        elif q_id == 42:
             # Verifica discrepancia
             res = df.limit(10).select((pl.col("Bottle Volume (ml)") * pl.col("Bottles Sold") / 1000).alias("calc"), pl.col("Volume Sold (Liters)")).collect().to_dicts()
             return all(abs(r["calc"] - r["Volume Sold (Liters)"]) < 0.1 for r in res)
        elif q_id == 43:
             # 2 meses piores vendas médias históricas
             return df.select(pl.col("Date").dt.strftime("%B").alias("month"), "Sale (Dollars)").group_by("month").agg(pl.col("Sale (Dollars)").sum()).sort("Sale (Dollars)").limit(2).collect().to_dicts()
        elif q_id == 44:
             total = df.select(pl.col("Sale (Dollars)").sum()).collect().to_dicts()[0]["Sale (Dollars)"]
             top_store = df.group_by("Store Name").agg(pl.col("Sale (Dollars)").sum()).sort("Sale (Dollars)", descending=True).limit(1).collect().to_dicts()[0]
             return {"Store": top_store["Store Name"], "Share": (top_store["Sale (Dollars)"] / total) * 100}
        elif q_id == 45:
             # Simplesmente agregados mensais
             return df.select(pl.col("Date").dt.strftime("%Y-%m").alias("month"), "Sale (Dollars)").group_by("month").agg(pl.col("Sale (Dollars)").sum()).sort("month").collect().to_dicts()
        elif q_id == 46 or q_id == 50:
            return df.group_by("City" if q_id==46 else "Category Name").agg(pl.col("Bottles Sold").sum()).sort("Bottles Sold", descending=True).limit(10).collect().to_dicts()
        elif q_id == 47:
            return df.group_by("County").agg(pl.col("Sale (Dollars)").sum()).sort("Sale (Dollars)", descending=True).limit(5).collect().to_dicts()
        elif q_id == 48:
            return df.select(pl.col("Date").dt.strftime("%Y-%m").alias("month"), pl.col("Sale (Dollars)")).group_by("month").agg(pl.col("Sale (Dollars)").sum()).sort("month").collect().to_dicts()
        elif q_id == 49:
            return df.select("State Bottle Cost", "State Bottle Retail").limit(1000).collect().to_dicts()
                
    except Exception as e:
        return f"Error: {e}"
    return "Not Implemented"

def main():
    df = load_data()
    gabarito = {}
    for i in range(1, 51):
        print(f"Resolving Q{i}...")
        gabarito[str(i)] = get_answer(i, df)
        
    with open("gabarito.json", "w", encoding="utf-8") as f:
        json.dump(gabarito, f, indent=2, ensure_ascii=False, default=str)
    print("Gabarito saved to gabarito.json")

if __name__ == "__main__":
    main()
