# The Council v2.0 - Backend

Sistema de análise de dados com agentes AI autônomos e análises determinísticas.

---

## 🎯 Visão Geral

The Council v2.0 é um sistema multi-agente que combina:
- **LLM (Ollama)** para roteamento e explicações
- **Polars** para análises determinísticas de alta performance
- **LangGraph** para orquestração de agentes
- **FastAPI** para API REST

---

## 🚀 Quick Start

### 1. Instalar Dependências
```bash
uv sync
```

### 2. Iniciar Ollama
```bash
ollama pull qwen2.5-coder:1.5b
```

### 3. Iniciar Backend
```bash
uv run main.py
```

Servidor: `http://localhost:8000`

---

## 📊 Funcionalidades Principais

### ⭐ Análises Determinísticas (QueryEngine)
```
"Qual o total de vendas?"        → Agregação
"Vendas por categoria"           → Group By
"Mostre estatísticas"            → Describe
"Top 10 produtos"                → Top N
```

**Performance**: 50-100ms (vs 5-10s com LLM puro)

### 📚 Base de Conhecimento (LibrarianAgent)
```
"Como fazer group by no Polars?"
```

### 💬 Conversação Geral
```
"Olá, como você está?"
```

---

## 🧪 Testes

```bash
uv run test_query_engine.py    # Teste completo
uv run test_simple_query.py    # Teste rápido
uv run test_analyst_e2e.py     # End-to-end
```

---

## 📖 Documentação

- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Como usar
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Resumo técnico
- **[CHANGELOG_QUERY_ENGINE.md](CHANGELOG_QUERY_ENGINE.md)** - Mudanças

---

## 🏗️ Arquitetura

```
Frontend → FastAPI → LangGraph → Agentes
                                    ↓
                            QueryEngine (Polars)
```

**Agentes**:
- **RouterAgent**: Roteia queries
- **AnalystAgent**: Análise de dados (+ QueryEngine)
- **LibrarianAgent**: RAG com docs Polars
- **DesignerAgent**: Visualizações
- **GeneralAgent**: Conversação

---

## 📈 Performance

| Operação | QueryEngine | LLM | Melhoria |
|----------|-------------|-----|----------|
| Agregação | 50ms | 5s | **100x** |
| Group By | 100ms | 8s | **80x** |

---

**Status**: ✅ Produção  
**Versão**: 2.0.0  
**Data**: 2025-12-11
