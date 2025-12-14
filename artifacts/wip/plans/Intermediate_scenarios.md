# Intermediate Scenarios for Order Return Agent

This document outlines intermediate-level scenarios that extend the current agent capabilities without requiring major architectural changes. These scenarios add complexity through multi-step workflows, conditional logic, and enhanced customer interactions.

---

## Current Baseline Capabilities

The agent currently handles:
- Single-order return requests
- Basic eligibility checking (time window, final sale, fraud flag)
- RMA creation with label generation
- Email notifications
- Escalation for damaged items

---

## Intermediate Scenarios

### 1. Partial Order Returns

**Scenario:** Customer wants to return only some items from a multi-item order.

**User Story:**
> "I ordered 5 items last week. I want to keep the shoes and the jacket, but return the other 3 items."

**Complexity Added:**
- Item selection logic within a single order
- Partial refund calculation
- Multiple eligibility checks per order (some items may be final sale, others not)
- Single RMA covering multiple items with different categories

**Implementation Touches:**
- `CheckEligibility` - evaluate each item independently, aggregate results
- `CreateRMA` - accept partial item list, calculate partial refund
- Email template showing itemized return list

---

### 2. Exchange Instead of Refund

**Scenario:** Customer prefers to exchange an item for a different size/color rather than get a refund.

**User Story:**
> "The medium shirt doesn't fit. Can I exchange it for a large instead of getting a refund?"

**Complexity Added:**
- New return type: EXCHANGE vs REFUND
- Inventory availability check (does the requested variant exist?)
- Price difference handling (if exchanging for different priced item)
- Two-way logistics: return old item + ship new item

**New Tool Required:**
- `CheckInventory` - verify replacement item availability

**Implementation Touches:**
- RMA schema extended with `return_type` and `exchange_item_id`
- Modified email template for exchange confirmation
- Additional RAG documents for exchange policies

---

### 3. Multi-Order Return (Same Session)

**Scenario:** Customer wants to return items from multiple recent orders in a single session.

**User Story:**
> "I have returns from two orders - order #12345 and order #67890. Can we process both?"

**Complexity Added:**
- Session-level tracking of multiple orders
- Consolidated vs separate RMAs decision logic
- Combined shipping label option (customer preference)
- Multiple eligibility evaluations

**Implementation Touches:**
- Agent memory for multi-order context
- Decision flow: "Would you like separate return labels or one combined shipment?"
- Summary email covering all returns in session

---

### 4. Return Status Inquiry

**Scenario:** Customer checks status of an existing return (not starting a new one).

**User Story:**
> "I sent back my return last week. What's the status? When will I get my refund?"

**Complexity Added:**
- Query existing RMAs by customer email or RMA number
- Status interpretation and timeline estimation
- Proactive updates if delays detected

**New Tool Required:**
- `GetRMAStatus` - lookup existing RMAs, return current status, estimated timeline

**Implementation Touches:**
- RAG documents for typical processing timelines
- Status-specific response templates (in transit, received, processing, refunded)

---

### 5. Gift Return (No Receipt)

**Scenario:** Customer received an item as a gift and wants to return it without the original order number.

**User Story:**
> "I received this as a gift and want to return it. I don't have the order number."

**Complexity Added:**
- Alternative lookup methods (gift registry, product SKU + timeframe)
- Store credit vs refund options (gift returns typically get store credit)
- Privacy considerations (don't reveal gift giver's order details)

**Implementation Touches:**
- `GetOrderDetails` extended with product SKU lookup
- New refund type: STORE_CREDIT
- Modified eligibility rules for gift returns
- Careful response templating to protect gift giver privacy

---

### 6. Return with Missing/Damaged Components

**Scenario:** Customer wants to return an item but admits a component is missing or damaged.

**User Story:**
> "I want to return the camera, but I lost the charging cable that came with it."

**Complexity Added:**
- Partial refund calculation (deduct missing component value)
- Threshold decision: reject return vs accept with deduction vs escalate
- Component value lookup from product catalog

**Implementation Touches:**
- Product schema extended with `components` list and values
- `CheckEligibility` handles missing component scenarios
- Customer disclosure flow: "Are all original components included?"

---

### 7. Policy Exception Request

**Scenario:** Customer's return is outside policy but requests an exception due to circumstances.

**User Story:**
> "I know it's been 45 days, but I was hospitalized and couldn't return it sooner. Can you make an exception?"

**Complexity Added:**
- Exception request capture and documentation
- Conditional escalation with context (not just damaged items)
- Customer tier consideration (VIP customers may get auto-exceptions)
- Audit trail for exception approvals

**Implementation Touches:**
- Extended escalation metadata (exception_type, customer_statement)
- RAG documents for exception criteria
- Tiered response: auto-approve for VIP, escalate for others

---

### 8. Warranty vs Return Clarification

**Scenario:** Customer has an issue that might be warranty claim vs standard return.

**User Story:**
> "My headphones stopped working after 4 months. What are my options?"

**Complexity Added:**
- Differentiate: defect within warranty vs buyer's remorse
- Product warranty lookup (varies by category/brand)
- Route to warranty process vs return process
- Manufacturer vs retailer responsibility

**New Tool Required:**
- `CheckWarranty` - lookup product warranty terms, determine coverage

**Implementation Touches:**
- Product schema with warranty_months field
- Decision tree: return window open? warranty active? defect or change-of-mind?
- Different email templates for warranty claims

---

### 9. Shipping Damage Claim

**Scenario:** Item arrived damaged due to shipping (not product defect).

**User Story:**
> "The package arrived crushed and the item inside is broken."

**Complexity Added:**
- Photo evidence request (future: image upload handling)
- Carrier claim initiation vs direct replacement
- No-return replacement option (don't require customer to ship back damaged item)
- Insurance claim coordination

**Implementation Touches:**
- New reason codes: SHIPPING_DAMAGE vs PRODUCT_DEFECT
- Modified flow: skip label generation for no-return replacements
- Escalation path for carrier claim coordination

---

### 10. Subscription/Recurring Order Return

**Scenario:** Customer wants to return items from a subscription order and possibly pause/cancel.

**User Story:**
> "I want to return this month's subscription box and skip next month."

**Complexity Added:**
- Subscription vs one-time order handling
- Return + subscription modification in same session
- Prorated refund for partial subscription periods
- Future order management (skip, pause, cancel)

**New Tool Required:**
- `ManageSubscription` - modify subscription status (pause, skip, cancel)

**Implementation Touches:**
- Order schema with `is_subscription` and `subscription_id` fields
- Cross-reference subscription status when processing returns
- Combined confirmation: "Return processed + subscription paused until [date]"

---

### 11. Pre-Return Troubleshooting

**Scenario:** Agent attempts to solve issue before processing return (reducing unnecessary returns).

**User Story:**
> "This bluetooth speaker won't connect to my phone."

**Complexity Added:**
- Problem diagnosis flow before offering return
- Product-specific troubleshooting steps from knowledge base
- Track "issue resolved" vs "proceeding to return" outcomes
- Deflection rate metrics

**Implementation Touches:**
- Enhanced RAG with product troubleshooting guides
- Conversation flow: troubleshoot first, then offer return if unresolved
- New conversation outcome types: RESOLVED_NO_RETURN, PROCEEDED_TO_RETURN

---

### 12. Address Change for Return Label

**Scenario:** Customer's address has changed since the original order.

**User Story:**
> "I moved last month. Can you send the return label to my new address?"

**Complexity Added:**
- Address verification/update flow
- Label regeneration with new pickup address
- Customer record update considerations
- Fraud prevention (address change + high-value return = flag)

**Implementation Touches:**
- `GenerateReturnLabel` accepts optional override address
- Address validation step before label generation
- Risk scoring for address mismatches on high-value returns

---

## Implementation Priority Matrix

| Scenario | Complexity | Business Value | Dependencies |
|----------|------------|----------------|--------------|
| 1. Partial Order Returns | Low | High | None |
| 4. Return Status Inquiry | Low | High | New tool |
| 6. Missing Components | Medium | Medium | Product catalog |
| 11. Pre-Return Troubleshooting | Medium | High | RAG content |
| 3. Multi-Order Return | Medium | Medium | Agent memory |
| 7. Policy Exception | Medium | Medium | Escalation enhancement |
| 2. Exchange Instead of Refund | High | High | Inventory system |
| 5. Gift Return | High | Medium | Alternative lookup |
| 8. Warranty Clarification | High | Medium | Warranty database |
| 9. Shipping Damage | High | Medium | Carrier integration |
| 10. Subscription Return | High | Low | Subscription system |
| 12. Address Change | Medium | Low | Address validation |

---

## Recommended Phase 4 Implementation Order

### Phase 4A: Quick Wins (Low complexity, high value)
1. **Partial Order Returns** - leverages existing tools
2. **Return Status Inquiry** - simple new tool + templates

### Phase 4B: Enhanced Customer Experience
3. **Pre-Return Troubleshooting** - RAG enhancement
4. **Policy Exception Requests** - escalation enhancement
5. **Missing Components** - eligibility logic extension

### Phase 4C: Advanced Workflows
6. **Multi-Order Returns** - session management
7. **Exchange Processing** - new fulfillment path
8. **Gift Returns** - alternative lookup patterns

### Phase 4D: Integrations (Requires External Systems)
9. **Warranty Claims** - warranty database needed
10. **Shipping Damage** - carrier API integration
11. **Subscription Returns** - subscription management system
12. **Address Changes** - address validation service

---

## Test Data Additions Needed

To support these scenarios, add to `seed.py`:

```python
# Multi-item orders for partial return testing
# Orders with subscription flag
# Products with warranty_months field
# Products with component lists
# Customers with recent address changes
# Existing RMAs in various statuses for status inquiry
# Gift orders (marked with gift_message, gift_from_customer_id)
```

---

## Success Metrics for Intermediate Scenarios

| Metric | Target |
|--------|--------|
| Partial return accuracy | 95%+ correct item selection |
| Status inquiry resolution | 90%+ answered without escalation |
| Troubleshooting deflection | 15%+ returns avoided via troubleshooting |
| Exception handling time | <2 min to escalate with full context |
| Multi-order session completion | 85%+ both orders processed correctly |
