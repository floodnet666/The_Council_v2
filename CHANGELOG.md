# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2026-05-25

### Added
- Adicionado script de teste E2E `backend/tests/test_api_e2e_gemma.py` construído para validar estritamente o `hf.co/mradermacher/gemma-4-E2B-it-uncensored-GGUF:Q8_0`. Garante que operações semânticas do Polars não sofram alucinações de Pandas.
- Adicionado teste complementar de geração visual `test_gemma_designer_chart_generation` provando que o LLM não envia bibliotecas gráficas imperativas (Matplotlib/Seaborn).

### Changed
- **Default LLM Engine**: O modelo default de todo o ecossistema mudou. `qwen2.5:1.5b` foi removido das definições base e substituído pelo `hf.co/mradermacher/gemma-4-E2B-it-uncensored-GGUF:Q8_0` (`backend/.env.example`, `backend/engines/llm_engine.py`).
- **Documentação**: `README.md`, `backend/README.md` e `backend/IMPLEMENTATION_STATUS.md` atualizados com as novas instruções de pull via ollama (`ollama run ...`).

### Fixed
- **`QueryEngine.execute_deterministic_operation`**: 
  - *Bug:* Se o LLM alucinasse `null` (None) para atributos opcionais (`limit`, `sort_descending`), o Pydantic propagava o nulo e o Polars estourava `TypeError` em `sort(descending=None)`.
  - *Fix (Zero Bloat):* Adicionados fallbacks idiomáticos nativos antes da cadeia de invocação: `descending = True if operation.sort_descending is None else operation.sort_descending`.
- **`DesignerAgent.run`**: 
  - *Fix:* Roteado para extração nativa direta e limpa do cache do Polars LazyFrame `self.data_engine.df.head(3).collect().to_dicts()`.

### Arquitetura (XP/TDD) & Zero Bloat
- **Sincronia Frontend/Backend de Gráficos**: Refatorado o grafo de estados do LangGraph (`backend/workflow/graph.py`, `state.py`). Pedidos de gráficos (intent `designer`) agora roteiam obrigatoriamente pelo `AnalystAgent` (engine matemática Polars) definindo a flag `wants_chart = True`. Após a análise estrutural, o supervisor roteia para o `DesignerAgent`. Isso injeta `visual_data` e `visual_config` na API, ativando corretamente o `<ChartRenderer />` no Frontend (React).
- **Limpeza Central (Zero Bloat)**: Removidos arquivos de logs soltos (`test_out.txt`, `full_diff.txt`, `.tsv`, `.csv` temporários). Scripts de debug e validação rápida movidos de raiz para a nova pasta utilitária `scripts/debug_tools/`.

### Adicionado (Data Profiling & BI Semântico)
- **`engines/data_engine.py`**:
  - Adicionado Profiling Semântico para colunas Categóricas e Strings (`string_profiles`) limitadas a 20 valores únicos. Isso provê à LLM a capacidade de mapear agrupamentos temporais ou lógicos não-nativos (ex: nomes de meses em texto) substituindo o uso falho de funções de datas em Strings.
- **`agents/analyst_agent.py`**:
  - Adicionado Self-Healing loop dinâmico (MAX_RETRIES=2) para interceptar o erro de exceção de parser `sqlparser-rs` do Polars e forçar a correção ANSI da query pela LLM em runtime.
  - O prompt da LLM foi ajustado com diretrizes de "CRITICAL BI LOGIC" estritas, coibindo `SUM()` em campos Boleanos, orientando o uso do `COUNT(*)` filtrado e proibindo matemática temporal baseada no `CURRENT_DATE`. Alias obrigatórios (`AS`) implementados no exemplo analítico para resolver o crash de duplicidade nativo do Polars SQL.
