import polars as pl

df = pl.read_csv("uploads/online_shoppers.csv")
ctx = pl.SQLContext(frames={"data": df})

query = "SELECT SUM(Revenue) AS total_vendas_semestre FROM data WHERE Month IN ('Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')"
res = ctx.execute(query).collect()
print("Resultado da agregação Polars SQL:")
print(res.to_dicts())

query2 = "SELECT SUM(Revenue) AS total_vendas_semestre FROM data"
res2 = ctx.execute(query2).collect()
print("Resultado do total geral Polars SQL:")
print(res2.to_dicts())
