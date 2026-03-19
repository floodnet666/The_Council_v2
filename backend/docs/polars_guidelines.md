# 📋 Polars Structure and Best Practices for Analysis

Use this document to generate correct codes using the **Polars** library for structured analysis operations.

## 1. 🚫 Prohibited Pandas Patterns
Never use pandas-style indexing, loops or assignments.
*   **Do Not Use**: `.apply()`, `.loc`, `.iloc`, `.iterrows()`, `df['A'] = value`, `.groupby().apply()`.
*   **Do Not Use**: Row-by-row lambda functions. They are slow and trigger execution safety locks.

## 2. ✅ Proper Aggregations (Soma, Média, Contagem)
Do not use `df["Col"].sum()`. Use `.select()` with standard expressions.
```python
# Correto: Calcular Soma de uma Coluna
result = df.select(pl.col("Sale (Dollars)").sum()).collect()

# Correto: Contar Linhas totais
result = df.select(pl.len()).collect()

# Correto: Média (Average)
result = df.select(pl.col("State Bottle Cost").mean()).collect()
```

## 3. 📊 GroupBy Operações (Agrupamentos)
Group calculations must use `.agg()` with proper alias formats.
```python
# Correto: Agrupar por Cidade e somar Vendas das top 10
result = df.group_by("City").agg(
    pl.col("Sale (Dollars)").sum().alias("total_sales")
).sort("total_sales", descending=True).limit(10).collect()

# Correto: Agrupar por Mês (usando str.to_date)
result = df.with_columns(
    pl.col("Date").str.to_date("%m/%d/%Y").alias("parsed_date")
).with_columns(
    pl.col("parsed_date").dt.strftime("%Y-%m").alias("Month")
).group_by("Month").agg(
    pl.col("Sale (Dollars)").sum()
).sort("Month").collect()
```

## 4. 🧮 Criando Colunas Calculadas
Always use `.with_columns()` that processes data fully vectorized.
```python
# Correto: Multiplicar duas colunas
result = df.with_columns(
    (pl.col("Bottles Sold") * pl.col("State Bottle Cost")).alias("Total_Cost")
).collect()
```

## 5. 📅 Filtros e Datas
Apply accurate data casting patterns before filtering.
```python
# Correto: Filtrar por data específica
result = df.filter(
    pl.col("Date").str.to_date("%m/%d/%Y") > pl.date(2015, 1, 1)
).collect()
```
