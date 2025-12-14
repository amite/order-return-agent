# ChromaDB & RAG Knowledge Base - Complete Guide

This guide teaches you how to use the ChromaDB implementation in this project for semantic search and retrieval-augmented generation (RAG).

## Table of Contents

1. [Quick Start](#quick-start)
2. [Core Concepts](#core-concepts)
3. [API Methods](#api-methods)
4. [Usage Examples](#usage-examples)
5. [Integration Patterns](#integration-patterns)
6. [Troubleshooting](#troubleshooting)
7. [API Reference](#api-reference)

---

## Quick Start

### 1. Initialize and Ingest Documents

```python
from src.rag.knowledge_base import KnowledgeBase

# Initialize (connects to ChromaDB, sets up embeddings)
kb = KnowledgeBase()

# Ingest documents (one-time setup, or when you update knowledge base)
doc_count = kb.ingest_documents()
print(f"Ingested {doc_count} documents")  # Should print: "Ingested 4 documents"
```

### 2. Basic Query

```python
# Query for information
results = kb.query("return policy for electronics")
for doc in results:
    print(f"Source: {doc.metadata['source']}")
    print(f"Content: {doc.page_content[:200]}...")
```

### 3. Health Check

```python
# Verify system is working
if kb.health_check():
    print("✅ Knowledge base is ready!")
else:
    print("❌ Need to ingest documents")
    kb.ingest_documents()
```

---

## Core Concepts

### What is ChromaDB?

ChromaDB is a vector database that stores documents as **embeddings** (numerical representations) that capture semantic meaning. This allows you to search by **meaning**, not just keywords.

### How It Works in This Project

1. **Documents** → Markdown files in `data/knowledge_base/`
2. **Chunking** → Split into 500-character chunks with 50-character overlap
3. **Embedding** → Convert to vectors using Ollama (`mxbai-embed-large`)
4. **Storage** → Persist in ChromaDB at `data/chroma_db/`
5. **Query** → Semantic search returns most relevant chunks

### Key Components

- **Vector Store**: ChromaDB collection (`order_return_kb`)
- **Embeddings**: Ollama embeddings model
- **Documents**: 4 knowledge base markdown files
- **Chunks**: 73 searchable pieces from those documents

---

## API Methods

### 1. `query(query_text: str, top_k: Optional[int] = None) -> list[Document]`

**Purpose**: General semantic search across all documents

**Parameters**:
- `query_text`: Natural language query string
- `top_k`: Number of results (default: 3 from settings)

**Returns**: List of `Document` objects with:
- `page_content`: The text content
- `metadata`: Dictionary with `source` (filename) and `path` (full path)

**Example**:
```python
results = kb.query("return policy electronics 90 days")
for doc in results:
    print(f"From {doc.metadata['source']}: {doc.page_content[:100]}")
```

---

### 2. `get_policy_context(reason_code: str) -> str`

**Purpose**: Get policy explanation for specific eligibility reason codes

**Parameters**:
- `reason_code`: One of:
  - `"TIME_EXP"` - Return window expired
  - `"ITEM_EXCL"` - Item not returnable (final sale)
  - `"DAMAGED_MANUAL"` - Damaged items need escalation
  - `"RISK_MANUAL"` - Fraud/high returns need review
  - `"DATA_ERR"` - Missing order information

**Returns**: Formatted policy context string

**Example**:
```python
from src.models.enums import EligibilityReasonCode

if eligibility_result.reason_code == EligibilityReasonCode.TIME_EXP:
    policy_explanation = kb.get_policy_context("TIME_EXP")
    # Use to explain to customer why return was rejected
```

---

### 3. `get_communication_template(scenario: str) -> str`

**Purpose**: Retrieve response templates for consistent customer communication

**Parameters**:
- `scenario`: Communication scenario:
  - `"approval"` - Return approved
  - `"rejection"` - Return rejected
  - `"escalation"` - Needs human review
  - `"partial_refund"` - Partial refund scenario
  - `"exchange"` - Exchange scenario

**Returns**: Communication template string

**Example**:
```python
if eligibility_result.reason_code == EligibilityReasonCode.APPROVED:
    template = kb.get_communication_template("approval")
    message = template.format(
        customer_name="John Doe",
        order_id="ORD-12345",
    )
```

---

### 4. `get_exception_guidance(exception_type: str) -> str`

**Purpose**: Get guidance for handling specific exceptions or edge cases

**Parameters**:
- `exception_type`: Type of exception:
  - `"damaged"` - Damaged items
  - `"fraud"` - Fraud prevention
  - `"compassionate"` - Compassionate circumstances
  - `"high_value"` - High-value items
  - `"customized"` - Customized items

**Returns**: Exception handling guidance string

**Example**:
```python
guidance = kb.get_exception_guidance("damaged")
# Use to guide agent on how to handle damaged item returns
```

---

### 5. `health_check() -> bool`

**Purpose**: Verify knowledge base is properly initialized and accessible

**Returns**: `True` if healthy, `False` otherwise

**Example**:
```python
if not kb.health_check():
    print("Re-initializing...")
    kb.ingest_documents()
```

---

### 6. `ingest_documents() -> int`

**Purpose**: Load and ingest all knowledge base documents into vector store

**Returns**: Number of documents ingested

**When to use**:
- First-time setup
- After updating knowledge base markdown files
- If vector store is corrupted

**Example**:
```python
count = kb.ingest_documents()
print(f"Successfully ingested {count} documents")
```

---

## Usage Examples

### Example 1: General Information Retrieval

```python
from src.rag.knowledge_base import KnowledgeBase

kb = KnowledgeBase()
if not kb.health_check():
    kb.ingest_documents()

# Search for information
results = kb.query("What is the return policy for electronics?", top_k=5)

# Process results
for i, doc in enumerate(results, 1):
    print(f"\n--- Result {i} ---")
    print(f"Source: {doc.metadata['source']}")
    print(f"Content: {doc.page_content}")
```

### Example 2: Policy Context for Rejection

```python
from src.rag.knowledge_base import KnowledgeBase
from src.models.enums import EligibilityReasonCode

kb = KnowledgeBase()

# When eligibility check fails
reason_code = "TIME_EXP"  # or from EligibilityReasonCode.TIME_EXP

# Get policy explanation
policy_context = kb.get_policy_context(reason_code)

# Get rejection template
rejection_template = kb.get_communication_template("rejection")

# Combine for customer response
customer_message = f"{rejection_template}\n\nPolicy Details:\n{policy_context}"
```

### Example 3: Exception Handling

```python
from src.rag.knowledge_base import KnowledgeBase

kb = KnowledgeBase()

# Get guidance for specific exception
guidance = kb.get_exception_guidance("damaged")

# Use in agent logic
if item_condition == "damaged":
    handling_instructions = kb.get_exception_guidance("damaged")
    # Follow instructions from guidance
```

### Example 4: Complete Agent Integration Pattern

```python
from src.rag.knowledge_base import KnowledgeBase
from src.models.enums import EligibilityReasonCode

class ReturnAgent:
    def __init__(self):
        # Initialize RAG during agent startup
        self.kb = KnowledgeBase()
        if not self.kb.health_check():
            self.kb.ingest_documents()
    
    def handle_return_request(self, eligibility_result):
        """Handle return request with RAG support"""
        
        if eligibility_result.reason_code == EligibilityReasonCode.APPROVED:
            # Get approval template
            template = self.kb.get_communication_template("approval")
            return template
        
        elif eligibility_result.reason_code == EligibilityReasonCode.TIME_EXP:
            # Get policy explanation and rejection template
            policy = self.kb.get_policy_context("TIME_EXP")
            template = self.kb.get_communication_template("rejection")
            return f"{template}\n\n{policy}"
        
        elif eligibility_result.reason_code == EligibilityReasonCode.DAMAGED_MANUAL:
            # Get exception guidance
            guidance = self.kb.get_exception_guidance("damaged")
            template = self.kb.get_communication_template("escalation")
            return f"{template}\n\n{guidance}"
```

---

## Integration Patterns

### Pattern 1: Agent Initialization

Always initialize RAG during agent startup:

```python
def __init__(self):
    self.kb = KnowledgeBase()
    if not self.kb.health_check():
        logger.info("Ingesting knowledge base documents...")
        self.kb.ingest_documents()
```

### Pattern 2: Policy Explanation on Rejection

When eligibility check fails, explain why:

```python
def explain_rejection(self, reason_code: str) -> str:
    policy_context = self.kb.get_policy_context(reason_code)
    template = self.kb.get_communication_template("rejection")
    return f"{template}\n\nPolicy: {policy_context}"
```

### Pattern 3: Template-Based Responses

Use templates for consistent communication:

```python
def send_approval_message(self, customer_name: str, order_id: str):
    template = self.kb.get_communication_template("approval")
    # Templates may have placeholders - check your knowledge base
    return template  # or format with variables if needed
```

### Pattern 4: Exception Handling

Use guidance for edge cases:

```python
def handle_exception(self, exception_type: str):
    guidance = self.kb.get_exception_guidance(exception_type)
    # Follow guidance in agent logic
    return guidance
```

---

## Troubleshooting

### Issue: "Vector store not initialized"

**Solution**:
```python
kb = KnowledgeBase()
kb.ingest_documents()  # This initializes the vector store
```

### Issue: "No results returned"

**Check**:
1. Is Ollama running?
   ```bash
   cd /home/amite/code/docker/ollama-docker && docker compose ps
   ```
2. Is the embedding model available?
   ```bash
   docker compose exec ollama ollama list
   ```
3. Have documents been ingested?
   ```python
   if not kb.health_check():
       kb.ingest_documents()
   ```

### Issue: "Health check fails"

**Solution**:
```python
# Re-initialize
kb = KnowledgeBase()
kb.ingest_documents()
assert kb.health_check()  # Should be True now
```

### Issue: Need to reset vector store

**Solution**:
```python
import shutil
from pathlib import Path

# Remove old data
chroma_path = Path("data/chroma_db")
if chroma_path.exists():
    shutil.rmtree(chroma_path)

# Re-initialize and ingest
kb = KnowledgeBase()
kb.ingest_documents()
```

---

## Configuration

Settings are in `src/config/settings.py`:

```python
# RAG Configuration
rag_top_k: int = 3                    # Number of results to return
rag_chunk_size: int = 500             # Size of text chunks
rag_chunk_overlap: int = 50           # Overlap between chunks
rag_similarity_threshold: float = 0.7  # Minimum similarity (not used yet)

# ChromaDB Configuration
chroma_persist_dir: str = "data/chroma_db"
chroma_collection_name: str = "order_return_kb"

# Ollama Configuration
ollama_base_url: str = "http://localhost:11434"
ollama_embedding_model: str = "mxbai-embed-large:latest"
```

---

## API Reference

For detailed API documentation, see:
- **[API Reference](./api_reference.md)** - Complete API documentation from Context7
- **[Example Scripts](./scripts/)** - Runnable code examples

---

## Next Steps

1. **Run the example scripts** in `scripts/` folder
2. **Experiment** with different queries and parameters
3. **Integrate** into your agent code
4. **Review** the API reference for advanced features

---

## Resources

- **Project Implementation**: `src/rag/knowledge_base.py`
- **Tests**: `tests/test_rag.py` (27 comprehensive tests)
- **Knowledge Base Files**: `data/knowledge_base/*.md`
- **ChromaDB Storage**: `data/chroma_db/`
