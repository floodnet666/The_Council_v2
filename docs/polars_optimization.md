# Otimização de Performance no Polars (Large Datasets)

Para lidar com arquivos massivos (ex: 4.7GB+ como `Liquor_Sales.csv`), o Polars oferece uma arquitetura **LazyFrame** que otimiza o plano de execução (Query Planner). Contudo, certas operações podem saturar a memória física se não configuradas corretamente.

## 🚀 1. Streaming Mode (`streaming=True`)

Ao invocar o método `.collect()`, o Polars tenta carregar todo o resultado calculado na memória de uma vez. Para agregações (`group_by`) e junções (`joins`) em tabelas gigantes, o ideal é usar:

```python
# Streaming processa os dados em batches/shards, evitando pico de consumo de RAM
resultado = lazy_df.group_by("coluna").agg(pl.len()).collect(streaming=True)
```

**Benefícios:**
- Evita estouro de RAM (OOM) e congelamento por *Memory Swapping* (Paginação).
- Permite que operações paralelas rodem sem saturar a Thread Pool de IO.

---

## 🔍 2. Projection & Selection Pushdown (Automático)

O Polars empurra filtros (`.filter()`) e seleções (`.select()`) para o início da leitura do arquivo. 
**Regra de Ouro:** Nunca chame `.collect()` antes de aplicar filtros. Faça toda a cadeia de operações no `LazyFrame` antes de materializar.

---

## ⏱️ 3. Timeout de Segurança no Backend

Para evitar que consultas extremamente lentas (ex: múltiplos `strptime` em loops) deixem a thread travada consumindo CPU:
- Envolver chamadas assíncronas no FastAPI com `asyncio.wait_for(..., timeout=35.0)`.
- Isso liberta o endpoint da API para responder ao cliente num tempo determinístico, evitando o acúmulo de requisições travadas em concorrência.
