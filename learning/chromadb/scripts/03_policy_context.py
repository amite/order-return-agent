#!/usr/bin/env python3
"""
Policy Context Examples

This script demonstrates how to retrieve policy explanations
for specific eligibility reason codes.

Run with: uv run python learning/chromadb/scripts/03_policy_context.py
"""

from src.rag.knowledge_base import KnowledgeBase
from src.models.enums import EligibilityReasonCode


def main():
    print("=" * 60)
    print("Policy Context Examples")
    print("=" * 60)
    
    # Initialize
    kb = KnowledgeBase()
    if not kb.health_check():
        print("Ingesting documents...")
        kb.ingest_documents()
    
    # All supported reason codes
    reason_codes = [
        ("TIME_EXP", "Return window expired"),
        ("ITEM_EXCL", "Item not returnable (final sale)"),
        ("DAMAGED_MANUAL", "Damaged items need escalation"),
        ("RISK_MANUAL", "Fraud/high returns need review"),
        ("DATA_ERR", "Missing order information"),
    ]
    
    print("\nRetrieving policy context for each reason code:\n")
    
    for reason_code, description in reason_codes:
        print(f"📋 {reason_code} - {description}")
        print("-" * 60)
        
        context = kb.get_policy_context(reason_code)
        
        # Display first 300 characters
        preview = context[:300] + "..." if len(context) > 300 else context
        print(f"\n{preview}\n")
        print(f"Full context length: {len(context)} characters\n")
    
    # Example: Using in a real scenario
    print("\n" + "=" * 60)
    print("Example: Using in Agent Logic")
    print("=" * 60)
    
    # Simulate an eligibility check result
    eligibility_result = {
        "reason_code": EligibilityReasonCode.TIME_EXP,
        "order_id": "ORD-12345",
        "customer_id": 1
    }
    
    print(f"\nScenario: Return request rejected")
    print(f"Reason Code: {eligibility_result['reason_code']}")
    print(f"Order ID: {eligibility_result['order_id']}")
    
    # Get policy context
    policy_context = kb.get_policy_context(eligibility_result['reason_code'])
    
    print(f"\nPolicy Explanation:")
    print(f"{policy_context[:400]}...")
    
    print("\n" + "=" * 60)
    print("✅ Policy context examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
