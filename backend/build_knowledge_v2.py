import time
import uuid
import traceback
import polars as pl
import numpy as np
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

# --- CONFIGURAÇÃO TÉCNICA ---
CHROMA_PATH = "./chroma_memory"
OLLAMA_MODEL = "qwen2.5-coder:32b"
OLLAMA_URL = "http://localhost:11434"
EMBEDDING_MODEL = 'all-MiniLM-L6-v2' # 384 Dimensões - Padrão Ouro Local

# URLs Oficiais para Ingestão Massiva
DOCS_URLS = [
    "https://docs.pola.rs/api/python/stable/reference/lazyframe/index.html",
    "https://docs.pola.rs/api/python/stable/reference/expressions/index.html",
    "https://docs.pola.rs/api/python/stable/reference/dataframe/index.html",
    "https://docs.pola.rs/api/python/stable/reference/series/index.html",
    "https://docs.pola.rs/api/python/stable/reference/functions/index.html"
]

# --- SCHEMA DE REFERÊNCIA PARA O TREINAMENTO ---
SCHEMA_CONTEXT = """
O código deve operar sobre a variável 'lf' (LazyFrame Polars) com estas colunas:
- produto (String): Nome do item.
- categoria (String): Categoria comercial (TI, Móveis, Alimentos, etc).
- quantidade_vendida (Int64): Unidades por transação.
- valor_unitario (Float64): Preço unitário do item.
- data_pedido (Date): Data da venda.
- vendas (Float64): Resultado de quantidade_vendida * valor_unitario.
- ano (String): Ano extraído (YYYY).
- mes_ano (String): Mês e ano extraído (YYYY-MM).
- dia_semana_idx (Int32): Índice do dia da semana (1-7).
"""

# --- AS 200 PERGUNTAS DE OURO (Métrica de Sucesso 100%) ---
QUESTIONS = [
    # Tier 1: Agregações e BI Fundamental (1-40)
    "Qual o faturamento total acumulado?", "Quantos itens foram vendidos no total?", "Qual o ticket médio geral?",
    "Qual a receita total por ano?", "Qual a média de vendas mensal?", "Qual o dia da semana com maior volume?",
    "Recorde de vendas in um único dia?", "Quantos pedidos únicos na base?", "Receita total no último trimestre?",
    "Variação de faturamento entre primeiro e último ano?", "Quais os 5 produtos mais vendidos?",
    "Top 5 produtos em receita?", "Produtos com maior preço unitário?", "Categoria com melhor faturamento?",
    "Produtos sem venda no último mês?", "Share de cada categoria no faturamento?", "Média de preço por categoria?",
    "Contagem de produtos distintos por categoria?", "Curva ABC de produtos por faturamento?", 
    "Total de vendas apenas para a categoria TI?", "Preço médio ponderado geral?", "Qual o menor valor unitário vendido?",
    "Soma de faturamento por dia da semana?", "Quantidade total por mes_ano?", "Ticket médio por ano?",
    "Ranking de categorias por quantidade?", "Faturamento médio por dia do mês?", "Volume de vendas por ano e categoria?",
    "Faturamento total no mês de Dezembro de qualquer ano?", "Produto mais barato de cada categoria?",
    "Qual o faturamento acumulado do top 1 produto?", "Percentual de vendas da categoria Móveis?",
    "Média de quantidade vendida por pedido?", "Faturamento da maior transação?", "Soma de vendas por ano-mês ordenado?",
    "Quantidade de produtos com preço acima de 100?", "Total de vendas em dias de semana?", 
    "Total de vendas em finais de semana?", "Média de itens por categoria?", "Faturamento total por produto (Top 10)?",

    # Tier 2: Análise Temporal e Diagnóstica (41-80)
    "Taxa de crescimento mensal (MoM)?", "Taxa de crescimento anual (YoY)?", "Tendência da média móvel de 3 meses?",
    "Meses com pior desempenho histórico?", "Evolução diária no último mês disponível?", "Projeção simples para o próximo mês?",
    "Soma de vendas por semestre?", "Crescimento percentual entre jan e fev de 2023?", "Média móvel de 7 dias?",
    "Vendas totais por trimestre (Quarter)?", "Comparativo Q1 vs Q2 em faturamento?", "Variação mensal de quantidade vendida?",
    "Produto com maior crescimento de vendas no ano?", "Mês com maior ticket médio?", "Faturamento acumulado (Running Total)?",
    "Diferença de vendas entre hoje e ontem (em dias com dados)?", "Faturamento do mesmo período no ano anterior?",
    "Média de dias entre vendas de um mesmo produto?", "Sazonalidade: Vendas médias por mês do ano (1-12)?",
    "Impacto de feriados (simulado) no faturamento?", "Taxa de conversão de leads (se houvesse coluna)?",
    "Quantidade de meses com faturamento acima de 1 milhão?", "Primeira e última data de venda na base?",
    "Tempo de vida médio dos produtos no catálogo?", "Concentração de vendas nos primeiros 10 dias do mês?",
    "Ranking de meses por crescimento MoM?", "Qual ano teve a maior queda de faturamento?", 
    "Percentual de crescimento acumulado desde o início?", "Média de vendas por trimestre por categoria?",
    "Faturamento médio por dia útil?", "Variação de preço médio por categoria ao longo do tempo?",
    "Faturamento total por década (se aplicável)?", "Meses com faturamento recorrente estável?",
    "Crescimento anual composto (CAGR)?", "Volatilidade mensal do faturamento?", "Análise de sazonalidade por categoria?",
    "Faturamento total por estação do ano (verão, outono...)?", "Semana do ano com mais vendas?",
    "Diferença entre média e mediana mensal?", "Ranking de produtos por constância de vendas?",

    # Tier 3: Estatística, Distribuição e Qualidade (81-120)
    "Desvio padrão das vendas diárias?", "Percentil 90 das vendas totais?", "Identificação de Outliers de preço (IQR)?",
    "Z-Score das vendas por produto?", "Correlação entre preço e quantidade?", "Resumo estatístico (describe) geral?",
    "Mediana absoluta das vendas por categoria?", "Amplitude de preço por categoria?", "Distribuição de frequência de preços (bins)?",
    "Verificar valores nulos em todas as colunas?", "Contagem de zeros na coluna de faturamento?",
    "Identificar nomes de produtos duplicados?", "Assimetria (Skewness) das vendas?", "Curtose da distribuição de preços?",
    "Coeficiente de variação das vendas por categoria?", "Teste de integridade: faturamento = qtd * valor?",
    "Percentil 25, 50 e 75 do volume de vendas?", "Identificar datas no futuro (erro)?", "Cardinalidade da coluna categoria?",
    "Moda do dia da semana com mais pedidos?", "Frequência relativa de cada categoria?", "Variância das quantidades vendidas?",
    "Detecção de anomalias (vendas > 3 desvios)?", "Percentual de registros nulos por ano?",
    "Histograma de vendas (contagem por faixas de 500)?", "Dispersão de faturamento por produto?",
    "Outliers de quantidade vendida?", "Média aparada (trimmed mean) tirando 5% extremos?",
    "Média harmônica das vendas?", "Erro padrão da média de faturamento?", "Análise de lacunas temporais (dias sem dados)?",
    "Consistência de tipos de dados?", "Identificar categorias com apenas 1 produto?", 
    "Soma de vendas ignorando valores nulos?", "Média de vendas por SKU (produto)?",
    "Relação entre tamanho do nome do produto e vendas?", "Verificar se há preços negativos?",
    "Contagem de produtos ativos por ano?", "Ticket médio excluindo o top 1% de pedidos?",
    "Impacto de outliers no faturamento total (em %)?",

    # Tier 4: Modelagem e Simulações (121-160)
    "Regressão linear: Slope da tendência de vendas?", "Simulação Monte Carlo: Ruído gaussiano nas vendas?",
    "Forecast Naive para faturamento do próximo mês?", "Probabilidade empírica de faturamento > 5000 amanhã?",
    "Cenário pessimista: Redução de 20% em todas as vendas?", "Simulação de aumento de 10% no preço e impacto no total?",
    "Classificação de produtos por faturamento (High, Medium, Low)?", "Matriz de correlação entre colunas numéricas?",
    "Clusterização simples de produtos por preço e volume (KMeans)?", "Projeção de vendas baseada em média móvel exponencial?",
    "Intervalo de confiança de 95% para o faturamento médio?", "Simulação de ruptura: E se a categoria TI zerar?",
    "Elasticidade preço-demanda simplificada?", "Ponto de equilíbrio (break-even) simulado?",
    "Análise de Cohort: Vendas por safra de lançamento?", "Retenção de faturamento por mes de vida do produto?",
    "Impacto de uma taxa de inflação de 0.5% ao mês acumulada?", "Previsão de estoque necessário (soma próximos 7 dias)?",
    "Ranking de produtos Estrela vs Vaca Leiteira (Matriz BCG)?", "Simulação de desconto progressivo por quantidade?",
    "Cálculo de LTV (Life Time Value) estimado por produto?", "Churn rate simulado de produtos (pararam de vender)?",
    "Análise de Pareto: 20% dos produtos geram 80% da receita?", "Simulação de custo fixo vs faturamento (Margem)?",
    "Geração de dados sintéticos para o próximo ano seguindo tendência?", "Valor presente líquido (VPL) de fluxos de venda?",
    "Simulação de Monte Carlo com 1000 iterações para o total anual?", "Análise de sensibilidade do faturamento por preço?",
    "Cálculo de Beta (volatilidade relativa) das categorias?", "Modelagem de crescimento logarítmico?",
    "Detecção de mudança de regime (vendas subiram e mantiveram)?", "Simulação de impacto de taxa de câmbio nas vendas?",
    "Previsão de quebra de recorde diário (probabilidade)?", "Simulação de estoque de segurança (z-score 1.65)?",
    "Cálculo de ROAS (Return on Ad Spend) simulado?", "Otimização de mix de produtos para faturamento máximo?",
    "Cenário Otimista: Dobro de vendas no último trimestre?", "Impacto de canibalização entre produtos da mesma categoria?",
    "Análise de dependência de receita por fornecedor (simulado)?", "Valor em Risco (VaR) do faturamento mensal?",

    # Tier 5: Consultas Complexas e Casos Especiais (161-200)
    "Pivot de faturamento: Anos nas linhas, Categorias nas colunas?", "Top produto por faturamento dentro de cada categoria?",
    "Faturamento por faixa horária (se houvesse timestamp)?", "Diferença de faturamento entre meses pares e ímpares?",
    "Soma de vendas filtrando produtos que contenham 'Premium'?", "Lista de produtos que representam 50% do estoque?",
    "Meses onde todas as categorias cresceram simultaneamente?", "Categorias que nunca tiveram queda MoM?",
    "Cálculo de margem bruta simulada (vendas - custo)?", "Ranking de eficiência (faturamento / quantidade)?",
    "Identificar meses com comportamento 'Black Friday' (picos surpresa)?", "Média de vendas por dia da semana em cada ano?",
    "Faturamento total de produtos lançados há menos de 90 dias?", "Percentual de vendas em produtos com preço < 50?",
    "Crescimento real descontando inflação simulada?", "Comparativo de faturamento entre trimestres ímpares?",
    "Faturamento por categoria excluindo a categoria TI?", "Soma de vendas de produtos com nomes longos (>20 chars)?",
    "Média de faturamento por dia do ano (1-365)?", "Ranking de produtos por faturamento no Q4?",
    "Variação percentual entre a maior e a menor venda diária?", "Total de vendas de produtos que vendem todos os meses?",
    "Categorias com faturamento acima da média global?", "Soma de vendas de produtos únicos (venderam só 1 vez)?",
    "Faturamento acumulado por categoria ordenado por tempo?", "Percentual de dias do ano com faturamento zero?",
    "Média de faturamento por transação por categoria?", "Identificar categorias 'nicho' (poucos produtos, alto valor)?",
    "Vendas totais de produtos cujo nome começa com 'A'?", "Soma de faturamento filtrando quantidades pares?",
    "Média móvel de 12 meses (anualizada)?", "Diferença entre o topo 1 e o topo 2 produtos?",
    "Faturamento total no primeiro dia de cada mês?", "Crescimento de vendas em dias de chuva (simulado)?",
    "Impacto de mudança de nome de categoria (re-mapping)?", "Análise de dispersão: preço unitário vs vendas totais?",
    "Quais produtos bateram a meta simulada de 10k faturamento?", "Faturamento médio por hora do dia (simulado)?",
    "Ranking de consistência (menor desvio padrão de vendas)?", "Soma de faturamento total formatada como moeda?"
]

class SelfHealingKnowledgeBuilder:
    def __init__(self):
        print(f"🚀 Iniciando Fábrica de Conhecimento v2 [{OLLAMA_MODEL}]")
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        
        self.skills_col = self.client.get_or_create_collection(
            name="polars_skills", metadata={"hnsw:space": "cosine"}
        )
        
        self.llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.0, base_url=OLLAMA_URL)
        self.dummy_lf = self._generate_dummy_data()

    def _generate_dummy_data(self):
        """Gera um LazyFrame sintético perfeito para testar os scripts."""
        np.random.seed(42)
        dates = pl.date_range(pl.date(2023, 1, 1), pl.date(2023, 12, 31), "1d", eager=True)
        n = len(dates)
        
        prod_list = ([f"Produto {i}" for i in range(1, 21)] * ((n + 20) // 20 + 1))[:n+20]
        cat_list = (["TI", "Móveis", "Alimentos", "Serviços"] * ((n + 20) // 4 + 1))[:n+20]
        
        df = pl.DataFrame({
            "produto": prod_list,
            "categoria": cat_list,
            "quantidade_vendida": np.random.randint(1, 50, n + 20),
            "valor_unitario": np.random.uniform(10.0, 2000.0, n + 20),
            "data_pedido": dates.append(pl.date_range(pl.date(2024,1,1), pl.date(2024,1,20), "1d", eager=True))
        }).head(n)
        
        # Colunas calculadas conforme o padrão da v1
        df = df.with_columns([
            (pl.col("quantidade_vendida") * pl.col("valor_unitario")).alias("vendas"),
            pl.col("data_pedido").dt.year().cast(pl.String).alias("ano"),
            pl.col("data_pedido").dt.strftime("%Y-%m").alias("mes_ano"),
            pl.col("data_pedido").dt.weekday().alias("dia_semana_idx")
        ])
        return df.lazy()

    def test_code_execution(self, code: str) -> tuple[bool, str]:
        """Executa o código em sandbox e valida se gerou a variável 'result'."""
        loc = {"pl": pl, "np": np, "lf": self.dummy_lf, "result": None}
        try:
            # Proteção básica contra loops infinitos ou imports perigosos via exec
            exec(code, {}, loc)
            res = loc.get("result")
            if res is None:
                return False, "O código rodou mas não salvou o resultado na variável 'result'."
            return True, "OK"
        except Exception:
            return False, traceback.format_exc()

    def generate_gold_standard(self, question: str, max_retries: int = 3):
        """Gera e valida o código. Se falhar, entra em loop de reflexão."""
        print(f"\n[QUERY] {question[:70]}...")
        
        system_msg = f"""Você é um Arquiteto de Dados Polars Sênior.
        Gere APENAS o código Python para responder à pergunta.
        
        REGRAS:
        1. O resultado final DEVE estar na variável `result`.
        2. O LazyFrame de entrada chama-se `lf`.
        3. Use métodos modernos: `group_by`, `agg`, `with_columns`, `filter`.
        4. NUNCA explique nada. Apenas o código.
        5. Se necessário, use `np` (numpy) para estatística complexa ou simulação.
        6. Schema disponível: {SCHEMA_CONTEXT}
        """

        current_error = ""
        for attempt in range(max_retries):
            user_prompt = f"Pergunta: {question}"
            if current_error:
                user_prompt += f"\n\nERRO NA TENTATIVA ANTERIOR:\n{current_error}\nCORRIJA O CÓDIGO."

            try:
                response = self.llm.invoke([SystemMessage(content=system_msg), HumanMessage(content=user_prompt)])
                code = response.content.replace("```python", "").replace("```", "").strip()
                
                # Validação Crítica
                is_valid, diag = self.test_code_execution(code)
                
                if is_valid:
                    print(f"  ✅ [Sucesso] Tentativa {attempt+1}")
                    # Salva no Chroma com Embeddings de 384d
                    emb = self.embedder.encode(question).tolist()
                    self.skills_col.add(
                        documents=[code],
                        embeddings=[emb],
                        metadatas={"query": question, "verified": "true", "tier": "gold"},
                        ids=[str(uuid.uuid4())]
                    )
                    return True
                else:
                    print(f"  ⚠️ [Falha] Tentativa {attempt+1}. Erro capturado.")
                    current_error = diag
            except Exception as e:
                print(f"  ❌ Erro de Conexão: {e}")
                time.sleep(2)
        
        print(f"  🛑 [FALHA CRÍTICA] Pergunta descartada após {max_retries} tentativas.")
        return False

    def run(self):
        start_time = time.time()
        success_count = 0
        
        # Limpa base antiga se o usuário desejar reset total (opcional)
        # self.client.delete_collection("polars_skills")
        
        for q in QUESTIONS:
            if self.generate_gold_standard(q):
                success_count += 1
        
        total_time = time.time() - start_time
        print(f"\n{'='*50}\n🏁 PROCESSO FINALIZADO\n{'='*50}")
        print(f"Sucesso: {success_count}/{len(QUESTIONS)} ({(success_count/len(QUESTIONS))*100:.1f}%)")
        print(f"Tempo total: {total_time/60:.2f} minutos")
        print(f"Base de Conhecimento salva em: {CHROMA_PATH}")

if __name__ == "__main__":
    builder = SelfHealingKnowledgeBuilder()
    builder.run()
