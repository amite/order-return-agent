#!/usr/bin/env python3
"""
Complete ChromaDB Demo

This script demonstrates a complete workflow:
1. Initialization and health check
2. Document ingestion (if needed)
3. General queries
4. Policy context retrieval
5. Communication templates
6. Exception handling
7. Integration pattern example

Run with: uv run python learning/chromadb/scripts/06_complete_demo.py
"""

from src.rag.knowledge_base import KnowledgeBase
from src.models.enums import EligibilityReasonCode


def simulate_agent_workflow(kb: KnowledgeBase):
    """Simulate how an agent would use the knowledge base"""
    print("\n" + "=" * 60)
    print("🤖 Simulated Agent Workflow")
    print("=" * 60)
    
    # Scenario 1: Return Approved
    print("\n📋 Scenario 1: Return Approved")
    print("-" * 60)
    print("Customer: Jane Smith")
    print("Order ID: ORD-12345")
    print("Item: Wireless Mouse")
    print("Status: APPROVED")
    
    template = kb.get_communication_template("approval")
    print(f"\nResponse Template:")
    print(f"{template[:200]}...")
    
    # Scenario 2: Return Rejected (Time Expired)
    print("\n\n📋 Scenario 2: Return Rejected (Time Expired)")
    print("-" * 60)
    print("Customer: John Doe")
    print("Order ID: ORD-67890")
    print("Item: Laptop")
    print("Status: TIME_EXP")
    
    policy = kb.get_policy_context("TIME_EXP")
    rejection_template = kb.get_communication_template("rejection")
    
    print(f"\nRejection Template:")
    print(f"{rejection_template[:200]}...")
    print(f"\nPolicy Explanation:")
    print(f"{policy[:200]}...")
    
    # Scenario 3: Exception Handling (Damaged Item)
    print("\n\n📋 Scenario 3: Exception Handling (Damaged Item)")
    print("-" * 60)
    print("Customer: Alice Johnson")
    print("Order ID: ORD-11111")
    print("Item: Monitor")
    print("Condition: Damaged")
    print("Status: DAMAGED_MANUAL")
    
    guidance = kb.get_exception_guidance("damaged")
    escalation_template = kb.get_communication_template("escalation")
    
    print(f"\nEscalation Template:")
    print(f"{escalation_template[:200]}...")
    print(f"\nHandling Guidance:")
    print(f"{guidance[:200]}...")
    
    print("\n" + "=" * 60)


def main():
    print("=" * 60)
    print("ChromaDB Complete Demo")
    print("=" * 60)
    
    # Step 1: Initialize
    print("\n1️⃣ Initializing KnowledgeBase...")
    kb = KnowledgeBase()
    print("   ✅ Initialized")
    
    # Step 2: Health check and ingest
    print("\n2️⃣ Health Check...")
    if not kb.health_check():
        print("   ⚠️  Not ready, ingesting documents...")
        count = kb.ingest_documents()
        print(f"   ✅ Ingested {count} documents")
    else:
        print("   ✅ System healthy")
    
    # Step 3: General queries
    print("\n3️⃣ General Queries...")
    queries = [
        "return policy electronics",
        "final sale restrictions",
        "fraud prevention"
    ]
    
    for query in queries:
        results = kb.query(query, top_k=1)
        print(f"   Query: '{query}' → {len(results)} result(s)")
    
    # Step 4: Policy context
    print("\n4️⃣ Policy Context Retrieval...")
    reason_codes = ["TIME_EXP", "ITEM_EXCL", "DAMAGED_MANUAL"]
    for code in reason_codes:
        context = kb.get_policy_context(code)
        print(f"   {code}: {len(context)} characters")
    
    # Step 5: Templates
    print("\n5️⃣ Communication Templates...")
    scenarios = ["approval", "rejection", "escalation"]
    for scenario in scenarios:
        template = kb.get_communication_template(scenario)
        print(f"   {scenario}: {len(template)} characters")
    
    # Step 6: Exception handling
    print("\n6️⃣ Exception Guidance...")
    exceptions = ["damaged", "fraud", "compassionate"]
    for exc_type in exceptions:
        guidance = kb.get_exception_guidance(exc_type)
        print(f"   {exc_type}: {len(guidance)} characters")
    
    # Step 7: Complete workflow simulation
    simulate_agent_workflow(kb)
    
    print("\n" + "=" * 60)
    print("✅ Complete demo finished!")
    print("=" * 60)
    print("\nNext steps:")
    print("  - Review the scripts in this folder")
    print("  - Read the README.md for detailed documentation")
    print("  - Check api_reference.md for API details")
    print("  - Integrate into your agent code")


if __name__ == "__main__":
    main()
