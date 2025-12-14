#!/usr/bin/env python3
"""
Exception Handling Examples

This script demonstrates how to retrieve guidance for handling
specific exceptions and edge cases.

Run with: uv run python learning/chromadb/scripts/05_exception_handling.py
"""

from src.rag.knowledge_base import KnowledgeBase


def main():
    print("=" * 60)
    print("Exception Handling Examples")
    print("=" * 60)
    
    # Initialize
    kb = KnowledgeBase()
    if not kb.health_check():
        print("Ingesting documents...")
        kb.ingest_documents()
    
    # Exception types
    exception_types = [
        ("damaged", "Damaged items"),
        ("fraud", "Fraud prevention"),
        ("compassionate", "Compassionate circumstances"),
        ("high_value", "High-value items"),
        ("customized", "Customized items")
    ]
    
    print("\nRetrieving guidance for each exception type:\n")
    
    for exception_type, description in exception_types:
        print(f"⚠️  {description} ({exception_type})")
        print("-" * 60)
        
        guidance = kb.get_exception_guidance(exception_type)
        
        # Display first 300 characters
        preview = guidance[:300] + "..." if len(guidance) > 300 else guidance
        print(f"\n{preview}\n")
        print(f"Guidance length: {len(guidance)} characters\n")
    
    # Example: Using in a real scenario
    print("\n" + "=" * 60)
    print("Example: Using in Agent Logic")
    print("=" * 60)
    
    # Simulate a damaged item scenario
    item_condition = "damaged"
    order_id = "ORD-12345"
    item_name = "Laptop"
    
    print(f"\nScenario: Damaged item return")
    print(f"Order ID: {order_id}")
    print(f"Item: {item_name}")
    print(f"Condition: {item_condition}")
    
    # Get exception guidance
    guidance = kb.get_exception_guidance(item_condition)
    
    print(f"\nHandling Guidance:")
    print(f"{guidance[:400]}...")
    
    print("\n" + "=" * 60)
    print("✅ Exception handling examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
