import os
import json
import asyncio
from langchain_core.messages import HumanMessage
from workflow.graph import create_graph

QUESTIONS = {
    "bar": "Gere um gráfico de barras com o total de pedidos por status_pedido",
    "line": "Gere um gráfico de linha do tempo mostrando o lucro diário",
    "pie": "Mostre a proporção de pedidos por status_pedido em um gráfico de pizza",
    "scatter": "Faça um gráfico de dispersão cruzando o valor bruto com o valor de desconto para achar padrões"
}

async def run_round(graph, round_name: str, file_name: str):
    print(f"\n--- INICIANDO {round_name} ---")
    results = {}
    
    for q_type, q_text in QUESTIONS.items():
        print(f"\n[{round_name}] Processando Gráfico ({q_type}): {q_text}")
        
        input_state = {
            "messages": [HumanMessage(content=q_text)],
            "language": "pt",
            "active_file": "uploads/vendas_complexas_100k.csv"
        }
        
        # Thread isolation for stateless LLM runs
        config = {"configurable": {"thread_id": f"designer_{round_name}_{q_type}"}}
        
        try:
            print(f"[{round_name}] Enviando requisição para a LLM. Aguardando conclusão síncrona...")
            output = await asyncio.wait_for(graph.ainvoke(input_state, config=config), timeout=300)
            print(f"[{round_name}] Resposta da LLM recebida com sucesso!")
            viz_config = output.get("visual_schema", {})
            viz_data = output.get("raw_data_context", []) # FIXED
            
            print(f"DEBUG: viz_data tem {len(viz_data)} linhas. Config: {viz_config.get('chart_type')}")
        except asyncio.TimeoutError:
            print(f"[{round_name}] TIMEOUT EXTREMO (300s) DO LLM para {q_type}!")
            viz_config = {"error": "LLM Timeout"}
            viz_data = []
        
        results[q_type] = {
            "query": q_text,
            "visual_config": viz_config,
            "visual_data": viz_data
        }
        
        print(f"[{round_name}] Pausa de 5 segundos garantindo esvaziamento total do socket Ollama...")
        await asyncio.sleep(5)
        
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n[{round_name}] Concluído. Salvo em {file_name}")

async def main():
    import workflow.graph as wgraph
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
    
    # [SENIOR ENGINEERING] Isolamento do ambiente de benchmark
    # Em vez de tentar deletar o banco de produção (the_council.db) travado por locks WAL da interrupção abrupta,
    # instanciamos um SQLite em memória exclusivo para a bateria de testes. Zero impacto em Prod.
    async with AsyncSqliteSaver.from_conn_string(":memory:") as checkpointer:
        wgraph._checkpointer = checkpointer
        graph = await wgraph.create_graph()
        await run_round(graph, "RUN_1", "designer_bench_1.json")
        await run_round(graph, "RUN_2", "designer_bench_2.json")
        print("\nBENCHMARK FINALIZADO.")

if __name__ == "__main__":
    asyncio.run(main())
