#!/usr/bin/env python3
"""
Basic ChromaDB Usage Example

This script demonstrates the fundamental operations:
1. Initialize KnowledgeBase
2. Ingest documents
3. Perform basic queries
4. Display results

Run with: uv run python learning/chromadb/scripts/01_basic_usage.py
"""

from src.rag.knowledge_base import KnowledgeBase


def main():
    print("=" * 60)
    print("ChromaDB Basic Usage Example")
    print("=" * 60)
    
    # Step 1: Initialize
    print("\n1️⃣ Initializing KnowledgeBase...")
    kb = KnowledgeBase()
    print("   ✅ KnowledgeBase initialized")
    
    # Step 2: Check health and ingest if needed
    print("\n2️⃣ Checking health...")
    if not kb.health_check():
        print("   ⚠️  Vector store not ready, ingesting documents...")
        count = kb.ingest_documents()
        print(f"   ✅ Ingested {count} documents")
    else:
        print("   ✅ Vector store is ready")
    
    # Step 3: Basic query
    print("\n3️⃣ Performing basic query...")
    query = "return policy for electronics"
    print(f"   Query: '{query}'")
    
    results = kb.query(query, top_k=3)
    print(f"   Found {len(results)} results\n")
    
    # Step 4: Display results
    for i, doc in enumerate(results, 1):
        print(f"   --- Result {i} ---")
        print(f"   Source: {doc.metadata['source']}")
        print(f"   Content preview: {doc.page_content[:150]}...")
        print()
    
    print("=" * 60)
    print("✅ Basic usage example complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
