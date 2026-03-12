# 📖 Guia de Uso - QueryEngine e AnalystAgent

## 🎯 Visão Geral

O **QueryEngine** permite executar análises determinísticas em DataFrames Polars sem depender de LLM para cálculos. O **AnalystAgent** usa o QueryEngine para fornecer respostas rápidas, precisas e estruturadas.

---

## 🚀 Como Usar

### 1. Queries Analíticas (Usa QueryEngine)

O sistema detecta automaticamente queries analíticas e usa o QueryEngine:

#### Agregações
```
✅ "Qual o total de valor?"
✅ "Qual a média de quantidade?"
✅ "Quantos registros existem?"
✅ "Qual o valor máximo?"
✅ "Qual o valor mínimo?"
```

**Resposta**:
```json
{
  "query_type": "aggregation",
  "operation": "sum",
  "results": {"valor_sum": 6050},
  "columns_analyzed": ["valor"]
}
+ Explicação do LLM
```

#### Group By (Agrupamentos)
```
✅ "Total por categoria"
✅ "Vendas por tipo"
✅ "Agrupar por região"
✅ "Faturamento por produto"
```

**Resposta**:
```json
{
  "query_type": "group_by",
  "group_column": "categoria",
  "results": [
    {"categoria": "A", "count": 3, "valor_sum": 1500},
    {"categoria": "B", "count": 2, "valor_sum": 800}
  ]
}
+ Explicação do LLM
```

#### Estatísticas Descritivas
```
✅ "Mostre estatísticas"
✅ "Resumo dos dados"
✅ "Describe dataset"
✅ "Overview dos dados"
```

**Resposta**:
```json
{
  "query_type": "describe",
  "row_count": 100,
  "numeric_stats": {
    "valor": {
      "mean": 756.25,
      "median": 350.0,
      "std": 703.42,
      "min": 180.0,
      "max": 2000.0
    }
  }
}
+ Explicação do LLM
```

#### Top N
```
✅ "Top 10 maiores valores"
✅ "5 menores quantidades"
✅ "Melhores produtos"
✅ "Piores vendas"
```

**Resposta**:
```json
{
  "query_type": "top_n",
  "n": 10,
  "sort_column": "valor",
  "descending": true,
  "results": [...]
}
+ Explicação do LLM
```

---

### 2. Queries Exploratórias (Usa LLM)

Queries que não são analíticas usam o comportamento original:

```
✅ "O que você pode me dizer sobre esses dados?"
✅ "Que insights você sugere?"
✅ "Como posso analisar isso?"
```

**Resposta**: Análise textual do LLM baseada no summary dos dados

---

## 🔧 Uso Programático

### Exemplo 1: Usar QueryEngine Diretamente
```python
import polars as pl
from engines.query_engine import QueryEngine

# Criar DataFrame
df = pl.DataFrame({
    "categoria": ["A", "B", "A"],
    "valor": [100, 200, 150]
}).lazy()

# Inicializar engine
engine = QueryEngine(df)

# Executar query
result = engine.execute_query("Total por categoria")

# Resultado
print(result)
# {
#   "query_type": "group_by",
#   "group_column": "categoria",
#   "results": [...]
# }
```

### Exemplo 2: Usar AnalystAgent
```python
from engines.data_engine import DataEngine
from agents.analyst_agent import AnalystAgent

# Inicializar
data_engine = DataEngine()
analyst = AnalystAgent(data_engine)

# Carregar dados
data_engine.load_data("vendas.csv")

# Fazer query
response = await analyst.run(
    message="Total de vendas por categoria",
    active_file="vendas.csv"
)

# Resposta contém:
# ANALYSIS_DATA: {json} + explicação
```

### Exemplo 3: Parsear Resposta Estruturada
```python
response = await analyst.run("Total por categoria", "vendas.csv")

if "ANALYSIS_DATA:" in response:
    parts = response.split("---")
    
    # Extrair JSON
    data_json = parts[0].replace("ANALYSIS_DATA:", "").strip()
    data = json.loads(data_json)
    
    # Extrair explicação
    explanation = parts[1].strip() if len(parts) > 1 else ""
    
    print("Dados:", data)
    print("Explicação:", explanation)
```

---

## 📊 Formato de Resposta

### Estrutura Geral
```
ANALYSIS_DATA:
{
  "query_type": "tipo_da_query",
  "timestamp": "2025-12-11T15:00:00",
  "original_query": "query original",
  ... dados específicos do tipo ...
}

---

[Explicação em linguagem natural do LLM]
1. Key Finding: [principal descoberta]
2. Details: [detalhes dos resultados]
3. Insight: [o que isso significa]
```

### Tipos de Dados por Query Type

#### aggregation
```json
{
  "query_type": "aggregation",
  "operation": "sum|mean|count|max|min",
  "results": {"coluna_operacao": valor},
  "columns_analyzed": ["col1", "col2"]
}
```

#### group_by
```json
{
  "query_type": "group_by",
  "group_column": "categoria",
  "numeric_column": "valor",
  "results": [
    {"categoria": "A", "count": 3, "valor_sum": 1500, "valor_mean": 500}
  ]
}
```

#### describe
```json
{
  "query_type": "describe",
  "row_count": 100,
  "column_count": 5,
  "columns": ["col1", "col2"],
  "dtypes": {"col1": "Int64", "col2": "String"},
  "numeric_stats": {
    "col1": {
      "mean": 100.0,
      "median": 95.0,
      "std": 15.5,
      "min": 50.0,
      "max": 200.0,
      "null_count": 0
    }
  }
}
```

#### top_n
```json
{
  "query_type": "top_n",
  "n": 10,
  "sort_column": "valor",
  "descending": true,
  "results": [
    {"categoria": "A", "valor": 2000},
    {"categoria": "B", "valor": 1500}
  ]
}
```

---

## 🎨 Palavras-Chave Detectadas

### Aggregation
- `total`, `soma`, `sum`
- `média`, `average`, `avg`
- `count`, `contar`, `quantos`
- `máximo`, `max`
- `mínimo`, `min`

### Group By
- `por categoria`, `por tipo`, `por região`
- `group by`, `agrupar por`
- `total por`, `soma por`, `média por`

### Describe
- `estatísticas`, `statistics`
- `describe`, `resumo`, `summary`
- `overview`

### Top N
- `top 10`, `top 5`
- `melhores`, `piores`
- `maiores`, `menores`
- `3 maiores`, `5 menores`

---

## ⚡ Performance

### Benchmarks
- **Agregação simples**: ~50ms
- **Group by**: ~100ms
- **Describe**: ~150ms
- **Top N**: ~80ms

### Cache
- Queries repetidas: **~1ms** (do cache)
- Cache é limpo quando DataFrame muda

---

## 🐛 Troubleshooting

### Problema: Query não detectada como analítica
**Solução**: Use palavras-chave explícitas:
```
❌ "Mostre vendas"
✅ "Total de vendas"
✅ "Vendas por categoria"
```

### Problema: Coluna errada sendo usada
**Solução**: QueryEngine usa primeira coluna numérica/categórica. Para especificar:
```python
# Futuro: suporte para especificar colunas
result = engine.execute_query(
    "Total por categoria",
    group_column="tipo",
    agg_column="valor"
)
```

### Problema: Erro "No dataframe loaded"
**Solução**: Certifique-se de carregar dados primeiro:
```python
data_engine.load_data("arquivo.csv")
analyst.run("query", active_file="arquivo.csv")
```

---

## 📚 Exemplos Práticos

### Análise de Vendas
```python
# Dataset: vendas.csv
# Colunas: data, produto, categoria, valor, quantidade

queries = [
    "Total de vendas",                    # aggregation
    "Vendas por categoria",               # group_by
    "Top 10 produtos mais vendidos",      # top_n
    "Estatísticas de vendas",             # describe
]

for query in queries:
    response = await analyst.run(query, "vendas.csv")
    print(response)
```

### Análise de Clientes
```python
# Dataset: clientes.csv
# Colunas: id, nome, idade, cidade, valor_total

queries = [
    "Quantos clientes temos?",            # aggregation (count)
    "Valor médio por cliente",            # aggregation (mean)
    "Clientes por cidade",                # group_by
    "5 maiores clientes",                 # top_n
]
```

### Análise Temporal
```python
# Dataset: vendas_mensais.csv
# Colunas: mes, ano, categoria, valor

queries = [
    "Total de vendas por mês",            # group_by
    "Média mensal de vendas",             # aggregation
    "Melhores meses de vendas",           # top_n
]
```

---

## 🔮 Recursos Futuros

### Em Desenvolvimento
- ⏳ `filter`: "Vendas onde valor > 1000"
- ⏳ `time_series`: "Tendência ao longo do tempo"
- ⏳ `correlation`: "Correlação entre preço e quantidade"

### Planejado
- 📋 Especificar colunas manualmente
- 📋 Queries SQL diretas
- 📋 Joins entre datasets
- 📋 Persistência de cache

---

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique este guia
2. Consulte `IMPLEMENTATION_SUMMARY.md`
3. Veja exemplos em `test_analyst_e2e.py`
4. Consulte código em `engines/query_engine.py`

---

**Versão**: 2.0.0  
**Última Atualização**: 2025-12-11  
**Status**: ✅ Produção
