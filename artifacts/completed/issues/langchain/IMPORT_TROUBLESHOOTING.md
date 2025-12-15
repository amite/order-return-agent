# LangChain Import Troubleshooting Guide

**Diagnosis and resolution steps for common import errors**

---

## Error: ModuleNotFoundError

### Symptom
```
ModuleNotFoundError: No module named 'langchain.schema'
ModuleNotFoundError: No module named 'langchain_chroma'
ModuleNotFoundError: No module named 'module_x.module_y'
```

### Diagnosis Steps

**Step 1: Check if the module was reorganized**
```bash
# Search for the class in installed packages
uv pip list | grep langchain
```

**Step 2: Check LangChain version**
```bash
uv pip show langchain
uv pip show langchain-core
```

**Step 3: Verify the import path exists**
```bash
# For Document class
python -c "from langchain_core.documents import Document; print('✅')"

# For OllamaEmbeddings
python -c "from langchain_ollama import OllamaEmbeddings; print('✅')"

# For Chroma
python -c "from langchain_community.vectorstores import Chroma; print('✅')"
```

### Common Causes & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `langchain.schema` | Module moved | Use `langchain_core.documents` |
| `langchain_chroma` | Package not installed | Use `langchain_community.vectorstores` |
| `langchain.embeddings` | Package restructured | Use `langchain_ollama` (for Ollama) |
| `langchain.chat_models` | Package restructured | Use `langchain_ollama` or `langchain_openai` |

### Resolution Checklist

- [ ] Is the package installed? (`uv pip show package-name`)
- [ ] Is the module path correct? (test with `python -c`)
- [ ] Are you using the right LangChain version?
- [ ] Did you search for `langchain-{provider}` first?
- [ ] Is there a vendor-specific package available?

---

## Error: DeprecationWarning

### Symptom
```
LangChainDeprecationWarning: The class `OllamaEmbeddings` was deprecated in
LangChain 0.3.1 and will be removed in 1.0.0. An updated version of the class
exists in the `langchain-ollama package and should be used instead.
```

### Why This Matters

- ⚠️ **Warning now** → **Broken code later** (in LangChain 1.0.0)
- This is intentional: gives time to migrate before breaking change
- Ignoring deprecation warnings leads to technical debt

### Resolution Steps

**Step 1: Identify the deprecated import**
```python
# Current (deprecated)
from langchain_community.embeddings import OllamaEmbeddings
```

**Step 2: Find the replacement**
- Read the warning message carefully
- It usually says: "An updated version exists in..."
- In this case: "use `langchain-ollama package`"

**Step 3: Verify the replacement exists**
```bash
uv pip show langchain-ollama
# If not installed, add to pyproject.toml
```

**Step 4: Update the import**
```python
# Fixed
from langchain_ollama import OllamaEmbeddings
```

**Step 5: Test the replacement**
```bash
python -c "from langchain_ollama import OllamaEmbeddings; print('✅')"
```

**Step 6: Run tests**
```bash
uv run pytest tests/test_rag.py -v
```

### Prevention

- [ ] Don't ignore deprecation warnings
- [ ] Search for the recommended package immediately
- [ ] Test the new import before committing
- [ ] Update all occurrences in the codebase
- [ ] Run full test suite after migration

---

## Error: ImportError (Module Exists But Won't Import)

### Symptom
```
ImportError: cannot import name 'Document' from 'langchain_core.documents'
(import error during module loading)
```

### Diagnosis Steps

**Step 1: Verify the module exists**
```bash
python -c "import langchain_core.documents; print(dir(langchain_core.documents))"
```

**Step 2: Check for version mismatch**
```bash
uv pip show langchain-core
# Ensure version >= 1.2.0 (from pyproject.toml)
```

**Step 3: Try alternative import paths**
```bash
# Try Pydantic v1 compat layer (if using older LangChain)
python -c "from langchain_core.pydantic_v1 import BaseModel; print('✅')"
```

### Common Causes

1. **Package not installed** - Check `pyproject.toml`
2. **Version conflict** - Package installed but wrong version
3. **Name changed** - Class renamed between versions
4. **Circular import** - Module A imports B imports A

### Resolution

**If package not installed:**
```bash
uv add langchain-core
uv sync
```

**If version is wrong:**
```bash
# Check required version in pyproject.toml
uv sync  # Resync dependencies
```

**If name changed:**
```bash
# Search for the new name
python -c "import langchain_core; help(langchain_core)" | grep -i "oldname"
```

---

## Scenario: Building Phase 2 Agent

### Challenge: Finding the Right Imports

When building `src/agents/return_agent.py`, you'll need:

1. **Agent Framework**
   ```python
   # These MIGHT work (test first)
   from langchain import agents
   from langchain_core.agents import AgentAction

   # OR look for newer approach
   # Check: https://python.langchain.com/docs/modules/agents/
   ```

2. **LLM Integration**
   ```python
   # ✅ This should work
   from langchain_ollama import ChatOllama

   # Test before using
   llm = ChatOllama(model="qwen2.5:14b")
   ```

3. **Tool Binding**
   ```python
   # ✅ This should work
   from langchain_core.tools import StructuredTool

   # Test before using
   tools = [tool1, tool2, tool3]
   ```

4. **Memory/Session**
   ```python
   # ⚠️ Need to check docs - might change
   # Try: from langchain.memory import ConversationBufferMemory
   # Or: from langchain_community.memory import ???

   # Before coding: TEST THIS IMPORT FIRST
   ```

### Pre-Phase-2 Testing Strategy

**Create a test file first:**
```python
# test_agent_imports.py
try:
    from langchain_ollama import ChatOllama
    print("✅ ChatOllama import OK")
except ImportError as e:
    print(f"❌ ChatOllama: {e}")

try:
    from langchain_core.tools import StructuredTool
    print("✅ StructuredTool import OK")
except ImportError as e:
    print(f"❌ StructuredTool: {e}")

# Test for uncertain imports
try:
    from langchain.agents import AgentExecutor
    print("✅ AgentExecutor from langchain OK")
except ImportError:
    try:
        from langchain_core.agents import AgentExecutor
        print("✅ AgentExecutor from langchain_core OK")
    except ImportError as e:
        print(f"❌ AgentExecutor not found: {e}")
```

**Run this before writing real code:**
```bash
uv run python test_agent_imports.py
```

---

## Import Chain Analysis

Understanding dependencies helps avoid circular imports:

```
Your code (src/agents/return_agent.py)
    ↓
    imports
    ↓
langchain_ollama (Ollama integration)
langchain_core (Base types)
    ↓
    all depend on
    ↓
langchain_core (single source of truth)
    ↓
    NO circular dependencies ✅
```

**Why this matters:**
- Circular dependencies cause import errors
- LangChain design converges all packages on `langchain_core`
- You can safely mix imports from different LangChain packages

---

## Testing Imported Code

### Basic Import Test
```python
def test_imports():
    """Verify all imports work"""
    from langchain_core.documents import Document
    from langchain_ollama import OllamaEmbeddings
    from src.rag.knowledge_base import KnowledgeBase

    assert Document is not None
    assert OllamaEmbeddings is not None
    assert KnowledgeBase is not None
```

### Integration Test
```python
def test_imported_classes_work():
    """Verify imported classes can be instantiated"""
    from langchain_core.documents import Document
    from src.rag.knowledge_base import KnowledgeBase

    # Can we create a Document?
    doc = Document(page_content="test", metadata={})
    assert doc.page_content == "test"

    # Can we create a KnowledgeBase?
    kb = KnowledgeBase()
    assert kb is not None
```

---

## Debugging Import Issues

### Enable Verbose Output
```bash
# Show what's being imported
python -v -c "from langchain_core.documents import Document" 2>&1 | head -20

# Show import errors with traceback
python -c "from nonexistent import Something"
```

### Check Python Path
```bash
python -c "import sys; print('\n'.join(sys.path))"
```

### Verify Package Location
```bash
python -c "import langchain_core; print(langchain_core.__file__)"
```

### List All Installed Packages
```bash
uv pip list | grep -E "langchain|pydantic|chromadb"
```

---

## Prevention Strategies

### 1. **Test Imports Early**
- Before writing lots of code, verify imports work
- Use `python -c` to test quick imports

### 2. **Pin Versions Carefully**
```python
# pyproject.toml
langchain-core = ">=1.2.0"  # Minimum version
```

### 3. **Monitor Deprecation Warnings**
```bash
# Run tests with warnings displayed
uv run pytest -W default::DeprecationWarning tests/
```

### 4. **Keep Documentation Updated**
- Document which import path works in this version
- Update when migrating to new versions
- Reference: `/artifacts/wip/issues/IMPORT_QUICK_REFERENCE.md`

### 5. **Use Type Hints**
```python
# This helps catch import issues at type-check time
from langchain_core.documents import Document

def process_doc(doc: Document) -> str:
    return doc.page_content
```

---

## When All Else Fails

### Nuclear Option: Reinstall Everything
```bash
# Completely reinstall dependencies
rm -rf .venv
uv sync
```

### Check Project Config
```bash
# Verify pyproject.toml has correct dependencies
cat pyproject.toml | grep -A 20 "dependencies"
```

### Look at Working Examples
- Reference: `src/rag/knowledge_base.py` (proven to work)
- Copy import patterns from here for similar use cases

### Search for Official Examples
- Go to: https://python.langchain.com/docs/
- Find your use case
- Copy the import from official docs (not blog posts)

---

## Summary Checklist

When facing import errors:

- [ ] Read the error message carefully
- [ ] Check if package is installed (`uv pip show`)
- [ ] Verify import path with `python -c`
- [ ] Check for deprecation warnings
- [ ] Look for vendor-specific package (`langchain-{vendor}`)
- [ ] Test the import before writing code
- [ ] Run full test suite after changes
- [ ] Reference working examples in this project
- [ ] Update documentation for future developers

---

## Files for Reference

- **Working Example**: `src/rag/knowledge_base.py`
- **Test Suite**: `tests/test_rag.py`
- **Quick Reference**: `IMPORT_QUICK_REFERENCE.md`
- **Detailed Analysis**: `LANGCHAIN_IMPORT_CHALLENGES.md`

---

## Version Information

**As of 2025-12-14:**
- Python: 3.12.3
- LangChain: 1.1.3+
- LangChain Core: 1.2.0+
- LangChain Ollama: 1.0.1+
- ChromaDB: 1.3.7

**Note**: If upgrading LangChain, re-test all imports and check for new deprecations.
