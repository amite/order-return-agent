# Performance Instrumentation Plan

Based on the data flow architecture in `Flow_v1.md`, this plan identifies performance-critical components to instrument and provides a simple timing-based implementation approach.

## Components to Instrument

### 1. End-to-End Message Processing Pipeline
**Location**: `src/agents/return_agent.py` - `run()` method  
**Metrics**:
- Total response time (user input → agent response)
- LLM reasoning time (per iteration)
- Tool execution time (per tool call)
- Response formatting time
- Total iterations in agent loop

**Why**: This is the user-facing latency - critical for UX. The example shows ~120ms for a complete flow with 5 tool calls, so we need to track if this degrades.

### 2. LLM Operations
**Location**: `src/agents/return_agent.py` - agent executor invocation  
**Metrics**:
- LLM call duration (per reasoning step)
- Token generation time
- Context preparation time
- Number of LLM calls per conversation turn

**Why**: LLM calls are typically the slowest operations. The system allows up to 15 iterations, so tracking LLM performance helps identify bottlenecks.

### 3. Tool Execution Times (All 6 Tools)
**Locations**: Each tool's `_run()` method in `src/tools/`

#### 3.1 GetOrderDetails Tool
- Database query time (by order_id vs email)
- Schema transformation time
- Total tool execution time

#### 3.2 CheckEligibility Tool (Critical Path)
- Order fetch time
- Days calculation time
- Each decision step time (9 steps total):
  - Item validation
  - Damage keyword check
  - Fraud flag check
  - Return frequency check
  - Returnability check
  - Policy lookup
  - Window validation
- Total eligibility check time

**Why**: This is the most complex tool with a 9-step decision tree. Performance here directly impacts return processing speed.

#### 3.3 CreateRMA Tool
- Order verification time
- RMA number generation time
- Refund calculation time
- Database write time (INSERT + UPDATE)
- Transaction commit time

#### 3.4 GenerateReturnLabel Tool
- RMA lookup time
- Label generation time (simulated, but track for future API integration)
- Database update time

#### 3.5 SendEmail Tool
- Template loading time
- Jinja2 rendering time
- Email logging time
- Total email processing time

#### 3.6 EscalateToHuman Tool
- Conversation retrieval time (querying conversation_logs)
- Summary generation time
- RMA update time
- Ticket creation time

### 4. Database Operations
**Location**: `src/db/connection.py` - `get_db_session()` context manager  
**Metrics**:
- Query execution time (per query)
- Transaction duration
- Connection acquisition time
- Commit/rollback time

**Why**: Database operations are frequent (every tool touches DB). Need to identify slow queries, especially:
- Order lookups with joins
- Conversation log retrieval (can grow large)
- RMA updates

### 5. RAG System Operations
**Location**: `src/rag/knowledge_base.py`  
**Metrics**:
- Document retrieval time (vector search)
- Embedding generation time (if done on-the-fly)
- Context preparation time
- RAG query latency

**Why**: RAG is used for policy context and templates. Vector search performance affects agent response quality and speed.

### 6. Agent Loop Iterations
**Location**: `src/agents/return_agent.py` - agent executor loop  
**Metrics**:
- Iteration count per conversation turn
- Time per iteration
- Tool chaining patterns (which tools called together)
- Average tools per conversation

**Why**: The system allows up to 15 iterations. Tracking helps identify:
- Inefficient tool chaining
- LLM making unnecessary tool calls
- Optimal vs suboptimal paths

### 7. Application Initialization
**Location**: `src/main.py` - `main()` function  
**Metrics**:
- Database initialization time
- Database seeding time (first run)
- RAG initialization time
- Document ingestion time
- Agent creation time
- Total startup time

**Why**: Startup performance affects developer experience and deployment times.

## Implementation Approach

### Step 1: Create Timing Utilities
Create `src/utils/timing.py` with:
- `@timed` decorator for function timing
- `TimingContext` context manager for block timing
- `PerformanceLogger` class for structured logging

### Step 2: Instrument Core Agent Loop
Add timing to `ReturnAgent.run()`:
- Wrap entire method with timing
- Time LLM invocations
- Time each tool execution
- Log iteration counts

### Step 3: Instrument All Tools
Add `@timed` decorator to each tool's `_run()` method:
- `GetOrderDetailsTool._run()`
- `CheckEligibilityTool._run()` (with sub-step timing)
- `CreateRMATool._run()`
- `GenerateReturnLabelTool._run()`
- `SendEmailTool._run()`
- `EscalateToHumanTool._run()`

### Step 4: Instrument Database Operations
Add timing context manager to `get_db_session()`:
- Track session duration
- Track individual query times (via SQLAlchemy event listeners)

### Step 5: Instrument RAG Operations
Add timing to `KnowledgeBase` methods:
- `get_policy_context()` - vector search time
- `get_communication_template()` - retrieval time
- `get_exception_guidance()` - search time

### Step 6: Instrument Initialization
Add timing to `main()` initialization steps:
- Database setup
- RAG initialization
- Agent creation

## Log Format

Structured JSON logs with performance metrics:
```json
{
  "timestamp": "2025-12-14T12:00:00.123Z",
  "level": "INFO",
  "component": "performance",
  "metric": "tool_execution",
  "tool_name": "CheckEligibility",
  "duration_ms": 45.2,
  "step": "total",
  "session_id": "550e8400-...",
  "order_id": "77893"
}
```

## Key Metrics to Track

1. **P50, P95, P99 latencies** for:
   - End-to-end response time
   - LLM reasoning time
   - Tool execution times
   - Database query times

2. **Throughput**:
   - Messages processed per second
   - Tools executed per conversation

3. **Resource Usage**:
   - Memory usage (if possible)
   - Database connection pool usage

4. **Error Rates**:
   - Timeout frequency
   - Database error frequency
   - Tool failure rates

## Files to Modify

1. **New File**: `src/utils/timing.py` - Timing utilities
2. **Modify**: `src/agents/return_agent.py` - Add timing to agent loop
3. **Modify**: `src/tools/*.py` - Add `@timed` decorators to all tools
4. **Modify**: `src/db/connection.py` - Add timing to database operations
5. **Modify**: `src/rag/knowledge_base.py` - Add timing to RAG operations
6. **Modify**: `src/main.py` - Add timing to initialization

## Success Criteria

- All critical path components instrumented
- Performance logs generated for every operation
- Easy to identify bottlenecks in logs
- No significant performance overhead from instrumentation (<1% overhead)
- Logs can be parsed for analysis (JSON format)

## Future Enhancements

- Export metrics to Prometheus/StatsD
- Add APM integration (OpenTelemetry)
- Create performance dashboard
- Automated performance regression testing
- Alerting on performance degradation
