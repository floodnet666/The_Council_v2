import time
import uuid
import json
import polars as pl
import numpy as np
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_ollama import ChatOllama

# --- CONFIGURAÇÃO ---
CHROMA_PATH = "./chroma_memory"
OLLAMA_MODEL = "deepseek-r1:1.5b" # Modelo com Thinker Desabilitado
OLLAMA_URL = "http://localhost:11434"
EMBEDDING_MODEL = 'all-MiniLM-L6-v2' 

# --- SCHEMA PARA VALIDAÇÃO (SANDBOX) ---
SCHEMA_CONTEXT = """
Variável 'lf' (LazyFrame Polars):
- produto (String)
- categoria (String)
- quantidade_vendida (Int64)
- valor_unitario (Float64)
- data_pedido (Date)
- vendas (Float64) -> qtd * valor
- ano (String)
- mes_ano (String)
- dia_semana_idx (Int32)
"""

# --- MATRIZ MASSIVA DE 200 PERGUNTAS (Base PT-BR) ---
BASE_QUESTIONS = [
    # TIER 1: VOLUME E BI (1-40)
    "Qual o faturamento total acumulado?", "Quantos itens foram vendidos no total?", "Qual o ticket médio geral?",
    "Receita total por ano?", "Média de vendas mensal?", "Dia da semana com mais vendas?",
    "Recorde de vendas em um único dia?", "Quantos pedidos únicos existem?", "Receita no último trimestre?",
    "Variação de faturamento entre primeiro e último ano?", "Quais os 5 produtos mais vendidos?",
    "Top 5 produtos em receita?", "Produtos mais caros?", "Categoria com melhor desempenho?",
    "Produtos sem vendas no mês atual?", "Share de categoria no faturamento?", "Preço médio por categoria?",
    "Produtos distintos por categoria?", "Curva ABC de faturamento?", "Total de vendas em TI?",
    "Preço médio ponderado?", "Menor valor unitário?", "Faturamento por dia da semana?",
    "Volume total por mes_ano?", "Ticket médio por ano?", "Ranking de categorias por volume?",
    "Vendas médias por dia do mês?", "Volume por ano e categoria?", "Vendas em Dezembro?",
    "Produto mais barato por categoria?", "Faturamento do top 1 produto?", "Percentual da categoria Móveis?",
    "Qtd média por pedido?", "Valor da maior transação?", "Vendas por ano-mês ordenado?",
    "Produtos com preço > 100?", "Vendas em dias úteis?", "Vendas em fins de semana?",
    "Média de itens por categoria?", "Faturamento top 10 produtos?",

    # TIER 2: TEMPORAL E MÉTRICAS (41-80)
    "Taxa de crescimento mensal (MoM)?", "Crescimento anual (YoY)?", "Média móvel de 3 meses?",
    "Meses com pior receita?", "Evolução diária no mês?", "Projeção simples próximo mês?",
    "Soma de vendas por semestre?", "Crescimento Jan vs Fev?", "Média móvel 7 dias?",
    "Vendas por trimestre?", "Comparativo Q1 vs Q2?", "Variação mensal de qtd?",
    "Produto que mais cresceu?", "Mês com maior ticket médio?", "Faturamento acumulado?",
    "Diferença vendas hoje e ontem?", "Faturamento mesmo período ano anterior?", "Média dias entre vendas?",
    "Sazonalidade mensal?", "Faturamento médio dia útil?", "Variação preço médio por categoria?",
    "Faturamento por década?", "Meses com faturamento estável?", "CAGR das vendas?",
    "Volatilidade mensal?", "Sazonalidade por categoria?", "Vendas por estação?",
    "Semana com mais vendas?", "Diferença média vs mediana?", "Ranking consistência?",
    "Vendas dia 01?", "Crescimento trimestral?", "Vendas por hora (simulado)?",
    "Produtos inativos 90 dias?", "Ticket médio Q4 vs Q1?", "Impacto Black Friday?",
    "Share de TI evolução?", "Meses acima da média?", "Dispersão vendas anual?",
    "Sazonalidade Dezembro?",

    # TIER 3: ESTATÍSTICA E DATA QUALITY (81-120)
    "Desvio padrão vendas diárias?", "Percentil 90 vendas?", "Outliers de preço (IQR)?",
    "Z-Score das vendas?", "Correlação preço e qtd?", "Resumo estatístico completo?",
    "Mediana por categoria?", "Amplitude de preço?", "Distribuição de faixas de preço?",
    "Valores nulos?", "Zeros no faturamento?", "Produtos duplicados?",
    "Skewness das vendas?", "Curtose dos preços?", "Coeficiente variação por categoria?",
    "Integridade faturamento=qtd*valor?", "Quartis de volume?", "Datas futuras?",
    "Cardinalidade categorias?", "Moda dia da semana?", "Frequência relativa categorias?",
    "Variância quantidades?", "Anomalias (>3 std)?", "Nulos por ano?",
    "Histograma faturamento?", "Dispersão faturamento produto?", "Outliers quantidade?",
    "Trimmed mean 5%?", "Média harmônica?", "Erro padrão média?",
    "Gaps temporais?", "Tipagem dados consistente?", "Categorias 1 produto?",
    "Soma vendas sem nulos?", "Vendas por SKU?", "Nome produto vs vendas?",
    "Preços negativos?", "Produtos ativos/ano?", "Ticket médio sem top 1%?",
    "Impacto outliers faturamento?",

    # TIER 4: SIMULAÇÕES E ML (121-160)
    "Regressão: Slope tendência?", "Monte Carlo: Ruído vendas?", "Forecast Naive?",
    "Probabilidade vendas > 5000?", "Cenário -20% vendas?", "Aumento 10% preço?",
    "Classe High/Med/Low?", "Matriz correlação?", "Cluster KMeans?",
    "Média móvel exponencial?", "Intervalo confiança 95%?", "Ruptura categoria TI?",
    "Elasticidade preço?", "Break-even simulado?", "Cohort análise?",
    "Retenção por mês?", "Inflação 0.5% mensal?", "Estoque 7 dias?",
    "Matriz BCG?", "Desconto progressivo?", "LTV estimado?",
    "Churn produtos?", "Pareto 80/20?", "Custo fixo vs vendas?",
    "Dados sintéticos?", "VPL fluxos?", "Monte Carlo 1000 iterações?",
    "Análise sensibilidade?", "Beta categorias?", "Crescimento logarítmico?",
    "Mudança regime?", "Impacto câmbio?", "Ruptura recorde?",
    "Estoque segurança?", "ROAS simulado?", "Otimização mix?",
    "Cenário Dobro Q4?", "Canibalização?", "Dependência fornecedor?",
    "VaR mensal?",

    # TIER 5: AVANÇADO E EDGE CASES (161-200)
    "Pivot Ano vs Categoria?", "Top produto por faturamento dentro de cada categoria?", "Faturamento por turno?",
    "Meses pares vs ímpares?", "Produtos 'Premium'?", "50% estoque produtos?",
    "Crescimento simultâneo?", "Categorias sem queda?", "Margem bruta?",
    "Ranking eficiência?", "Picos Black Friday?", "Vendas dia/semana/ano?",
    "Lançamentos < 90 dias?", "Vendas < 50 reais?", "Crescimento real?",
    "Trimestres ímpares?", "Excluir TI faturamento?", "Nomes longos vendas?",
    "Média dia do ano?", "Faturamento Q4 ranking?", "Amplitude maior/menor?",
    "Vendas recorrentes?", "Categorias acima média?", "Produtos únicos vendas?",
    "Acumulado categoria?", "Dias faturamento zero?", "Média por transação?",
    "Categorias nicho?", "Produtos inicia 'A'?", "Quantidades pares?",
    "Média móvel 12m?", "Delta Top 1 vs 2?", "Faturamento total no primeiro dia de cada mês?",
    "Vendas chuva?", "Remapeamento categoria?", "Dispersão preço/venda?",
    "Meta 10k batida?", "Turnos faturamento?", "Menor volatilidade?",
    "Soma de faturamento total formatada como moeda?"
]

class UltimateKnowledgeBuilder:
    def __init__(self):
        print(f"🧬 Iniciando Protocolo Anti-Idiota [{OLLAMA_MODEL}]")
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        
        # --- PING EMBEDDING ---
        print(f"🔍 Carregando & Testando Embeddings: {EMBEDDING_MODEL}...")
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        self.embedder.encode("ping")
        print("   ✅ Embeddings OK")
        
        self.skills_col = self.client.get_or_create_collection(
            name="polars_skills", metadata={"hnsw:space": "cosine"}
        )
        
        # Desabilita o modo de 'Pensamento' (<think>) para evitar travamentos
        self.llm = ChatOllama(
            model=OLLAMA_MODEL, 
            temperature=0.0, 
            base_url=OLLAMA_URL,
            #options={"think": False} 
        )
        
        # --- PING LLM (Com Retry e Timeout) ---
        print(f"🔍 Testando Conexão LLM [{OLLAMA_MODEL}]...")
        import concurrent.futures
        for i in range(12): # Aguarda até 60s (12 * 5s)
            def run_ping():
                return self.llm.invoke("Responda apenas 'PONG'")

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(run_ping)
                try:
                    future.result(timeout=10) # 10 Segundos de Tolerância para Resposta
                    print("   ✅ LLM OK")
                    break
                except concurrent.futures.TimeoutError:
                    print(f"   ⏳ Aguardando LLM responder (Timeout)... ({i+1}/12)")
                    time.sleep(5)
                except Exception:
                    print(f"   ⏳ Aguardando LLM responder (Erro)... ({i+1}/12)")
                    time.sleep(5)
        else:
            raise Exception(f"❌ Falha Crítica: LLM {OLLAMA_MODEL} não respondeu ao ping.")
            
        self.dummy_lf = self._generate_dummy_data()

    def _generate_dummy_data(self):
        """Sandbox para teste de execução corrigido contra ShapeError."""
        np.random.seed(42)
        dates = pl.date_range(pl.date(2023, 1, 1), pl.date(2023, 12, 31), "1d", eager=True)
        n = len(dates)
        
        prod_list = ([f"P{i}" for i in range(20)] * ((n + 20) // 20 + 1))[:n+20]
        cat_list = (["TI", "Móveis", "Alimentos", "Serviços"] * ((n + 20) // 4 + 1))[:n+20]
        
        df = pl.DataFrame({
            "produto": prod_list,
            "categoria": cat_list,
            "quantidade_vendida": np.random.randint(1, 50, n+20),
            "valor_unitario": np.random.uniform(10.0, 1000.0, n+20),
            "data_pedido": dates.append(pl.date_range(pl.date(2024,1,1), pl.date(2024,1,20), "1d", eager=True))
        }).head(n)
        
        return df.with_columns([
            (pl.col("quantidade_vendida") * pl.col("valor_unitario")).alias("vendas"),
            pl.col("data_pedido").dt.year().cast(pl.String).alias("ano"),
            pl.col("data_pedido").dt.strftime("%Y-%m").alias("mes_ano"),
            pl.col("data_pedido").dt.weekday().alias("dia_semana_idx")
        ]).lazy()

    def get_translations(self, q: str):
        """Gera variantes para robustez multilíngue com extração JSON resiliente."""
        prompt = f"Gere a versão em Inglês e Italiano desta pergunta: '{q}'. Retorne apenas JSON: {{'en': '...', 'it': '...'}}"
        try:
            res = self.llm.invoke(prompt).content
            
            # Extração resiliente de JSON de blocos de texto/markdown
            import re
            json_match = re.search(r'\{.*\}', res, re.DOTALL)
            if json_match:
                res = json_match.group(0)
                
            return json.loads(res.replace("'", '"'))
        except:
            return {"en": q, "it": q}

    def test_code(self, code: str):
        """Validação estrita de execução com Timeout de Segurança."""
        import concurrent.futures
        
        def run_exec():
            loc = {"pl": pl, "np": np, "lf": self.dummy_lf, "result": None}
            try:
                exec(code, {}, loc)
                return loc.get("result") is not None
            except:
                return False

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(run_exec)
            try:
                return future.result(timeout=5)  # 5 Segundos de Segurança
            except concurrent.futures.TimeoutError:
                print("   ⚠️ Timeout na execução do código (Possível loop infinito).")
                return False
            except Exception:
                return False

    def run(self):
        import concurrent.futures
        import time
        
        for q_pt in BASE_QUESTIONS:
            print("\n" + "="*50)
            print(f"🛠️  Codificando: {q_pt}")
            print("==========================================")
            
            # Geração de Código Sênior com Timeout
            gen_prompt = f"Gere APENAS o código Polars (variável 'result' a partir de 'lf') para responder: {q_pt}. Contexto: {SCHEMA_CONTEXT}"
            
            print(f"👉 Enviando Prompt de Geração (Resumo):\n   '{gen_prompt[:120]}...'")
            start_gen = time.time()
            
            def get_code():
                full_code = ""
                print("\n📥 [STREAMING] Resposta LLM:\n" + "-"*30)
                try:
                    for chunk in self.llm.stream(gen_prompt):
                        print(chunk.content, end="", flush=True)
                        full_code += chunk.content
                    print("\n" + "-"*30)
                    return full_code.replace("```python", "").replace("```", "").strip()
                except Exception as e:
                    print(f"\n❌ Erro no Stream: {e}")
                    raise e

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                code_future = executor.submit(get_code)
                try:
                    code = code_future.result(timeout=45)  # Timeout de 45s para Geração
                    gen_time = time.time() - start_gen
                    print(f"   ⏱️ Tempo Geração: {gen_time:.2f}s")
                    print(f"📥 Código Recebido:\n---\n{code}\n---")
                except concurrent.futures.TimeoutError:
                    print("   ⚠️ Timeout na Geração LLM para Código (45s excedidos). Pulando.")
                    continue
                except Exception as e:
                    print(f"   ❌ Erro na Geração: {e}")
                    continue
                    
            print("👉 Validando Código no Sandbox...")
            start_test = time.time()
            test_res = self.test_code(code)
            test_time = time.time() - start_test
            print(f"   ⏱️ Tempo Validação: {test_time:.2f}s")
            
            if test_res:
                print("   ✅ Sandbox: Código EXECUTOU com sucesso!")
                
                # Tradução com Timeout
                def get_trans():
                    return self.get_translations(q_pt)
                
                print("👉 Traduzindo Pergunta...")
                start_trans = time.time()
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor_trans:
                    trans_future = executor_trans.submit(get_trans)
                    try:
                        trans = trans_future.result(timeout=25) # Timeout de 25s para Tradução
                        trans_time = time.time() - start_trans
                        print(f"   ⏱️ Tempo Tradução: {trans_time:.2f}s")
                        print(f"📥 Variante EN: {trans.get('en')}\n   Variante IT: {trans.get('it')}")
                    except concurrent.futures.TimeoutError:
                        print("   ⚠️ Timeout na Tradução LLM. Usando base para variantes.")
                        trans = {"en": q_pt, "it": q_pt}
                    except Exception:
                        trans = {"en": q_pt, "it": q_pt}
                
                # Indexa o mesmo código para 3 idiomas + variantes comuns
                variants = [q_pt, trans.get('en', q_pt), trans.get('it', q_pt)]
                start_index = time.time()
                for v in variants:
                    uid = str(uuid.uuid4())
                    emb = self.embedder.encode(v).tolist()
                    self.skills_col.add(
                        documents=[code],
                        embeddings=[emb],
                        metadatas={"query": v, "verified": "true"},
                        ids=[uid]
                    )
                index_time = time.time() - start_index
                print(f"   ⏱️ Tempo Indexação ChromaDB: {index_time:.2f}s")
                print("   ✅ Indexado com sucesso!")
            else:
                print("   ❌ Sandbox: FALHA (Erro de sintaxe ou 'result' é None). Código rejeitado.")

if __name__ == "__main__":
    builder = UltimateKnowledgeBuilder()
    builder.run()
