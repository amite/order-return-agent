# LangChain v1 Migration Fixes

**Date**: 2025-12-14
**Status**: ✅ RESOLVED
**Affected Files**: src/agents/return_agent.py, src/rag/knowledge_base.py, pyproject.toml

---

## Issue 1: Invalid Parameters in create_agent()

### Problem
When running the agent (`uv run python -m src.main`), initialization failed with:
```
TypeError: create_agent() got an unexpected keyword argument 'max_iterations'
```

### Root Cause
The code was attempting to pass `max_iterations` and `max_execution_time` to LangChain v1's `create_agent()` function:

```python
# ❌ INCORRECT - create_agent() doesn't accept these parameters
agent = create_agent(
    model=self.llm,
    tools=self.tools,
    system_prompt=AGENT_SYSTEM_PROMPT,
    max_iterations=self.settings.agent_max_iterations,
    max_execution_time=self.settings.agent_max_execution_time,
)
```

**API Mismatch**: LangChain v1's `create_agent()` signature is:
```python
create_agent(model, tools, system_prompt)
```

These parameters are only available at **invocation time**, not creation time.

### Challenge
Understanding the difference between:
- **Creation time** parameters (model, tools, system_prompt)
- **Invocation time** parameters (handled via agent configuration or invoke() args)

The previous pattern from LangChain v0.x made this ambiguous.

### Solution
**File**: `src/agents/return_agent.py` (lines 106-113)

```python
# ✅ CORRECT - Remove invalid parameters
agent = create_agent(
    model=self.llm,
    tools=self.tools,
    system_prompt=AGENT_SYSTEM_PROMPT,
)
```

**Note**: Max iterations/timeout can be configured at invoke time if needed:
```python
self.agent_executor.invoke(
    {"messages": [HumanMessage(content=user_input)]},
    # config={"max_iterations": 15}  # Optional at invocation time
)
```

---

## Issue 2: Deprecated ChromaDB Import

### Problem
Deprecation warning on startup:
```
LangChainDeprecationWarning: The class `Chroma` was deprecated in LangChain 0.2.9
and will be removed in 1.0. An updated version of the class exists in the
`langchain-chroma` package
```

### Root Cause
Code was importing from old location:
```python
# ❌ DEPRECATED
from langchain_community.vectorstores import Chroma
```

LangChain v0.2.9+ migrated Chroma support to a dedicated package.

### Challenge
**Package Migration Pattern**: LangChain moved integrations to separate packages:
- Old: `langchain_community.vectorstores.Chroma`
- New: `langchain_chroma.Chroma` (requires `langchain-chroma` package)

This pattern applies to many integrations (OpenAI, Cohere, Anthropic, etc.).

### Solution

**Step 1**: Install the dedicated package
```bash
uv add langchain-chroma
```

**Step 2**: Update import in `src/rag/knowledge_base.py` (line 7)
```python
# ✅ CORRECT - New import path
from langchain_chroma import Chroma
```

---

## Lessons Learned

### 1. LangChain v1 API Design
- **Creation vs Invocation**: Agent configuration split between creation (model, tools, prompt) and invocation (iterative behavior)
- **Cleaner API**: Removes redundancy when creating multiple agents with same config but different runtime behavior

### 2. Package Ecosystem Migration
- LangChain v1 extracted integrations into separate packages for better modularity
- Follow deprecation warnings - they provide exact migration paths
- Pattern: `langchain_<integration>` for all new integrations

### 3. Testing Pattern
When migrations are unclear:
```bash
# Run the code to see actual error messages
timeout 10 uv run python -m src.main <<< "/exit"

# Verify fixes work
timeout 10 uv run python -m src.main <<< "/exit"
```

---

## Verification

Both issues resolved:

```bash
$ timeout 10 uv run python -m src.main <<< "/exit"
[2025-12-14 10:15:32] INFO     Starting Order Return Agent
[2025-12-14 10:15:32] INFO     Database initialized
[2025-12-14 10:15:33] INFO     Creating new agent session: 7a6ac36a-2962-4915-87c0-61583e6f6ec2
[2025-12-14 10:15:34] INFO     ReturnAgent initialized with session_id: 7a6ac36a-2962-4915-87c0-61583e6f6ec2
... (no deprecation warnings)
[2025-12-14 10:15:35] INFO     Session ... ended by user
```

✅ Agent initializes cleanly
✅ No deprecation warnings
✅ No parameter errors

---

## Files Modified

- `src/agents/return_agent.py` - Removed invalid parameters from create_agent()
- `src/rag/knowledge_base.py` - Updated Chroma import path
- `pyproject.toml` - Added langchain-chroma dependency

---

## Related Documentation

- [Phase 2 Completion](../PHASE_2_COMPLETION.md) - Agent implementation details
- [LangChain Docs](https://python.langchain.com/docs/) - Official migration guides
