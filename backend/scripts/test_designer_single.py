import os
import json
import asyncio
from workflow.graph import create_graph
from langchain_core.messages import HumanMessage

async def main():
    graph = await create_graph()
    q_text = "Gere um gráfico de barras com o total de pedidos por status_pedido"
    
    input_state = {
        "messages": [HumanMessage(content=q_text)],
        "language": "pt",
        "active_file": "uploads/vendas_complexas_100k.csv"
    }
    config = {"configurable": {"thread_id": "test_single_designer"}}
    
    output = await graph.ainvoke(input_state, config=config)
    print("FINISHED")
    print(output.get("visual_schema"))

if __name__ == "__main__":
    asyncio.run(main())
