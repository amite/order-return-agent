# Context7 and Docs-LangChain Guidelines

**For AI developers implementing features in this project**

---

## Problem We Encountered

During Phase 1 RAG implementation, we spent **~4 hours troubleshooting import issues** that could have been **entirely prevented** by consulting official documentation first.

**Issues that occurred:**
- ❌ Using `langchain.schema.Document` (module reorganized)
- ⚠️ Using deprecated `langchain_community.embeddings.OllamaEmbeddings`
- ❌ Assuming `langchain_chroma` package exists (it doesn't)
- ⚠️ Concerns about import order and circular dependencies

**Root cause**: Relied on internal knowledge rather than checking official documentation

---

## The Solution: Use Official Documentation Tools

### Rule 1: LangChain Questions → docs-langchain

**When**: Any question about LangChain imports, APIs, or features
**How**: Use `mcp__docs-langchain__SearchDocsByLangChain` tool
**Example Query**: "OllamaEmbeddings import path"
**Benefit**: Always get official, up-to-date information

```python
# Instead of guessing:
# from langchain_community.embeddings import OllamaEmbeddings  ❌

# Use docs-langchain first:
# Query: "OllamaEmbeddings import"
# Result: Official LangChain docs show:
# from langchain_ollama import OllamaEmbeddings  ✅
```

### Rule 2: Other Libraries → context7

**When**: Integrating new libraries or uncertain about API
**How**:
1. Use `mcp__context7__resolve-library-id` to find library
2. Use `mcp__context7__get-library-docs` to get documentation
**Example**: ChromaDB, SQLAlchemy, Pydantic, etc.
**Benefit**: Get official, version-specific documentation

```python
# Before implementing:
# 1. Resolve: mcp__context7__resolve-library-id("chromadb")
# 2. Get docs: mcp__context7__get-library-docs(library_id)
# Result: Know exact API and import paths for your version
```

---

## Where These Rules Are Documented

### Project Instructions
**File**: `CLAUDE.md` (in project root)
- Section: "Rules > Documentation Lookups"
- LangChain rule with examples
- Library documentation rule with benefits
- Ollama Docker command requirement

### Implementation Artifacts
**Files**: `artifacts/wip/issues/`
- `IMPORT_QUICK_REFERENCE.md` - How to find import information
- `LANGCHAIN_IMPORT_CHALLENGES.md` - Note for AI developers

---

## How These Rules Would Have Prevented Issues

### Issue #1: Document Import
**Without rule**: Used outdated path `langchain.schema.Document`
**With rule**: docs-langchain would show `langchain_core.documents.Document` immediately

### Issue #2: OllamaEmbeddings Deprecation
**Without rule**: Used deprecated `langchain_community.embeddings.OllamaEmbeddings`
**With rule**: docs-langchain would show deprecation warning and recommend `langchain_ollama`

### Issue #3: ChromaDB Package
**Without rule**: Assumed `langchain_chroma` exists
**With rule**: docs-langchain or context7 would clarify package structure

### Issue #4: Import Order
**Without rule**: Spent time worrying about circular dependencies
**With rule**: Official docs would explain import architecture

**Total time saved**: ~4 hours of troubleshooting

---

## Implementation Steps

### Before Writing Code That Uses a Library:

1. **Identify the library** (LangChain, ChromaDB, etc.)

2. **Check appropriate tool**:
   ```
   Is it LangChain?
   ├─ YES → Use docs-langchain
   │        Query: What you want to do
   │        Get: Official LangChain docs
   │
   └─ NO → Use context7
            Step 1: Resolve library ID
            Step 2: Get library docs
   ```

3. **Review official documentation**
   - Read import statements
   - Check for deprecation warnings
   - Understand version-specific features
   - Note any breaking changes

4. **Test imports early**
   ```bash
   python -c "from module import Class"
   ```

5. **Then write your code**
   - Confident in correct import paths
   - Aware of deprecations
   - Using official APIs

---

## Tool Usage Examples

### LangChain Example

**Task**: Implement RAG with ChromaDB and Ollama embeddings

```python
# Step 1: Check docs-langchain for ChromaDB integration
# Query: "ChromaDB langchain import vectorstore"
# Result: Use langchain_community.vectorstores.Chroma

# Step 2: Check docs-langchain for Ollama embeddings
# Query: "Ollama embeddings import"
# Result: Use langchain_ollama.OllamaEmbeddings

# Step 3: Check docs-langchain for Document class
# Query: "Document import langchain"
# Result: Use langchain_core.documents.Document

# Now write code with confidence:
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# All imports are correct because verified against official docs ✅
```

### Context7 Example

**Task**: Use ChromaDB library

```python
# Step 1: Resolve ChromaDB library
# mcp__context7__resolve-library-id("chromadb")
# Result: Library ID for ChromaDB

# Step 2: Get official documentation
# mcp__context7__get-library-docs(library_id)
# Result: Official ChromaDB docs for your version

# Step 3: Check API and import paths
# Confirm correct usage for your version
# Note any deprecations or breaking changes

# Now write code:
from chromadb import Client
client = Client()  # Using official API
```

---

## When to Use Each Tool

### Use docs-langchain for:
- ✅ Import paths for LangChain modules
- ✅ LangChain agent creation
- ✅ Tool definitions and schemas
- ✅ Memory and conversation management
- ✅ Integration patterns
- ✅ Deprecation warnings and migrations

### Use context7 for:
- ✅ ChromaDB API and usage
- ✅ SQLAlchemy queries and models
- ✅ Pydantic v1 vs v2 differences
- ✅ Any other library's official API
- ✅ Version-specific features
- ✅ Breaking changes between versions

### Don't use internal knowledge for:
- ❌ LangChain imports (too many changes)
- ❌ Deprecation status (might be outdated)
- ❌ Version-specific features (knowledge cutoff)
- ❌ Breaking changes (need current info)

---

## Integration into Development Workflow

### Phase 2 (Agent Orchestration)
Before implementing `src/agents/return_agent.py`:
1. Query docs-langchain: "Create LangChain agent with tools"
2. Query docs-langchain: "ChatOllama import"
3. Query docs-langchain: "Agent memory and conversation"
4. Then write code with official guidance

### Phase 3 (Main Application)
Before implementing `src/main.py`:
1. Query docs-langchain: "LangChain session management"
2. Query context7: "Database connection patterns"
3. Query context7: "Configuration best practices"
4. Then write code with confidence

### Phase 4 (Testing)
When writing tests:
1. Query docs-langchain: "How to test LangChain agents"
2. Query context7: "Pytest best practices"
3. Query context7: "Mock patterns for libraries"
4. Then write comprehensive tests

---

## Prevention Checklist

Before implementing ANY feature with external libraries:

- [ ] **Is LangChain involved?** → Use docs-langchain first
- [ ] **Using a new library?** → Use context7 first
- [ ] **Unsure about import path?** → Check official docs
- [ ] **Seen deprecation warnings?** → Read full warning, check docs
- [ ] **Need version-specific info?** → Use context7 for that version
- [ ] **Writing new integration?** → Start with official examples
- [ ] **Encountered error?** → Check official docs before debugging

---

## How to Enable These Rules

### In CLAUDE.md
The rules are documented in the project's `CLAUDE.md` file:
- Section: "Rules > Documentation Lookups"
- Read this before starting Phase 2

### In Your Development Process
1. Bookmark this file
2. Check it before implementing LangChain features
3. Share with team members working on this project
4. Update with new learnings

---

## Key Takeaways

### What We Learned
1. **Official docs are faster** than troubleshooting
2. **Documentation tools prevent errors** before they happen
3. **Version-specific info** is critical for library integration
4. **Deprecation warnings** come from official sources

### What to Remember
- Use docs-langchain **before** writing LangChain code
- Use context7 **before** integrating new libraries
- Test imports **early** after consulting docs
- Never ignore **deprecation warnings**

### Going Forward
- Phase 2 developers: Use these rules religiously
- Future developers: Follow the pattern
- New libraries: Always check official docs first
- Bug investigations: Start with official documentation

---

## References

### Documentation Tools
- [docs-langchain MCP Server](../../../) - Search LangChain documentation
- [context7 MCP Server](../../../) - Get library documentation

### Project Rules
- `CLAUDE.md` - Main rules for this project
- `IMPORT_QUICK_REFERENCE.md` - Quick import lookup
- `IMPORT_TROUBLESHOOTING.md` - Debugging guide

### Related Documentation
- `LANGCHAIN_IMPORT_CHALLENGES.md` - What went wrong (and how to prevent it)
- `RAG_IMPLEMENTATION_COMPLETE.md` - Example of correct implementation
- `PHASE_1_SUMMARY.md` - Phase 1 completion status

---

## Questions?

**If facing an import error:**
1. Check docs-langchain first (if LangChain)
2. Check context7 first (if other library)
3. Test import with `python -c`
4. Reference working examples (`src/rag/knowledge_base.py`)

**If implementing new feature:**
1. Identify external libraries needed
2. Query appropriate documentation tool
3. Review official guidance
4. Write code confidently
5. Test imports early

---

## Final Note

This document exists because we learned these lessons the hard way. Following the rules documented here will:
- **Save time**: No more import troubleshooting
- **Prevent errors**: Use official APIs from start
- **Scale better**: Easier to integrate new libraries
- **Help team**: Consistent, documented approach

**For Phase 2+**: Use these tools FIRST, before writing code. You'll thank yourself later.

---

**Last Updated**: 2025-12-14
**Status**: Official project guidelines ✅
