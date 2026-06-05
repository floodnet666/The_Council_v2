import asyncio
import time
import polars as pl
from langchain_ollama import ChatOllama
import json

async def run_test_a():
    print("=== INICIANDO TESTE A: MOTOR DETERMINÍSTICO + CÉTICO LLM ===")
    start_time = time.time()
    
    # 1. Pipeline Analítico Determinístico (Polars)
    print("[Polars] Carregando dados e calculando estatísticas descritivas (Contornos/Correlações)...")
    t_polars = time.time()
    df = pl.scan_csv("uploads/vendas_complexas_100k.csv").with_columns(
        (pl.col("valor_bruto") - pl.col("valor_desconto") - pl.col("valor_frete")).alias("lucro_estimado")
    )
    
    # Extrair Métricas Pesadas sem a LLM alucinar
    stats = df.select([
        pl.col("valor_bruto").mean().alias("media_vendas"),
        pl.col("valor_bruto").max().alias("max_vendas"),
        pl.col("valor_desconto").mean().alias("media_desconto"),
        pl.col("lucro_estimado").mean().alias("media_lucro"),
    ]).collect()
    
    # Simulação rápida de correlação no Polars:
    corr_df = df.select(["valor_bruto", "valor_desconto", "lucro_estimado"]).collect()
    corr_vendas_lucro = corr_df.select(pl.corr("valor_bruto", "lucro_estimado")).item()
    corr_desconto_lucro = corr_df.select(pl.corr("valor_desconto", "lucro_estimado")).item()
    
    dossie_estatistico = {
        "estatisticas_basicas": stats.to_dicts()[0],
        "correlacoes_exatas": {
            "vendas_vs_lucro": corr_vendas_lucro,
            "desconto_vs_lucro": corr_desconto_lucro
        }
    }
    
    print(f"[Polars] Concluído em {time.time() - t_polars:.2f}s")
    print(f"Dossiê Numérico Gerado: {json.dumps(dossie_estatistico, indent=2)}")
    
    # 2. Pipeline de Raciocínio Causal (LLM Sênior)
    print("\n[LLM] Injetando Dossiê no Prompt de Causalidade...")
    prompt = f"""
    Você é um Arquiteto de BI Sênior. 
    Abaixo estão os fatos matemáticos puros extraídos de 100.000 linhas de vendas:
    {json.dumps(dossie_estatistico, indent=2)}
    
    A tarefa:
    Existe um nexo de causalidade entre as variáveis? A correlação aponta que vender mais (dar mais desconto) gera lucro, ou estamos destruindo margem?
    Brinque de "Advogado do Diabo". Aponte hipóteses causais e avise sobre falsas correlações. Mantenha a resposta concisa.
    """
    
    llm = ChatOllama(model="hf.co/mradermacher/gemma-4-E2B-it-uncensored-GGUF:Q8_0", temperature=0.1)
    
    t_llm = time.time()
    try:
        response = await asyncio.wait_for(llm.ainvoke(prompt), timeout=120)
        output = response.content
    except Exception as e:
        output = f"Erro/Timeout na LLM: {e}"
        
    print(f"[LLM] Resposta gerada em {time.time() - t_llm:.2f}s")
    res = f"=== RESUMO (TESTE A) ===\n{output}\n\n[METRICAS A] Tempo Total: {time.time() - start_time:.2f}s"
    print("Writing to results_a.txt...")
    with open("results_a.txt", "w", encoding="utf-8") as f:
        f.write(res)

if __name__ == "__main__":
    asyncio.run(run_test_a())
