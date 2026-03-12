# The Council 2.0 - Code Index

## 📁 Root
- `README.md`: Project overview and quick start.
- `ARCHITECTURE.md`: Deep dive into system design and agent flows.
- `prd_content.md`: Original product requirements document.

## 📁 backend/
The engine room of the system.

### `agents/`
- `router_agent.py`: Initial intent classification.
- `analyst_agent.py`: Data reasoning and query generation.
- `designer_agent.py`: Chart specification generation.
- `librarian_agent.py`: RAG and documentation retrieval.

### `engines/`
- `data_engine.py`: Polars integration and dataset management.
- `query_engine.py`: SQL-to-Polars execution logic.
- `memory_engine.py`: Faiss vector storage and search.
- `visualization_engine.py`: Plotly chart generation.

### `workflow/`
- `graph.py`: LangGraph definition (Nodes and Edges).
- `state.py`: Global state schema definition.

## 📁 frontend/
Next.js web application.

### `app/`
- `page.tsx`: Main chat interface and layout.
- `globals.css`: Dark-Data theme styling.

### `components/`
- `ChatInterface.tsx`: Real-time interaction component.
- `ChartRenderer.tsx`: Plotly wrapper for dynamic charts.
- `DataTable.tsx`: Virtualized grid for fast data browsing.
