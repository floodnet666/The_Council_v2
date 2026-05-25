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
  - *Bug:* Acionava método não-existente na QueryEngine (`execute_query`) para reter contexto local para RAG.
  - *Fix:* Roteado para extração nativa direta e limpa do cache do Polars LazyFrame `self.data_engine.df.head(3).collect().to_dicts()`.
