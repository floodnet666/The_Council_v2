# Technical Architecture: The Council 2.0

## Philosophy: "Semantic Orchestra, Deterministic Execution"

The Council 2.0 avoids the overhead of traditional LLM "chaining" by utilizing **LangGraph** to build a cyclic, stateful multi-agent system. While LLMs handle reasoning and coordination, the actual data transformations are delegated to **Polars**, ensuring 100x speedups compared to pure-LLM data processing.

## 1. Multi-Agent Ecosystem

Each agent is a specialized "Councilor" with a specific cognitive role:

| Agent | Responsibility | Recommended Model |
| :--- | :--- | :--- |
| **Router** | Detects intent, language, and dataset relevance. | 1.5B (Fast) |
| **Analyst** | Generates Polars expressions/SQL for data analysis. | 14B-32B (Reasoning) |
| **Designer** | Translates insights into Plotly visualization schemas. | 7B (Precise) |
| **Librarian** | Retrieval Augmented Generation (RAG) for Polars/Project context. | 1.5B-7B |
| **Reporting** | Generates executive summaries and session reports. | 1.5B-7B |

## 2. Core Engines

### Data Engine (Polars)
- **Lazy Execution**: Operations are queued and optimized by Polars before execution.
- **Static Global Cache**: Uses singleton lazy frame references to avoid reloading 3GB+ files across isolated sessions.
- **SQLContext**: Allows Analyst Agent to interact with data using familiar SQL syntax, compiled into high-speed Rust-based Polars code.
- **Sandboxed Execution**: Runs Python code aggregates with `.execute_python()` securely limits safety setups benchmarks dynamically securely.

### Memory Engine (Faiss RAG)
- **Fast Similarity Search**: Replaces standard vector DBs with low-latency Faiss indices.
- **No-Reindex Principle**: Loads existing pre-computed knowledge bases instantly (< 50ms).

### Visualization Engine (Plotly)
- **High-Fidelity Graphs**: Generates interactive charts tailored for the "Dark-Data" theme.

## 3. Workflow Flow

1. **Input**: User asks a natural language question.
2. **Routing**: Router determines if the query is a greeting, a data request, a document search, or sub-reports.
3. **Execution**:
   - If data: Analyst generates query → Data Engine executes → Results returned.
   - If viz: Designer generates chart spec → Visualization Engine renders.
   - If reporting: ReportingAgent generates executive summaries layout aggregating sets.
4. **Synthesis**: Results are combined into a coherent, multi-lingual response.

## 4. State Management

The system state is maintained via a global `CouncilState` object:
- `messages`: Conversation history.
- `queries`: Generated Polars/SQL code.
- `results`: Raw and summarized data.
- `charts`: Rendered visualization configurations.
- `language`: Detected user language (PT-BR, EN, IT).
