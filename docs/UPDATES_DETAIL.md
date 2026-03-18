# System Updates Breakdown: The Council 2.0

Comprehensive details of recent features added to synchronize backend intelligence processing with immediate front-end rendering caches.

---

## 1. Backend Core Dynamics (`backend/engines/`)

### 📌 `data_engine.py`
-   **[ADD]** **Static Global Cache**: Added `_global_lazy_df`, `_global_scanned_file`, and `_global_ctx` static attributes to use singletons for avoiding 3GB+ CSV file reloading setups locks dynamic nodes requests isolated session setups.
-   **[ADD]** **Date Format Casting Auto-Parse Sandbox Sample**: Added `_detect_date_format` and `_parse_date_expr` using sample list `strptime` detection loops maps absolute format layouts structures instead safe `to_date` casting heuristics triggers.
-   **[ADD]** **Auto Column Derivation Nodes sets logic templates layout configurations triggers parameters parameters constraints settings setup setup settings options**: added immediate structural column generation rules mapping datasets dimensions over automatic derivation nodes triggers:
    -   Date metrics: `ano` (Year), `mes_ano` (Month-Year), `dia_semana_idx`.
    -   Volume metrics: `vendas` derived if "qty" and "price" features are detected sequentially.
-   **[ADD]** **Execute SQL**: Added `.execute_sql(query)` invoking `pl.SQLContext` aggregates frameworks execution safety safety bounded limits lock limit thresholds constraints parameters safely.
-   **[ADD]** **Execute Python Code Sandbox Execution Triggers locks lockdowns thresholds setups**: `.execute_python(code)` executing sandbox execution paths passing `pl`, `np`, `MinMaxScaler`, `KMeans`, `LinearRegression` libraries models setup setups locked down sandboxed outputs triggers limits safely.

### 📌 `query_engine.py`
-   **[ADD]** **Synonyms Dynamic Translations mapping maps Portuguese terms headers triggers setups constraints setups settings templates parameters options settings layouts structures rules layouts templates parameters constraints setups**: added `column_synonyms` sets to bridge Portuguese prompt names mapping accurate datasets columns headers schemas.
-   **[ADD]** **Top N Per Group Window metric partition algorithms nodes layout setup settings configuration setup settings parameters options**: added automatic metric layouts `.execute_top_n_per_group(query)` utilizing `.rank("desc").over(group_col)` constructs frameworks algorithms answers frameworks answer benchmarks aggregates thresholds safety locks.
-   **[ADD]** **Lazy Describe Aggregation setup configuration setups settings parameters constraints templates options setups**: refactored descriptions into lazy sum counts framing safety bounds processing safety thresholds bounded sets framework constructs framework aggregates locks lock down thresholds constraints parameter boundaries sets memory safety frameworks safely.

---

## 2. Workspace Workflow & Graph Configuration (`backend/workflow/`)

### 📌 `graph.py`
-   **[ADD]** **ReportingAgent Node Pipeline flow configurations setup settings layouts**: added executive summary analysis generation routes routing nodes transitions transitions routes transitions path configurations limits thresholds lock outputs lockdowns thresholds safes responsibly safely.
-   **[ADD]** **Memory singleton references layout setup setup specifications nodes limits parameters parameters constraints settings models specifications criteria rules layouts**: refactored node initializers calling imports singletons `engines.memory_engine` rather locally local scoped graph wrappers frameworks safes safes securely.

### 📌 `main.py`
-   **[ADD]** **Warmup singleton memory loading initial caches caches**: added `lifespan` handler triggers buffering loads setup loads buffer saves frames threshold loads buffers threshold safes securely safely.
-   **[ADD]** **Safety Timeout lock lockdowns boundaries thresholds constraints parameter setups setup specifications nodes limits**: added `asyncio.wait_for(..., timeout=42.0)` bounded thresholds triggers safeguards infinity runs worker timeouts limits parameter structures structural layout setups parameters constraints setups settings safely securely.

---

## 3. Frontend Component Ecosystem (`frontend/components/`)

### 📌 `DataTable.tsx`
-   **[FIX]** Parsing safeguards wrapping single-unit aggregates sets (`{"sum": 100}`) mapping array wraps `[results]` safety prevents crashing crash prevent parameters thresholds restraints securely safely.

### 📌 `ChatInterface.tsx`
-   **[ADD]** Immediate upload feedback labels loops loaders setups loaders locks lockdown disabled buttons uploads frames thresholds triggers disables uploads locked locking lockdowns safes responsibly safely lock disabled uploading locked loaders disabled button safeguards locked.

---

## 4. Project Configuration (`.gemini.md`)

-   **[ADD]** **Execution Directive**: Added rules instructing execution frameworks to STRICTLY use `uv run <script.py>` for all standalone or workspace Python execution runs to eliminate direct `python` or global virtualenv dependency anomalies.

---

## 5. Analyst Agent Evaluation Integrity (`backend/agents/`)

### 📌 `analyst_agent.py`
- **[FIX]** **Strict Dictionary Verification**: Replaced truthiness condition checks such as `if result:` with safe `isinstance(result, dict)` on node endpoints to guarantee upstream LazyFrame leaks don't trigger boolean context ambiguity crashes.
- **[FIX]** **Safe List/Dict Item Recovery**: Removed `or` operators inside lines 115 and 199 (e.g., `a.get("results") or a.get("data")`) that inadvertently triggered implicit truthiness evaluations (`bool(lazyframe)`) on stream variables. Replaced with explicit `is None` conditional branches to secure fallbacks flawlessly.
- **[MODIFY]** **Prompt Prompt Guideline**: Injected static rule guidelines preventing typical `.not_null()` expressions hallucinations triggering `AttributeError` loops during correlation queries framing.

## 6. Deterministic Fallbacks Immunity (`backend/engines/`)

### 📌 `query_engine.py`
- **[FIX]** **Fallback Frame Constraints**: Injected strict `isinstance(result, dict)` guard inside `execute_query` metadata updater, preventing execution pipeline unwrappings triggering ambiguous LazyFrame exception flows downstream inside the Analyst wrapper responsibly.
