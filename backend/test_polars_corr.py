import polars as pl

df = pl.DataFrame({
    "A": [1, 2, 3],
    "B": [4, 5, 6]
})

print("Testing pl.col('A').corr(pl.col('B')): ")
try:
    res = df.select(pl.col("A").corr(pl.col("B")))
    print("Success: ", res)
except Exception as e:
    print("Fail: ", e)

print("\nTesting pl.corr('A', 'B'): ")
try:
    res = df.select(pl.corr("A", "B"))
    print("Success: ", res)
except Exception as e:
    print("Fail: ", e)
