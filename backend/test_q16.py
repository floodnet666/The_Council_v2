import asyncio
from engines.data_engine import DataEngine
from agents.analyst_agent import AnalystAgent

async def main():
    de = DataEngine()
    # Use small slice or full file to evaluate correlation 
    de.load_data(r"C:\Users\thiag\Downloads\online_shoppers.csv")
    
    agent = AnalystAgent(data_engine=de)
    
    # Query 16 from benchmark
    query = "Existe correlação entre BounceRates e ExitRates?"
    print(f"Executing: {query}")
    
    res = await agent.run(query, active_file=r"C:\Users\thiag\Downloads\online_shoppers.csv")
    print("\n--- AGENT RESPONSE ---")
    print(res)

if __name__ == "__main__":
    asyncio.run(main())
