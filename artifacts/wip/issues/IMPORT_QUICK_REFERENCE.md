# LangChain Imports - Quick Reference Guide

**For developers working on this project and Phase 2+ implementation**

---

## The Problem

LangChain has been refactored into multiple packages with different import paths. Using old imports causes:
- ❌ `ModuleNotFoundError` (module doesn't exist)
- ⚠️ `DeprecationWarning` (will break in future versions)

---

## Quick Decision Tree

```
Need to import from LangChain?
│
├─ Core types (Document, BaseModel)?
│  └─ Use: from langchain_core.xxx import ...
│
├─ Ollama (embeddings, chat)?
│  └─ Use: from langchain_ollama import ...
│
├─ OpenAI (embeddings, chat)?
│  └─ Use: from langchain_openai import ...
│
├─ ChromaDB vectorstore?
│  └─ Use: from langchain_community.vectorstores import Chroma
│
├─ Text splitting, tools, memory, agents?
│  └─ Check latest docs + test imports
│
└─ Anything else?
   └─ Use: from langchain_community.xxx import ...
```

---

## Common Imports (Correct Paths)

### Core Types
```python
# ✅ CORRECT
from langchain_core.documents import Document
from langchain_core.tools import StructuredTool, tool
from langchain_core.pydantic_v1 import BaseModel

# ❌ WRONG
from langchain.schema import Document
from langchain.tools import tool
```

### Ollama Integration
```python
# ✅ CORRECT
from langchain_ollama import OllamaEmbeddings, ChatOllama

# ⚠️ DEPRECATED (works now, breaks in 1.0.0)
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
```

### Text Processing
```python
# ✅ CORRECT
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ❌ WRONG
from langchain.text_splitter import RecursiveCharacterTextSplitter
```

### Vector Stores
```python
# ✅ CORRECT
from langchain_community.vectorstores import Chroma

# ❌ WRONG (langchain_chroma doesn't exist in this project)
from langchain_chroma import Chroma
```

### Tools & Decorators
```python
# ✅ CORRECT
from langchain_core.tools import StructuredTool

# Setup:
def my_tool_func(arg1: str) -> str:
    """Tool description"""
    return result

tool = StructuredTool.from_function(my_tool_func)
```

---

## Pre-Implementation Checklist

Before writing code that imports from LangChain:

- [ ] Check `pyproject.toml` to see what's installed
- [ ] Google "{package}-{feature}" for official package
  - Example: "langchain-ollama" for Ollama
  - Example: "langchain-openai" for OpenAI
- [ ] Try the import in a test file first
- [ ] If `ModuleNotFoundError`, check alternative paths
- [ ] If deprecation warning, use the recommended package
- [ ] Run tests to verify import works

---

## Testing Imports

Quick way to verify imports work:

```bash
# Test a single import
python -c "from langchain_ollama import OllamaEmbeddings; print('✅')"

# List all installed LangChain packages
uv pip list | grep langchain

# Show details of a package
uv pip show langchain-ollama
```

---

## Installed Packages in This Project

Check `pyproject.toml` dependencies section:

```
✅ langchain>=1.1.3           # Main framework
✅ langchain-core>=1.2.0      # Core types (REQUIRED)
✅ langchain-community>=0.4.1 # Community integrations
✅ langchain-ollama>=1.0.1    # Ollama integration
```

**Key Point**: If something isn't in these packages, it doesn't exist in this project.

---

## Common Mistakes to Avoid

### ❌ Mistake #1: Using Old Paths
```python
# WRONG - module removed
from langchain.schema import Document
from langchain.embeddings import OllamaEmbeddings
```

**Fix**: Use `langchain_core` or `langchain_ollama`

### ❌ Mistake #2: Assuming Package Exists
```python
# WRONG - langchain_chroma not installed
from langchain_chroma import Chroma
```

**Fix**: Verify with `uv pip show langchain_chroma`, use fallback if needed

### ❌ Mistake #3: Ignoring Deprecation Warnings
```python
# Deprecated but works now
from langchain_community.embeddings import OllamaEmbeddings
```

**Fix**: Use `from langchain_ollama import OllamaEmbeddings` instead

### ❌ Mistake #4: Not Testing Imports
```python
# Don't discover import errors at runtime
def my_function():
    from some_module import SomeClass  # Fails later
```

**Fix**: Import at top of file, test early

---

## Phase 2 Preparation

For implementing `src/agents/return_agent.py`:

### Probably Correct ✅
```python
from langchain_core.tools import StructuredTool
from langchain_ollama import ChatOllama
from langchain_community.vectorstores import Chroma
from src.rag.knowledge_base import KnowledgeBase
```

### Check Before Using ⚠️
```python
# Agent creation - check latest docs
from langchain import ???  # TBD based on version

# Memory/Session - check latest approach
from langchain.memory import ???  # TBD based on version

# Conversation - use langchain or langchain_core?
from langchain??? import ???  # TBD based on version
```

### Definitely Wrong ❌
```python
from langchain.schema import Document  # Use langchain_core
from langchain_community.embeddings import OllamaEmbeddings  # Use langchain_ollama
from langchain_chroma import Chroma  # Package doesn't exist
```

---

## When in Doubt

1. **Run the import in a test**
   ```bash
   python -c "from module import X; print('OK')"
   ```

2. **Check official docs for your feature**
   - Search: "langchain {feature} python"
   - Look for the official LangChain docs, not blogs

3. **Look at existing working imports** in this project
   - `src/db/schema.py` - SQLAlchemy imports
   - `src/config/settings.py` - Pydantic imports
   - `src/rag/knowledge_base.py` - LangChain imports ✅

4. **Ask yourself**: "Is this module in `langchain_core`, vendor package, or community?"
   - If vendor (Ollama, OpenAI): Look for `langchain-{vendor}`
   - If generic (ChromaDB): Look in `langchain_community`
   - If core type (Document): Look in `langchain_core`

---

## Summary

| Import Type | Package | Example |
|---|---|---|
| Core types | `langchain_core` | `Document`, `StructuredTool` |
| Ollama | `langchain_ollama` | `OllamaEmbeddings`, `ChatOllama` |
| OpenAI | `langchain_openai` | `OpenAIEmbeddings`, `ChatOpenAI` |
| Community | `langchain_community` | `Chroma` vectorstore |
| Generic | `langchain_*` | `langchain_text_splitters` |

---

## References

- [LangChain Imports Guide](https://python.langchain.com/docs/)
- [This Project's Working Example](../src/rag/knowledge_base.py)
- [Detailed Challenge Document](./LANGCHAIN_IMPORT_CHALLENGES.md)

---

## Quick Checklist for New Developers

When adding a new LangChain import:

- [ ] Is this a core type? → Use `langchain_core`
- [ ] Is this Ollama-specific? → Use `langchain_ollama`
- [ ] Is this vendor-specific (OpenAI, Anthropic)? → Use `langchain-{vendor}`
- [ ] Is this a generic tool? → Check `langchain_community`
- [ ] Does it exist in our `pyproject.toml`? → If not, it can't be imported
- [ ] Did I test the import? → Run `python -c "from x import y"`
- [ ] Any deprecation warnings? → Fix them now, not later

**When in doubt, look at `src/rag/knowledge_base.py` for reference examples!**
