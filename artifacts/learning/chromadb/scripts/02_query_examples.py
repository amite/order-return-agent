#!/usr/bin/env python3
"""
Query Examples - Different Types of Queries

This script demonstrates various query patterns:
1. Policy-related queries
2. Time-based queries
3. Item-specific queries
4. Exception handling queries
5. Custom top_k values

Run with: uv run python learning/chromadb/scripts/02_query_examples.py
"""

from src.rag.knowledge_base import KnowledgeBase


def main():
    print("=" * 60)
    print("ChromaDB Query Examples")
    print("=" * 60)
    
    # Initialize
    kb = KnowledgeBase()
    if not kb.health_check():
        print("Ingesting documents...")
        kb.ingest_documents()
    
    # Example queries
    queries = [
        {
            "name": "Policy Query",
            "query": "return policy electronics 90 days",
            "top_k": 3
        },
        {
            "name": "Time-based Query",
            "query": "return window expiration time limit",
            "top_k": 2
        },
        {
            "name": "Item-specific Query",
            "query": "final sale items non-returnable",
            "top_k": 2
        },
        {
            "name": "Exception Query",
            "query": "damaged items escalation process",
            "top_k": 2
        },
        {
            "name": "Fraud Prevention Query",
            "query": "fraud prevention high return frequency",
            "top_k": 1
        }
    ]
    
    # Execute each query
    for i, example in enumerate(queries, 1):
        print(f"\n{i}️⃣ {example['name']}")
        print(f"   Query: '{example['query']}'")
        print(f"   Top K: {example['top_k']}")
        
        results = kb.query(example['query'], top_k=example['top_k'])
        print(f"   Results: {len(results)}")
        
        for j, doc in enumerate(results, 1):
            print(f"\n   Result {j}:")
            print(f"   - Source: {doc.metadata['source']}")
            print(f"   - Preview: {doc.page_content[:100]}...")
    
    print("\n" + "=" * 60)
    print("✅ Query examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
