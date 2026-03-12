import asyncio
from agents.librarian_agent import LibrarianAgent
from utils.logging_config import logger
import json

# Example Golden Dataset
GOLDEN_DATASET = [
    {
        "query": "What is the main purpose of the Council system?",
        "expected_keywords": ["agent", "orchestration", "data", "analysis"]
    },
    {
        "query": "How does the AnalystAgent handle data?",
        "expected_keywords": ["polars", "query", "execution"]
    }
]

async def evaluate_librarian():
    agent = LibrarianAgent()
    logger.info(f"Starting evaluation of LibrarianAgent with {len(GOLDEN_DATASET)} cases")
    
    results = []
    for case in GOLDEN_DATASET:
        query = case["query"]
        logger.info(f"Testing query: {query}")
        
        response = await agent.run(query)
        
        # Simple keyword check for evaluation
        matched = [kw for kw in case["expected_keywords"] if kw.lower() in response.lower()]
        score = len(matched) / len(case["expected_keywords"])
        
        results.append({
            "query": query,
            "score": score,
            "matched_keywords": matched,
            "passed": score >= 0.5
        })
        
        logger.info(f"Score: {score:.2f} | Passed: {score >= 0.5}")

    # Final summary
    avg_score = sum(r["score"] for r in results) / len(results)
    logger.info(f"Evaluation complete. Average Score: {avg_score:.2f}")
    
    with open("tests/evaluation_results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    asyncio.run(evaluate_librarian())
