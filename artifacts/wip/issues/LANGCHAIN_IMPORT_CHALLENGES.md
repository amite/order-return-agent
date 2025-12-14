# LangChain Library Import Challenges & Solutions

**Date**: 2025-12-14
**Phase**: Phase 1 - RAG Implementation
**Status**: Resolved ✅

## Overview

During implementation of the RAG knowledge base system, several challenges arose related to LangChain library imports. This document details the issues encountered, their root causes, solutions applied, and lessons learned for future development.

---

## Issue #1: Incorrect Document Import Path

### Problem Statement

**Error**:
```
ModuleNotFoundError: No module named 'langchain.schema'
```

**Location**: `src/rag/knowledge_base.py:9`
```python
from langchain.schema import Document  # ❌ WRONG
```

### Root Cause

The `langchain.schema` module was removed in newer versions of LangChain (v0.1+). The library restructured its core types into separate packages:
- **Old location** (v0.0.x): `langchain.schema.Document`
- **New location** (v0.1+): `langchain_core.documents.Document`

The project's `pyproject.toml` specified `langchain-core>=1.2.0`, which is a modern version where this reorganization is complete.

### Solution Applied

Changed the import to use the correct module:
```python
from langchain_core.documents import Document  # ✅ CORRECT
```

### Why This Works

- `langchain-core` is the foundational package that contains all core types
- It's explicitly installed in the project (`langchain-core>=1.2.0`)
- This is the official location for base classes in modern LangChain

### Lesson Learned

**Always check the installed version and official documentation**
- LangChain has undergone significant architectural changes
- Core types moved from `langchain` to `langchain_core`
- Community integrations are in `langchain_community`
- Model-specific packages (Ollama, OpenAI, etc.) are in separate packages

---

## Issue #2: Deprecated Embeddings Import

### Problem Statement

**Deprecation Warning**:
```
LangChainDeprecationWarning: The class `OllamaEmbeddings` was deprecated in
LangChain 0.3.1 and will be removed in 1.0.0. An updated version of the class
exists in the `langchain-ollama package and should be used instead.
```

**Initial Code**:
```python
from langchain_community.embeddings import OllamaEmbeddings  # ⚠️ DEPRECATED
```

### Root Cause

LangChain deprecated integrations from `langchain_community` in favor of vendor-specific packages:
- Ollama integrations were moved to `langchain-ollama`
- OpenAI integrations were moved to `langchain-openai`
- Anthropic integrations were moved to `langchain-anthropic`
- This separation allows better version control and focused dependencies

### First Attempt to Fix

Tried to use the new package:
```python
from langchain_ollama import OllamaEmbeddings  # ✅ Correct package
```

However, this required checking if `langchain-ollama` was installed.

### Verification

**Command executed**:
```bash
uv pip show langchain-ollama
```

**Result**: Package was already installed (as per `pyproject.toml`)

### Final Solution

Use the new import path:
```python
from langchain_ollama import OllamaEmbeddings  # ✅ CORRECT
```

### Why This Works

- `langchain-ollama` is the official package for Ollama integrations
- It's a dedicated package that can evolve independently
- Better separation of concerns (Ollama-specific code stays in Ollama package)
- Reduces bloat in `langchain_community` which was becoming too large

### Lesson Learned

**Deprecation warnings should not be ignored**
- They indicate upcoming breaking changes
- Best practice: fix deprecations early, not later
- Always use the officially recommended replacement package
- Check release notes for migration paths

---

## Issue #3: Missing ChromaDB Package Integration

### Problem Statement

**Error**:
```
ModuleNotFoundError: No module named 'langchain_chroma'
```

**Attempted Code**:
```python
from langchain_chroma import Chroma  # ❌ Package doesn't exist
```

### Root Cause

Similar to the Ollama issue, ChromaDB integrations could potentially be in a separate package (`langchain-chroma`), but:
1. The package is **not installed** in the project
2. `pyproject.toml` shows `chromadb>=1.3.7` (the ChromaDB library itself)
3. LangChain's ChromaDB wrapper is in `langchain_community.vectorstores`

This was a misunderstanding of the packaging pattern based on the Ollama experience.

### Solution Applied

Reverted to the available import:
```python
from langchain_community.vectorstores import Chroma  # ✅ Available
```

### Verification

Confirmed that:
1. `langchain_community>=0.4.1` is installed
2. It provides the Chroma vectorstore wrapper
3. The wrapper works with the standalone `chromadb` library

### Why This Works

- `langchain_community.vectorstores.Chroma` is a wrapper around the ChromaDB library
- It provides the LangChain integration layer
- The underlying `chromadb` package (v1.3.7) is installed separately
- This is the correct approach when a dedicated package doesn't exist

### Lesson Learned

**Not all integrations follow the same pattern**
- Some libraries have dedicated LangChain packages (Ollama, OpenAI, Anthropic)
- Others use the community wrapper (`langchain_community`)
- Check what's installed before assuming a pattern
- Use `uv pip show` to verify package availability
- The existence of deprecation warnings doesn't guarantee a replacement package exists

---

## Issue #4: Import Order and Circular Dependencies

### Problem Statement

**Initial Concern**: Would importing from multiple sources cause circular dependencies?

**Original approach**:
```python
from langchain_ollama import OllamaEmbeddings           # From ollama package
from langchain_community.vectorstores import Chroma    # From community package
from langchain_text_splitters import ...               # From text splitters
from langchain_core.documents import Document          # From core package
```

### Root Cause

Different imports from different LangChain packages raised concerns about circular imports or version conflicts.

### Investigation Performed

Tested all imports together in actual implementation - **no issues found**.

### Why This Works

**LangChain Architecture**:
- `langchain_core`: Base types and abstractions (no external dependencies)
- `langchain_community`: Generic integrations (depends on `langchain_core`)
- `langchain_ollama`: Ollama-specific (depends on `langchain_core`)
- `langchain_text_splitters`: Text processing (depends on `langchain_core`)

All packages depend on `langchain_core` as a common base, preventing circular dependencies.

### Lesson Learned

**Understand the dependency hierarchy**
- Core → Utilities → Specific integrations
- All packages converge on `langchain_core`
- This is a healthy architecture that prevents circular dependencies
- Mixing packages from different layers is safe

---

## Solution Summary Table

| Issue | Old Import | New Import | Package | Status |
|-------|-----------|-----------|---------|--------|
| Document class | `langchain.schema` | `langchain_core.documents` | `langchain-core` | ✅ Fixed |
| OllamaEmbeddings | `langchain_community.embeddings` | `langchain_ollama` | `langchain-ollama` | ✅ Fixed |
| Chroma wrapper | `langchain_chroma` (n/a) | `langchain_community.vectorstores` | `langchain_community` | ✅ Correct |
| RecursiveCharacterTextSplitter | (works as-is) | `langchain_text_splitters` | `langchain-text-splitters` | ✅ Works |

---

## Best Practices Established

### 1. **Always Check Installed Packages**
```bash
# Before assuming a package exists, verify:
uv pip show package-name

# See all installed LangChain packages:
uv pip list | grep langchain
```

### 2. **Refer to Official Documentation**
- Each LangChain package has its own docs
- `langchain-ollama` docs ≠ `langchain_community` docs
- Always check the right package's documentation

### 3. **Handle Deprecation Warnings Proactively**
```python
# BAD: Ignore the warning
from langchain_community.embeddings import OllamaEmbeddings

# GOOD: Use the recommended replacement
from langchain_ollama import OllamaEmbeddings
```

### 4. **Test Import Paths Early**
```python
# Before writing lots of code, verify:
try:
    from langchain_ollama import OllamaEmbeddings
    print("✅ Import successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
```

### 5. **Understand Package Structure**
```
langchain-core          # Base types (Document, BaseModel, etc.)
  ├── langchain_community  # Generic integrations
  │   └── vectorstores (Chroma, Pinecone, etc.)
  │   └── embeddings (but deprecated - use vendor packages)
  ├── langchain-ollama   # Ollama-specific
  │   ├── OllamaEmbeddings
  │   └── ChatOllama
  ├── langchain-openai   # OpenAI-specific
  └── langchain-anthropic # Anthropic-specific
```

---

## Testing Strategy

### Import Verification Tests

Created tests to catch import issues early:

```python
# tests/test_rag.py - Initialization tests
def test_embeddings_configured(self):
    """Test that Ollama embeddings are configured"""
    kb = KnowledgeBase()
    assert kb.embeddings is not None
    assert kb.settings.ollama_embedding_model is not None
```

**Result**: All imports work correctly (27/27 tests passing)

---

## Recommendations for Future Development

### For Phase 2 (Agent Orchestration)

When implementing `src/agents/return_agent.py`, be aware of:

1. **LangChain Agent Creation**
   - Check if using `langchain` or newer agent framework
   - Look for deprecated agent imports
   - Use `langchain.agents` or newer approach

2. **LLM Integration** (qwen2.5 chat model)
   - Will likely use `langchain_ollama.ChatOllama`
   - Not `langchain_community.chat_models`

3. **Tool Definition**
   - Use `langchain.tools.StructuredTool` or `@tool` decorator
   - Location: `langchain_core.tools` (not `langchain.tools`)

4. **Memory/Session Management**
   - Check current LangChain approach to conversation memory
   - Might use `langchain.memory` or newer alternatives

### For New Integrations

If adding new LangChain integrations:

1. **Check if a vendor package exists first**
   - Search for `langchain-{provider}` pattern
   - Example: `langchain-anthropic`, `langchain-openai`

2. **If not, use `langchain_community`**
   - But be aware of potential deprecation

3. **Always pin versions carefully**
   - Use `>=` for minimum versions to avoid breaking changes
   - Test with newest versions periodically

---

## Files Affected

- ✅ `src/rag/knowledge_base.py` - Fixed all import issues
- ✅ `tests/test_rag.py` - Validates imports work correctly
- ✅ `pyproject.toml` - Dependencies already correctly specified

---

## References

### Official Documentation
- [LangChain Core](https://python.langchain.com/docs/api_reference/core/)
- [LangChain Ollama](https://python.langchain.com/docs/integrations/providers/ollama/)
- [LangChain Community](https://python.langchain.com/docs/integrations/providers/)

### Deprecation Notices
- LangChain 0.3.1+ moved Ollama to dedicated package
- LangChain 0.2.9+ deprecated community-provided vectorstores
- Check release notes for migration guides

---

## Conclusion

The import challenges were resolved by:
1. Understanding LangChain's architectural changes
2. Using vendor-specific packages when available
3. Falling back to `langchain_community` when necessary
4. Maintaining proper dependency ordering

**Lessons**: Always verify package availability, check deprecation warnings, understand the dependency hierarchy, and test imports early in development.

**Status**: ✅ All imports working correctly, 27/27 tests passing, ready for Phase 2.
