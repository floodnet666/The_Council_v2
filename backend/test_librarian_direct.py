import asyncio
from agents.librarian_agent import LibrarianAgent

async def test():
    print("Testing Librarian Guidelines retrieval...")
    lib = LibrarianAgent()
    res = await lib.run("Como fazer agregação ou agrupamento no Polars corretamente?")
    print("\n--- Librarian Response ---")
    print(res)

if __name__ == "__main__":
    asyncio.run(test())
