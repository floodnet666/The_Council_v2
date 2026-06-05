import asyncio
from langchain_core.messages import AIMessage
from workflow.graph import create_graph

async def main():
    graph = await create_graph()
    
    # Simulate correct config with a valid LazyFrame loaded, but we can just invoke it.
    state = {
        "active_file": r"uploads\Liquor_Sales.csv",
        "messages": [AIMessage(content="quais top 3 produtos mais vendios?")],
        "next_node": "analyst" # Skip router node trigger if needed, or let router decide
    }
    
    # Let's run analyst_node directly to avoid router node LLM latency
    from workflow.graph import analyst_node
    print("Running analyst_node directly...")
    try:
        # Mock State
        await analyst_node({
             "active_file": r"uploads\Liquor_Sales.csv",
             "messages": [AIMessage(content="quais top 3 produtos mais vendios?")]
        })
    except Exception:
        print("\n--- CRASHED ---")
    
if __name__ == "__main__":
    asyncio.run(main())
