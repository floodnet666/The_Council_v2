import asyncio
from engines.data_engine import DataEngine
from agents.analyst_agent import AnalystAgent

async def main():
    data_engine = DataEngine()
    # Create dummy empty CSV with Liquor columns if needed, or just loading something
    # For replication, we need to understand which line crashes.
    # Let's mock a LazyFrame scenario
    agent = AnalystAgent(data_engine)
    
    # We must load a dataset that triggers the exact flow.
    # Let's mock load_data to skip 4GB load for faster debug, or use online_shoppers.csv
    data_engine.load_data(r"C:\Users\thiag\Downloads\online_shoppers.csv")
    print("Data loaded. Running query...")
    try:
        res = await agent.run("quais top 3 produtos mais vendidos?", r"C:\Users\thiag\Downloads\online_shoppers.csv")
        print("\n--- AGENT RESPONSE ---")
        print(res)
    except Exception:
        print("\n--- CRASHED ---")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
