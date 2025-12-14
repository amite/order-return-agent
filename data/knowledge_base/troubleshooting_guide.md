# AI Agent Troubleshooting Guide

## Common Failure Scenarios

### Tool Call Failures

#### Order Not Found
**Symptom:** GetOrderDetails returns "Order not found"

**Diagnosis:**
- Customer may have typo in order number
- Order may be under different email
- Order may be from different company/website

**Resolution:**
1. Ask customer to double-check order number
2. Request confirmation email screenshot
3. Try alternate email addresses
4. If still not found, escalate to Account Research

#### Eligibility Check Returns Unexpected Result
**Symptom:** CheckEligibility returns INELIGIBLE when customer believes it should be eligible

**Diagnosis:**
- Order may be older than customer remembers
- Item may be final sale
- Customer may have fraud flag
- VIP status not recognized

**Resolution:**
1. Clearly explain the specific reason code (TIME_EXP, ITEM_EXCL, etc.)
2. Provide exact dates: "Order placed on [DATE], which is [X] days ago"
3. Offer alternatives (store credit, exchange)
4. If customer disputes, escalate to manager

#### RMA Creation Fails
**Symptom:** CreateRMA returns error after eligibility approved

**Diagnosis:**
- Database connectivity issue
- Invalid item IDs
- Duplicate RMA attempt

**Resolution:**
1. Retry once
2. If fails again, log error details
3. Escalate to Technical Support immediately
4. Inform customer: "I've encountered a technical issue. Our tech team will resolve this within 24 hours."

### Conversation Flow Issues

#### Customer Provides Incomplete Information
**Symptom:** Customer says "I want to return my order" without details

**Resolution:**
Ask clarifying questions in this order:
1. "Do you have your order number handy?"
2. "What item(s) would you like to return?"
3. "Could you tell me the reason for the return?"

**Example:**
"I'd be happy to help with your return! To get started, do you have your order number? It's usually in your confirmation email."

#### Customer Asks Multiple Questions at Once
**Symptom:** "I want to return these shoes and also when will my refund arrive and do you have them in blue?"

**Resolution:**
1. Acknowledge all questions
2. Address in logical order
3. Use numbered lists

**Example:**
"I can help with all of that! Let me address each question:

1. For the shoe return - Yes, I can process that. Do you have your order number?
2. Refund timing - Once we receive your return, refunds typically process in 3-5 business days
3. Blue shoes - I can check availability once we complete the return process

Let's start with #1. What's your order number?"

#### Customer Becomes Repetitive or Confused
**Symptom:** Customer keeps repeating the same information or question

**Resolution:**
1. Don't repeat yourself either
2. Summarize what you've done so far
3. Ask specific next-step question
4. If confusion persists after 3 attempts, escalate

**Example:**
"I want to make sure we're on the same page. So far:
- I found your order #12345
- I checked eligibility and unfortunately it's outside the 30-day window
- I offered store credit as an alternative

The next step is for you to decide if you'd like the store credit. Would that work for you? If not, I can connect you with a manager who may have other options."

### Edge Cases

#### Item Returned But Customer Never Shipped It
**Symptom:** Customer claims they didn't ship the item yet but RMA shows "In Transit"

**Diagnosis:**
- System error
- Wrong tracking number assigned
- Customer confused with another order

**Resolution:**
1. Verify RMA number with customer
2. Check tracking number status independently
3. If mismatch, escalate to Logistics immediately
4. Priority: HIGH

#### Customer Lost Return Label
**Symptom:** Customer can't find the email with the return label

**Resolution:**
1. Verify email address on file
2. Check spam/junk folder
3. Offer to resend: "I can resend the label to you right now."
4. Provide direct download link if possible
5. As last resort, create new label

#### Label Won't Print
**Symptom:** Customer can't print the return label

**Resolution:**
1. Verify file format (should be PDF)
2. Suggest: "Try opening the PDF in a different browser"
3. Offer email to different address
4. Alternative: "You can also show the digital label on your phone at the shipping location"
5. Last resort: "Let me email you a QR code instead"

### Performance Optimization

#### Conversation Taking Too Long
**Symptom:** More than 10 back-and-forth messages to complete return

**Diagnosis:**
- Not asking right questions
- Customer unsure what they want
- Technical issues

**Resolution:**
1. After 6 messages without progress, summarize and provide clear options
2. After 8 messages, consider escalation
3. Don't keep repeating same questions

**Example (after 6 messages):**
"Let me make sure I understand what you need. You have order #12345 and want to return the Red Shoes. The order is 45 days old.

Here are your options:
A) Accept store credit for $40 (50% of purchase price)
B) Speak with a manager about additional options
C) Keep the item

Please choose A, B, or C, and I'll proceed accordingly."

#### Tools Returning Slow
**Symptom:** Long delay between your message and next action

**Resolution:**
1. Let customer know: "I'm checking our system now, one moment please."
2. If timeout occurs, apologize and retry
3. If persistent, escalate to Technical Support

### Error Recovery Strategies

#### When You Make a Mistake
**Symptom:** You provided wrong information or called wrong tool

**Resolution:**
1. Acknowledge immediately: "I apologize, I misspoke."
2. Correct with accurate information
3. Continue professional
4. Don't over-apologize or dwell on it

**Example:**
"I apologize, I misspoke earlier. Your return window is actually 30 days, not 60 days. That means your order from 45 days ago is outside the standard window. I can still offer you store credit. Would that work?"

#### When System Fails Multiple Times
**Symptom:** 3+ tool calls fail in same conversation

**Resolution:**
1. Stop trying tools
2. Escalate to human immediately
3. Be transparent: "I'm experiencing technical difficulties. Let me connect you with a team member who can help you right away."

### Sentiment Analysis and De-escalation

#### Detecting Frustration
**Indicators:**
- Exclamation marks!!!!
- All caps: "THIS IS RIDICULOUS"
- Profanity
- Threats: "I'll never shop here again"
- Sarcasm: "Oh great, another useless policy"

**Response:**
1. Acknowledge emotion: "I understand this is frustrating."
2. Apologize for situation (not for policy): "I'm sorry this happened."
3. Take action or escalate
4. Don't match emotion or get defensive

**Example:**
"I completely understand your frustration, and I'm sorry our policy doesn't allow for a full refund in this case. I can see you're a valued customer, and I want to make this right. I can offer store credit or connect you with my manager who may have additional options. What would you prefer?"

#### When to Escalate Based on Sentiment
**Escalate if:**
- Customer uses profanity (even mild)
- Customer threatens legal action
- Customer expresses they want a human
- You've offered all possible solutions and customer still unsatisfied
- Customer tone becomes abusive

**Don't Escalate if:**
- Customer is mildly disappointed but accepting solution
- Customer asks simple follow-up questions
- Customer is just being verbose/chatty

### Quality Assurance Checks

#### Before Completing Any Return
**Checklist:**
✓ Order verified in system
✓ Eligibility checked with tool (not assumption)
✓ RMA created successfully
✓ Label generated
✓ Email sent to customer
✓ Customer acknowledges they received information

#### Before Denying Any Return
**Checklist:**
✓ Clear explanation of why given
✓ Specific reason code mentioned
✓ Alternative offered
✓ Customer given chance to respond
✓ Escalation offered if customer wants

### Handling Unique Situations

#### Customer is Blind/Visually Impaired
**Indicators:** Mentions screen reader, asks for text description of label

**Adaptations:**
- Provide detailed text instructions
- Read out tracking number clearly
- Offer to email instructions in plain text format
- Suggest phone support for label printing assistance

#### Customer Has Language Barrier
**Indicators:** Unclear phrasing, grammar issues, asks for clarification multiple times

**Adaptations:**
- Use simple, short sentences
- Avoid idioms and complex words
- Use bullet points and numbered lists
- Be patient and repeat if needed
- Don't escalate just due to language barrier

#### Customer is Elderly
**Indicators:** Mentions difficulty with technology, asks basic computer questions

**Adaptations:**
- Provide step-by-step instructions
- Offer phone support alternative
- Be patient with technical questions
- Don't assume knowledge of terms like "PDF" or "download"

### Success Metrics to Track

For each conversation, aim for:
- ✓ Resolution in under 10 messages
- ✓ Customer sentiment: Neutral or Positive at end
- ✓ All tools executed successfully
- ✓ Clear next steps provided
- ✓ No unnecessary escalations

### When in Doubt

**Golden Rules:**
1. If unsure about eligibility, let CheckEligibility tool decide (never guess)
2. If customer is upset, offer escalation
3. If technical issue persists, escalate to Tech Support
4. If policy is unclear, escalate to human rather than guess
5. Always err on the side of customer satisfaction while following policy

**Remember:** Your job is to help customers while following company policy. Use your tools correctly, be empathetic, and escalate when appropriate. You don't have to solve every problem yourself - knowing when to escalate is a skill.
