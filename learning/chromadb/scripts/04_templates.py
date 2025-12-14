#!/usr/bin/env python3
"""
Communication Templates Examples

This script demonstrates how to retrieve communication templates
for different scenarios (approval, rejection, escalation, etc.)

Run with: uv run python learning/chromadb/scripts/04_templates.py
"""

from src.rag.knowledge_base import KnowledgeBase


def main():
    print("=" * 60)
    print("Communication Templates Examples")
    print("=" * 60)
    
    # Initialize
    kb = KnowledgeBase()
    if not kb.health_check():
        print("Ingesting documents...")
        kb.ingest_documents()
    
    # Available scenarios
    scenarios = [
        "approval",
        "rejection",
        "escalation",
        "partial_refund",
        "exchange"
    ]
    
    print("\nRetrieving templates for each scenario:\n")
    
    for scenario in scenarios:
        print(f"📧 Scenario: {scenario.upper()}")
        print("-" * 60)
        
        template = kb.get_communication_template(scenario)
        
        # Display first 300 characters
        preview = template[:300] + "..." if len(template) > 300 else template
        print(f"\n{preview}\n")
        print(f"Template length: {len(template)} characters\n")
    
    # Example: Using in a real scenario
    print("\n" + "=" * 60)
    print("Example: Using in Agent Response")
    print("=" * 60)
    
    # Simulate an approval scenario
    customer_name = "John Doe"
    order_id = "ORD-12345"
    item_name = "Wireless Headphones"
    
    print(f"\nScenario: Return approved")
    print(f"Customer: {customer_name}")
    print(f"Order ID: {order_id}")
    print(f"Item: {item_name}")
    
    # Get approval template
    template = kb.get_communication_template("approval")
    
    print(f"\nTemplate:")
    print(f"{template[:400]}...")
    
    # Note: Templates may have placeholders - check your knowledge base
    # for the exact format and variables needed
    
    print("\n" + "=" * 60)
    print("✅ Template examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
