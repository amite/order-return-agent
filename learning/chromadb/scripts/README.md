# ChromaDB Example Scripts

This folder contains runnable example scripts demonstrating different aspects of using ChromaDB in this project.

## Scripts Overview

### 01_basic_usage.py
**Purpose**: Fundamental operations - initialization, ingestion, basic queries

**What it demonstrates**:
- Initializing KnowledgeBase
- Health checks
- Document ingestion
- Basic querying
- Displaying results

**Run**:
```bash
uv run python learning/chromadb/scripts/01_basic_usage.py
```

---

### 02_query_examples.py
**Purpose**: Various query patterns and use cases

**What it demonstrates**:
- Policy-related queries
- Time-based queries
- Item-specific queries
- Exception handling queries
- Custom top_k values

**Run**:
```bash
uv run python learning/chromadb/scripts/02_query_examples.py
```

---

### 03_policy_context.py
**Purpose**: Retrieving policy explanations for eligibility reason codes

**What it demonstrates**:
- All supported reason codes (TIME_EXP, ITEM_EXCL, etc.)
- Policy context retrieval
- Using in agent logic

**Run**:
```bash
uv run python learning/chromadb/scripts/03_policy_context.py
```

---

### 04_templates.py
**Purpose**: Communication template retrieval

**What it demonstrates**:
- Different communication scenarios
- Template retrieval
- Using templates in responses

**Run**:
```bash
uv run python learning/chromadb/scripts/04_templates.py
```

---

### 05_exception_handling.py
**Purpose**: Exception handling guidance

**What it demonstrates**:
- Different exception types
- Guidance retrieval
- Using guidance in agent logic

**Run**:
```bash
uv run python learning/chromadb/scripts/05_exception_handling.py
```

---

### 06_complete_demo.py
**Purpose**: Complete workflow demonstration

**What it demonstrates**:
- Full initialization workflow
- All major operations
- Simulated agent workflow
- Integration patterns

**Run**:
```bash
uv run python learning/chromadb/scripts/06_complete_demo.py
```

---

## Prerequisites

Before running any script, ensure:

1. **Ollama is running**:
   ```bash
   cd /home/amite/code/docker/ollama-docker && docker compose ps
   ```

2. **Embedding model is available**:
   ```bash
   docker compose exec ollama ollama list
   ```
   Should show `mxbai-embed-large:latest`

3. **Knowledge base files exist**:
   - `data/knowledge_base/return_policy.md`
   - `data/knowledge_base/exception_handling.md`
   - `data/knowledge_base/communication_templates.md`
   - `data/knowledge_base/troubleshooting_guide.md`

## Running Scripts

### Run a single script:
```bash
uv run python learning/chromadb/scripts/01_basic_usage.py
```

### Run all scripts in order:
```bash
for script in learning/chromadb/scripts/*.py; do
    echo "Running $script..."
    uv run python "$script"
    echo ""
done
```

## Expected Output

Each script will:
1. Initialize the KnowledgeBase
2. Check health and ingest if needed
3. Demonstrate the specific feature
4. Display results in a readable format

## Troubleshooting

### Script fails with "Vector store not initialized"
- The script will automatically ingest documents if needed
- If it still fails, manually run: `kb.ingest_documents()`

### Script fails with connection error
- Check Ollama is running: `docker compose ps`
- Verify Ollama URL in `.env`: `ollama_base_url=http://localhost:11434`

### No results returned
- Ensure documents have been ingested
- Check `kb.health_check()` returns `True`
- Try re-ingesting: `kb.ingest_documents()`

## Learning Path

Recommended order for learning:

1. **Start here**: `01_basic_usage.py` - Learn the fundamentals
2. **Explore queries**: `02_query_examples.py` - See different query patterns
3. **Policy context**: `03_policy_context.py` - Understand policy lookups
4. **Templates**: `04_templates.py` - Learn about communication templates
5. **Exceptions**: `05_exception_handling.py` - Handle edge cases
6. **Complete demo**: `06_complete_demo.py` - See it all together

## Next Steps

After running these scripts:

1. Read the main [README.md](../README.md) for detailed documentation
2. Review the [API Reference](../api_reference.md) for complete API details
3. Integrate into your agent code
4. Experiment with your own queries and use cases

## Modifying Scripts

Feel free to modify these scripts to:
- Test your own queries
- Experiment with different parameters
- Try different scenarios
- Debug issues
- Learn by doing

All scripts are well-commented and designed to be educational.
