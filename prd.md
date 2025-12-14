# Order Return Request agent involving rag and using mock database

An AI customer service agent executing an **Order Return Request** using tool-calling operates as a sophisticated, multi-step workflow in real-world implementations. It moves far beyond a simple Q\&A process by integrating with multiple internal and external systems via predefined functions (tools).

### 🤖 AI Return Request Execution: A Multi-Step Procedure

The process is inherently **multi-step** and often involves coordinating several distinct actions, each initiated by a tool-call from the core AI agent:

1. **Intent Identification & Data Acquisition:**
    - The agent first understands the customer's natural language request (e.g., "I need to return this shirt").
    - **Tool-Call:** A function like `GetOrderDetails(order_id, customer_id)` is called to retrieve necessary information from the **Order Management System (OMS)** or **CRM**. This fetches the original order, product details, purchase date, and customer history.
2. **Eligibility and Policy Validation:**
    - The agent checks the return request against the company's rules.
    - **Tool-Call:** A function like `CheckReturnEligibility(order_details, return_reason)` is called, which uses a knowledge base (often implemented via **Retrieval-Augmented Generation (RAG)** or a dedicated policy tool) to check factors like:
        - Is the request within the return window?
        - Is the item type eligible for return/refund/exchange?
        - Is the customer flagged for potential **fraud** (checked by a separate fraud detection agent or service)?
3. **Logistics and Authorization:**
    - If approved, the agent authorizes the return and arranges for shipping.
    - **Tool-Call:** A function like `GenerateReturnLabel(address, logistics_partner_API)` interacts with a **Logistics API** to create a shipping label, and simultaneously updates the internal system.
    - **Tool-Call:** A function like `SendCustomerCommunication(message, email_template)` is used to email the label and return instructions to the customer.
4. **System Update and Refund Trigger:**
    - The system must be updated to await the return and process the refund later.
    - **Tool-Call:** A function like `CreateReferenceReturnOrder(order_details, RMA_number)` updates the OMS or **Warehouse Management System (WMS)**, generating a Return Merchandise Authorization (RMA) number.
    - The agent may even initiate an instant refund for low-risk, high-value customers, using a **Dynamic Refund Management** tool-call to the **Payment Gateway**.

### 🤝 Multi-Agent Collaboration and Information Passing

The "real-world implementation" frequently involves a **multi-agent** or **multi-tool** architecture, demanding sophisticated **information passing**:

| Component | Role in Return Request | Information Passed |
| --- | --- | --- |
| **Orchestrator Agent** (Coordinator) | Manages the entire process flow, ensuring sequential execution. | Passes the customer's query and the `SupportCase` object to the next agent. |
|  |  |  |
| **Execution Agent** | Handles tool-calling for core actions (e.g., fetching order, generating label). | Passes `OrderDetails` and `RMA_number` to the Communication Agent. |
| **Communication Agent** | Generates and sends personalized, branded responses. | Receives `RMA_number` and `NextSteps` to craft the final email/chat response. |
| **Escalation Agent** | Determines if the issue is too complex for automation. | If an exception occurs, flags the `SupportCase` for a human agent. |

In this system, a central, shared object (like a `SupportCase` or a transaction record) acts as a **"shared notepad"** to transfer state and context between the specialized agents, ensuring seamless handoff and maintaining full context. This design is highly common as it increases precision and reduces the risk of the main agent exceeding its token limit or failing a complex reasoning task.

---

Systems involved

- **Order Management System (OMS)**
- Knowledge base (refund policies)

Work Flow

| **Requirement** | **Description** | **Acceptance Criteria** |
| --- | --- | --- |
| **R1: Order Retrieval** | Agent must call a tool to fetch customer order details (products, date, status). | Tool `GetOrderDetails(id)` returns valid JSON structure. |
| **R2: Eligibility Check** | Agent must apply business logic (e.g., 30-day window, item type) via a tool-call. | Tool `CheckEligibility()` returns `Eligible` or `Ineligible` with a reason code. |
| **R3: Label Generation** | Agent must call a logistics API tool to generate a shipping label. | Tool `GenerateReturnLabel()` returns a URL to a printable PDF label. |
| **R4: System Update** | Agent must update the Order Management System (OMS) to create an RMA (Return Merchandise Authorization) and mark the order as "Return Initiated."  | Tool `CreateRMA(order_id)` returns a unique RMA number. |
| **R5: Communication** | Agent must send the RMA number, label link, and instructions to the customer via email/chat. | Tool `SendEmail(customer_email, template)` confirms successful delivery. |
| **R6: Human Handoff** | If eligibility fails or the customer expresses frustration/complexity, the agent must escalate. | Agent passes full conversation history and `RMA_Attempt_Log` to human agent queue. |

| **Tool Name** | **Endpoint / Function Signature** | **Parameters** | **Response Example** |
| --- | --- | --- | --- |
| `GetOrderDetails` | `POST /api/v1/orders/lookup` | `order_id: string`, `email: string` | `{status: "shipped", items: [...]}` |
| `CheckEligibility` | `POST /api/v1/returns/eligibility` | `order_id: string`, `reason: string` | `{eligible: true, policy: "30-day"}` |
| `GenerateReturnLabel` | `POST /api/v1/logistics/label` | `order_id: string` | `{rma_id: "RMA123", label_url: "..."}` |

### 6. Risks, Assumptions, & Dependencies

- **Risk:** The LLM hallucinates an eligible return when the policy says no. **Mitigation:** Rely *only* on the hard-coded logic of the `CheckEligibility` tool, not the LLM's general knowledge.
- **Risk:** Latency on external API calls (e.g., Logistics) leads to slow response times. **Mitigation:** Set a strict timeout (e.g., 5 seconds) and fall back to the human agent on failure.
- **Assumption:** The `GetOrderDetails` tool is already available and provides real-time data.
- **Dependency:** Engineering team must complete and test the three core Tool APIs (`GetOrderDetails`, `CheckEligibility`, `GenerateReturnLabel`) before agent training can begin.

---

The process by which the agent collects initial user data about the order is crucial for initiating the return process. This flow is designed to be conversational while ensuring all necessary data points are captured to execute the first tool-call effectively.

Here is the step-by-step flow, often referred to as a **Slot-Filling** or **Data Elicitation** process:

---

## 🗺️ Flow for Collecting Initial Order Data

### Step 1: Intent Confirmation and Initial Prompt

The agent's first job is to confirm the user's goal and request the starting piece of information.

- **User Action:** User initiates the request (e.g., "I need to return something I bought last month.")
- **Agent Action:**
    1. **Confirm Intent:** "I can certainly help you with a return. To start the process, I'll need your order details."
    2. **Request Core Data:** "Do you have the **Order Number** available?"

### Step 2: Order ID Elicitation (Crucial Slot)

The Order Number is the primary key for the system. The agent will continue to prompt until this required "slot" is filled.

| **User Input Type** | **Agent Action** | **Next Step** |
| --- | --- | --- |
| **Direct Answer** | User: "Yes, it's **12345**." | Agent confirms and moves to **Step 3**. |
| **Partial Answer** | User: "It was that big electronics order." | Agent: "Thank you. I need the specific 5-digit order number. Can you check your confirmation email?" |
| **Don't Know / Need Help** | User: "No, I can't find it." | Agent: "No problem. I can look it up for you using the **email address** associated with the order." |

### Step 3: Secondary Data Elicitation (Fallback)

If the Order ID is unavailable, the agent needs an alternative identifier, usually the email address.

- **Agent Action (If Order ID Unknown):** "Please provide the email address used when you placed the order."
- **Data Validation:** The agent may use regex (internal validation) to ensure the input looks like a valid email format before attempting the lookup.
- **Scenario:** User provides `customer@example.com`.

### Step 4: Tool-Call Execution and Data Retrieval

Once the agent has the minimum required data (Order ID OR Email + related details like name/date), it executes the first tool-call.

- **Agent Action:** The agent executes the **`GetOrderDetails`** tool.
    - **Tool Signature:** `GetOrderDetails(order_id: string, email: string)`
    - **Parameters Passed:** `order_id="12345"` (or `order_id=null`, `email="customer@example.com"`)
- **System Response:**
    - **Success:** The tool returns a JSON object containing `order_date`, `customer_name`, and a list of `items_purchased`.
    - **Failure:** The tool returns an error code (e.g., "Order not found," "Multiple orders found").

### Step 5: Verification and Context Setting

To ensure accuracy and confirm the next steps, the agent verifies the retrieved information with the user.

- **Agent Action (Success):** "Great, I found Order **12345** placed on **November 10th**. This order contained a **Smart Watch** and a **Leather Band**. Is this the order you wish to return an item from?"
- **User Action:** User: "Yes, the Smart Watch."
- **Agent Action (Failure):** "I couldn't find an order with that number/email. Would you like to try the Order Number again or confirm your last name?" $\rightarrow$ **Return to Step 2/3 (Loop)**

### Step 6: Next Step - Eliciting Return Specifics

With the Order Data now successfully collected and verified, the agent moves on to the second data requirement, which informs the eligibility check.

- **Agent Action:** "Thank you for confirming. Could you please tell me **which item** you want to return and the **reason** (e.g., wrong size, defective, unwanted)?"

This structured flow ensures the agent efficiently gathers the necessary data to bridge the conversational gap with the first crucial technical action: calling the Order Management System tool.

Detailed **Acceptance Criteria for**  the **Eligibility Check**.

That's great! Let's focus on defining the detailed **Acceptance Criteria** for the most critical step in the process: the **Eligibility Check**.

This is vital because it protects your company against unauthorized returns and ensures compliance with your return policy.

## 🎯 Acceptance Criteria for R2: Eligibility Check

The tool-call for eligibility is designed to answer one question definitively: **Can this return proceed?** The agent must rely solely on the result of this tool, not on the LLM's interpretation of the policy.

The functional requirement is: **R2: Eligibility Check**.

- **Description:** Agent must apply business logic (e.g., 30-day window, item type) via a tool-call.

Here are the acceptance criteria for the tool `CheckEligibility(order_id, requested_items, return_reason)`:

| **Scenario** | **Input Parameters** | **Expected Tool Response (is_eligible)** | **Agent Action** |
| --- | --- | --- | --- |
| **Success: Standard Return** | Order date: **20 days ago**. Item: **Shirt**. Reason: **Wrong Size**. | `true` | Proceed to **R3: Label Generation**. |
| **Failure: Expired Window** | Order date: **95 days ago** (Policy: 90 days). Item: **Pants**. Reason: **Unwanted**. | `false` (Reason Code: `TIME_EXP`) | Inform customer: "Return window has closed. Cannot proceed." |
| **Failure: Non-Returnable Item** | Item: **Final Sale Digital Product**. Reason: **Unwanted**. | `false` (Reason Code: `ITEM_EXCL`) | Inform customer: "Item is non-returnable per our final sale policy." |
| **Failure: Partial/Missing Info** | `order_id` is invalid or product list is incomplete. | `false` (Reason Code: `DATA_ERR`) | Prompt customer: "I couldn't find that order. Please confirm the order number or email." |
| **Handoff: Potential Fraud Flag** | Customer history shows **3 returns in the last 30 days**. | `false` (Reason Code: `RISK_MANUAL`) | Inform customer: "I need to connect you with a specialist to review the order." $\rightarrow$ **R6: Human Handoff** |
| **Handoff: Complex Reason** | Reason: **Item arrived broken/defective** (Requires investigation/photo evidence). | `false` (Reason Code: `DAMAGED_MANUAL`) | Inform customer: "I'll connect you with a Quality Control agent for assistance." $\rightarrow$ **R6: Human Handoff** |

---

These criteria ensure that your Engineering team knows exactly what logic to build into the `CheckEligibility` tool and how the AI agent must respond to every possible outcome.

## The need for RAG

Retrieval-Augmented Generation (RAG) is involved in this process in areas that require the LLM to access and synthesize **proprietary, unstructured, or frequently updated knowledge** that isn't suitable for a rigid API tool call or a simple database lookup.

While the core return logic relies on structured tool-calls (like `CheckEligibility()`), RAG shines in providing the necessary **context and personalized language** around those rigid steps.

Here are the key areas where RAG would be involved in the Order Return Request Agent:

---

## 📚 RAG Involvement in the Return Request Process

### 1. **Policy Interpretation & Justification (High-Value Use Case)**

- **The Need:** The `CheckEligibility` tool returns a rigid code (`true`, `false`, `TIME_EXP`, etc.). The LLM needs to translate this code into a **natural, empathetic, and branded explanation** for the customer.
- **RAG's Role:**
    - **Retrieval:** The RAG system queries the **Policy Knowledge Base** (vector database containing PDFs, detailed policy web pages, legal disclaimers, etc.) using the eligibility reason code (e.g., `TIME_EXP`) and the product type as the query context.
    - **Generation:** The LLM uses the retrieved policy excerpts to generate a response like: "I am sorry, but your return window closed 5 days ago. According to our **Standard Return Policy (Section 3.A)**, returns must be initiated within 90 days of the purchase date. However, since you are a Gold Tier member, I can offer you a 10% discount on your next order as an alternative." (The "Gold Tier" detail is also pulled via RAG from the CRM's unstructured data).

### 2. **Handling Exception Cases and Edge Scenarios**

- **The Need:** The agent needs to guide the customer through non-standard return reasons that require human intervention, but the agent must provide a highly specific first response.
- **RAG's Role:**
    - **Scenario:** Customer says, "The **special edition vinyl** I ordered arrived with a split seam on the jacket."
    - **Retrieval:** The RAG system searches the **Internal Troubleshooting Guides** and **Past Resolution Logs** for: "special edition vinyl return," "split seam damage policy," or "logistics claim procedures."
    - **Generation:** The LLM uses the retrieved internal guide to frame the handoff precisely: "I understand. Returns for damaged items like this require us to open a **Logistics Claim (Procedure 4.B)**. I have already drafted the claim based on your description and will now connect you to a specialized Damaged Goods Agent who will ask for a photo of the item and confirm the resolution type."

### 3. **Generating Personalized and Contextual Communication**

- **The Need:** The standard email template for the return label is too generic. The communication should feel personal and proactive.
- **RAG's Role:**
    - **Retrieval:** RAG pulls unstructured data from the **Customer History Knowledge Base** (past chat transcripts, survey results, loyalty program notes).
    - **Generation:** The LLM incorporates the retrieved context into the final response: "Your return label for the **Red T-Shirt (Size M)** is attached. Since you mentioned in your last survey that you value speed, we’ve prioritized this RMA (**RMA1234**) for expedited processing once it reaches the warehouse."

### 4. **Internal Agent Support (Copilot Mode)**

- **The Need:** When the AI escalates to a human agent, the human agent needs a quick, comprehensive summary of the AI's actions.
- **RAG's Role:**
    - **Retrieval:** The RAG system retrieves the *entire conversation history*, all *tool-call results* (including the failed `CheckEligibility` logs), and any *intermediate LLM reasoning steps*.
    - **Generation:** The RAG system generates a concise, 3-sentence summary for the human agent's dashboard: "Customer attempting return for Order \#567. Agent determined item was outside the 90-day window (`TIME_EXP`). Customer conversation sentiment is **Frustrated**. Recommend offering an exception or store credit."

In summary, RAG acts as the **source of flexible, domain-specific wisdom**, preventing the LLM from hallucinating answers related to company policy and enabling it to provide accurate, personalized communication around the rigid, transactional tool-calls.

---

The agent must be trained to handle not just the perfect, structured query, but also the messy, conversational requests.

Here are 5 examples of real-world user queries that your tool-calling AI agent, following the multi-step flow, can successfully resolve:

---

## 💬 5 Real-World User Queries for the Agent

### Example 1: Standard, Eligible Return (Happy Path)

This is the ideal scenario where the agent executes all tools successfully and automatically.

- **User Query:**
    
    > "I need to return the hiking boots I bought a few weeks ago, order #77893. They're just too small and I need to send them back for a refund."
    > 
- **Agent Execution Flow:**
    1. **Intent/Data:** Identifies "return" intent and captures Order ID (`#77893`).
    2. **Tool-Call 1 (`GetOrderDetails`):** Retrieves order details (purchased 15 days ago, item: 'Hiking Boots', size 10).
    3. **Tool-Call 2 (`CheckEligibility`):** Determines: (1) Within 30-day window? **Yes**. (2) Non-final sale item? **Yes**. $\rightarrow$ **Eligible.**
    4. **Tool-Call 3 (`GenerateReturnLabel`):** Creates RMA and a prepaid shipping label.
    5. **Agent Resolution:** Provides the RMA number and immediately emails the prepaid label and return instructions.

### Example 2: Ineligible Return (Policy Enforcement)

This tests the agent's ability to politely enforce policy, relying strictly on the `CheckEligibility` tool.

- **User Query:**
    
    > "I bought a jacket last summer and it's too big. I want to return it. The order number is #45110."
    > 
- **Agent Execution Flow:**
    1. **Intent/Data:** Identifies "return" intent, captures Order ID (`#45110`).
    2. **Tool-Call 1 (`GetOrderDetails`):** Retrieves order details (purchased 185 days ago).
    3. **Tool-Call 2 (`CheckEligibility`):** Determines: (1) Within 90-day window? **No**. $\rightarrow$ **Ineligible (TIME_EXP).**
    4. **Agent Resolution:** Politely informs the user: "I'm sorry, Order #45110 was placed 185 days ago. According to our policy, we can only accept returns within 90 days. Unfortunately, I cannot process this return." (May offer an alternative, like a small credit, based on RAG policy lookup).

### Example 3: Missing Order Details (Elicitation & Lookup)

This tests the agent's data-elicitation flow and its ability to use a fallback key (email).

- **User Query:**
    
    > "I lost my receipt but I need to send back the toaster I bought. I think I used my [user's email address]."
    > 
- **Agent Execution Flow:**
    1. **Intent/Data:** Identifies "return" intent, missing Order ID, captures email address.
    2. **Tool-Call 1 (`GetOrderDetails`):** Attempts lookup using email.
    3. **Tool Response:** Returns a list of the last two orders associated with the email: Order #90123 (Toaster, 45 days ago) and Order #88765 (Coffee Maker, 10 days ago).
    4. **Agent Elicitation:** "I found two recent orders. Was it the **Toaster** from 45 days ago or the **Coffee Maker** from 10 days ago?"
    5. **User Response:** "The Toaster."
    6. **Tool-Call 2 (`CheckEligibility`):** Confirms the Toaster is eligible.
    7. **Agent Resolution:** Proceeds to generate and send the return label for the correct item.

### Example 4: Complex Reason Requiring Handoff (Safety Net Trigger)

This tests the agent's escalation logic based on the *reason* for the return.

- **User Query:**
    
    > "The package arrived totally ripped open and the electronics inside are shattered. Order #10552."
    > 
- **Agent Execution Flow:**
    1. **Intent/Data:** Identifies "return" intent, captures Order ID (`#10552`), and classifies the reason as **"Damaged/Defective."**
    2. **Tool-Call 2 (`CheckEligibility`):** Logic is coded to return **Ineligible** with a reason code of **`DAMAGED_MANUAL`** for all "damaged" requests.
    3. **Agent Escalation (R6):** Triggers the Human Handoff. "I'm very sorry to hear that. A damaged item requires us to file an immediate shipping claim. I am connecting you with our **Claims Specialist** now, and I've already shared your full chat history and order details so you don't have to repeat yourself."

### Example 5: Asking for Refund Status (Information Retrieval)

This tests the agent's ability to act as a look-up tool *after* a return has been initiated, requiring a check against a logistics or refund tool.

- **User Query:**
    
    > "I sent my return back last week using RMA RMA4567. Has my refund been processed yet?"
    > 
- **Agent Execution Flow:**
    1. **Intent/Data:** Identifies "Refund Status" intent, captures RMA (`RMA4567`).
    2. **Tool-Call (`CheckRefundStatus` - new tool!):** Executes a query to the Payment Gateway and Logistics APIs using the RMA number.
    3. **Tool Response:** Returns status: **"Item received at warehouse on 12/10. Refund initiated 12/11. Expected to post within 3-5 business days."**
    4. **Agent Resolution:** "Thank you for the RMA. I can confirm your package was received yesterday, and the **refund was initiated this morning**. You should see the funds reflected in your bank account within the next 3 to 5 business days."