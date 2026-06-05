import asyncio
import os
import sys
import traceback

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from engines.data_engine import DataEngine
from agents.analyst_agent import AnalystAgent

async def main():
    data_engine = DataEngine()
    analyst = AnalystAgent(data_engine=data_engine)
    dataset_path = r"C:\Users\thiag\Downloads\online_shoppers.csv"
    
    data_engine.load_data(dataset_path)
    
    try:
        response = await analyst.run("Existe correlação entre BounceRates e ExitRates?", active_file=dataset_path)
        print("Response:", response)
    except Exception:
        print("\n=== STACK TRACE ===")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
