# Plan: Rich CLI Enhancement & UX Improvements

## Objective
Enhance the interactive CLI with Rich library for better visual presentation and user experience, including loading indicators for delayed responses.

## Current CLI Implementation (src/main.py)

**Status**: Basic but functional (138 lines)
- Plain print() statements for output
- Simple input() for user prompts
- Basic welcome banner with `=` characters
- No visual feedback during agent processing
- Monochrome terminal output
- Agent responses can take 2-10 seconds with no indication

**Pain Points**:
1. **No loading indicator**: User waits 2-10s with no feedback
2. **Plain output**: Hard to distinguish user vs agent messages
3. **No markdown support**: Agent responses appear as plain text
4. **Basic errors**: Error messages blend with normal output
5. **Static welcome**: Banner could be more visually appealing

---

## Proposed Rich CLI Enhancements

### 1. **Welcome Screen Enhancement**

**Current** (lines 33-51):
```python
print("\n" + "=" * 70)
print("  ORDER RETURN AGENT - Customer Service Assistant".center(70))
print("=" * 70)
```

**Enhanced with Rich**:
- Use `Panel` with border styling
- Add gradient or colored title
- Use `Table` for commands list
- Add emoji/icons for visual appeal

**Example Output**:
```
╭─────────────────────────────────────────────────────────╮
│   🤖 ORDER RETURN AGENT - Customer Service Assistant   │
│                                                         │
│  Welcome! I'm here to help process your order return.  │
│                                                         │
│  Commands:                                              │
│  • /exit  - End conversation                            │
│  • /help  - Show this message                           │
│  • /reset - Start new conversation                      │
╰─────────────────────────────────────────────────────────╯
```

### 2. **Loading Spinner During Agent Processing**

**Current** (lines 120-124):
```python
logger.debug(f"User input: {user_input}")
response = agent.run(user_input)
print(f"\nAgent: {response}")
```

**Enhanced with Rich**:
- Show spinner/progress indicator while `agent.run()` executes
- Display status message: "🤔 Thinking..." or "Processing your request..."
- Use threading to run agent in background while showing spinner

**Implementation**:
```python
from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live
import threading

console = Console()

# Show spinner while agent processes
with console.status("[bold cyan]🤔 Agent is thinking...", spinner="dots"):
    response = agent.run(user_input)
```

### 3. **Styled Message Display**

**User Messages**:
- Light blue color
- Prefix with "👤 You:"
- No panel (keep it subtle)

**Agent Messages**:
- Green panel with border
- Prefix with "🤖 Agent:"
- Markdown rendering for formatted responses
- Syntax highlighting if code blocks present

**Example**:
```
👤 You: I want to return order 77893

╭─ 🤖 Agent ────────────────────────────────────────────╮
│ I found your order #77893 from November 28th.        │
│                                                       │
│ Item: Hiking Boots                                    │
│ Price: $89.99                                         │
│                                                       │
│ What's the reason for your return?                   │
╰───────────────────────────────────────────────────────╯
```

### 4. **Error Handling with Rich**

**Current** (lines 131-134):
```python
except Exception as e:
    logger.error(f"Unexpected error in main loop: {e}")
    print(f"\nError: {e}")
```

**Enhanced**:
- Red panel for errors
- Error icon ❌
- Helpful troubleshooting hints
- Pretty traceback (optional with `rich.traceback`)

**Example**:
```
╭─ ❌ Error ────────────────────────────────────────────╮
│ Connection refused to Ollama server                   │
│                                                       │
│ 💡 Tip: Start Ollama with:                           │
│    cd /path/to/ollama && docker compose up -d        │
╰───────────────────────────────────────────────────────╯
```

### 5. **Status Messages**

**Initialization**:
```
✓ Database initialized
✓ Agent session created (a1b2c3d4)
✓ Knowledge base loaded
```

**Session Management**:
```
🔄 Resetting conversation...
✓ New session started (b2c3d4e5)

👋 Goodbye! Session saved.
```

### 6. **Interactive Prompt Enhancement**

**Current**:
```python
user_input = input("\nYou: ").strip()
```

**Enhanced**:
- Styled prompt with `console.input()`
- Auto-completion hints
- Command suggestions

**Example**:
```python
from rich.prompt import Prompt

user_input = Prompt.ask("[cyan]👤 You[/cyan]").strip()
```

---

## Implementation Plan

### Phase 1: Dependencies & Setup

**File**: `pyproject.toml`
```toml
[project.dependencies]
rich = "^13.7.0"
```

**Command**:
```bash
uv add rich
```

### Phase 2: Create Rich UI Module

**New File**: `src/ui/rich_console.py` (~150 lines)

**Purpose**: Centralize all Rich UI components

**Functions**:
- `print_welcome(console)` - Enhanced welcome screen
- `print_user_message(console, message)` - Styled user input
- `print_agent_response(console, response)` - Styled agent output with markdown
- `print_error(console, error, hint=None)` - Error display
- `print_status(console, message, status="success")` - Status messages
- `get_user_input(console, prompt="You")` - Styled input prompt
- `show_spinner(console, message, func, *args)` - Spinner wrapper

**Styling Constants**:
```python
USER_STYLE = "cyan"
AGENT_STYLE = "green"
ERROR_STYLE = "red"
SUCCESS_STYLE = "green"
WARNING_STYLE = "yellow"
```

### Phase 3: Update Main CLI (src/main.py)

**Changes**:

1. **Import Rich components** (lines 1-11):
```python
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from src.ui.rich_console import (
    print_welcome,
    print_agent_response,
    print_error,
    print_status,
    get_user_input,
    show_spinner,
)

console = Console()
```

2. **Replace _print_welcome()** (line 33):
```python
def _print_welcome():
    print_welcome(console)
```

3. **Add spinner to initialization** (lines 62-84):
```python
# Database init
with console.status("[cyan]Initializing database...", spinner="dots"):
    db_exists = check_database_exists()
    init_database()

print_status(console, "Database initialized", "success")

# Agent init
with console.status("[cyan]Starting agent session...", spinner="dots"):
    agent = ReturnAgent(session_id=session_id)

print_status(console, f"Session created ({session_id[:8]})", "success")
```

4. **Update main loop** (lines 92-124):
```python
# Get user input
user_input = get_user_input(console, "You")

if not user_input:
    continue

# Process with spinner
with console.status("[cyan]🤔 Agent is thinking...", spinner="dots"):
    response = agent.run(user_input)

# Display agent response
print_agent_response(console, response)
```

5. **Update error handling** (lines 131-134):
```python
except Exception as e:
    logger.error(f"Unexpected error in main loop: {e}")
    print_error(
        console,
        str(e),
        hint="Check logs/agent.log for details"
    )
```

### Phase 4: Advanced Features (Optional)

**4.1 Progress Bar for Multi-Step Operations**:
```python
from rich.progress import track

for step in track(steps, description="Processing return..."):
    # Execute step
    pass
```

**4.2 Live Dashboard** (show session stats):
```python
from rich.live import Live
from rich.table import Table

def generate_stats_table(session_id, message_count):
    table = Table(title="Session Info")
    table.add_row("Session ID", session_id[:8])
    table.add_row("Messages", str(message_count))
    return table

# Update live during conversation
```

**4.3 Command Auto-completion**:
```python
from rich.prompt import Prompt

commands = ["/exit", "/help", "/reset"]
# Add completion hints
```

**4.4 Pretty Traceback**:
```python
from rich.traceback import install
install(show_locals=True)  # Beautiful tracebacks
```

---

## Files to Modify

1. **pyproject.toml** - Add Rich dependency
2. **src/ui/rich_console.py** (NEW) - Rich UI components module
3. **src/main.py** - Update to use Rich components
4. **README.md** - Add screenshot/note about enhanced CLI

---

## Testing Plan

1. **Manual Testing**:
   - Start agent and verify welcome screen looks good
   - Type message and verify spinner appears
   - Verify agent response is in panel with markdown
   - Test /help, /reset, /exit commands
   - Trigger error and verify error panel
   - Test with long responses (check wrapping)

2. **Visual Regression**:
   - Screenshot before/after for documentation
   - Verify colors work in different terminals

3. **Performance**:
   - Ensure Rich doesn't slow down responses
   - Check memory usage with long conversations

---

## Alternative Approaches

### Option A: Minimal (Recommended for MVP)
- **Scope**: Just add spinner + basic panels
- **Time**: ~30 minutes
- **Files**: Only modify src/main.py (no new module)
- **Benefit**: Quick win, immediate UX improvement

### Option B: Full Enhancement (Recommended)
- **Scope**: All features above
- **Time**: ~2 hours
- **Files**: New module + main.py updates
- **Benefit**: Professional appearance, reusable components

### Option C: Gradual Enhancement
- **Phase 1**: Add spinner only (today)
- **Phase 2**: Add panels (next session)
- **Phase 3**: Add markdown + advanced features (later)

---

## Example Rich CLI Demo Code

**Minimal Spinner Implementation** (5 lines):
```python
from rich.console import Console
console = Console()

# Wrap agent call
with console.status("[cyan]🤔 Thinking...", spinner="dots"):
    response = agent.run(user_input)
```

**Full Panel Implementation**:
```python
from rich.panel import Panel
from rich.markdown import Markdown

# Agent response
md = Markdown(response)
console.print(Panel(
    md,
    title="🤖 Agent",
    border_style="green",
    padding=(1, 2)
))
```

---

## Recommended Implementation Approach

**Option B (Full Enhancement)** is recommended because:
- Best ROI for user experience
- Professional appearance suitable for production
- Reusable components for future features
- Only ~2 hours of implementation time
- Addresses all 5 current pain points

**Default Styling Choices**:
- ✅ Emoji icons (🤖 👤 ✓ ❌) for visual appeal
- ✅ Green/cyan color scheme (professional, accessible)
- ✅ "dots" spinner style (clean, minimal)
- ✅ Markdown rendering enabled (better formatting)

---

## Detailed Implementation Specification

### Step 1: Add Rich Dependency (5 min)

**File**: [pyproject.toml](../../../pyproject.toml)
**Change**: Add `rich>=13.7.0` to dependencies array (line 7-21)

```bash
uv add rich
```

### Step 2: Create UI Module Structure (10 min)

**New Directory**: `src/ui/`

**File 1**: `src/ui/__init__.py` (~5 lines)
```python
"""UI components for Order Return Agent CLI"""

from .console import (
    print_welcome,
    get_user_input,
    print_agent_response,
    print_error,
    print_status,
    show_spinner,
)

__all__ = [
    "print_welcome",
    "get_user_input",
    "print_agent_response",
    "print_error",
    "print_status",
    "show_spinner",
]
```

**File 2**: `src/ui/console.py` (~200 lines)

Full implementation with 8 functions:

1. **Styling Constants**:
```python
"""Rich console utilities for Order Return Agent CLI"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt

# Styling constants
USER_STYLE = "cyan"
AGENT_STYLE = "green"
ERROR_STYLE = "red bold"
SUCCESS_STYLE = "green"
INFO_STYLE = "blue"
WARNING_STYLE = "yellow"
```

2. **print_welcome()** - Replaces lines 33-51 in main.py:
```python
def print_welcome(console: Console) -> None:
    """Display welcome screen with Rich Panel"""
    content = """
    🤖 **ORDER RETURN AGENT** - Customer Service Assistant

    Welcome! I'm here to help you process your order return.

    **To get started, please provide:**
    • Your order number, OR
    • Your email address

    **Commands:**
    • `/exit`  - End the conversation
    • `/help`  - Show this message again
    • `/reset` - Start a new conversation
    """
    panel = Panel(
        Markdown(content),
        border_style="blue",
        padding=(1, 2)
    )
    console.print(panel)
```

3. **get_user_input()** - Replaces line 95 in main.py:
```python
def get_user_input(console: Console) -> str:
    """Get styled user input with Rich Prompt"""
    return Prompt.ask("[cyan]👤 You[/cyan]").strip()
```

4. **print_agent_response()** - Replaces line 124 in main.py:
```python
def print_agent_response(console: Console, response: str) -> None:
    """Display agent response in styled panel with markdown"""
    md = Markdown(response)
    panel = Panel(
        md,
        title="🤖 Agent",
        title_align="left",
        border_style="green",
        padding=(1, 2)
    )
    console.print(panel)
```

5. **print_error()** - Replaces lines 73, 88, 133 in main.py:
```python
def print_error(console: Console, message: str, hint: str = None) -> None:
    """Display error in red panel with optional hint"""
    content = f"❌ {message}"
    if hint:
        content += f"\n\n💡 Hint: {hint}"
    panel = Panel(
        content,
        border_style="red bold",
        padding=(1, 2)
    )
    console.print(panel)
```

6. **print_status()** - Replaces lines 103, 115, 127 in main.py:
```python
def print_status(console: Console, message: str, status: str = "info") -> None:
    """Print status message with appropriate styling"""
    icons = {
        "success": "✓",
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌"
    }
    colors = {
        "success": "green",
        "info": "blue",
        "warning": "yellow",
        "error": "red"
    }
    icon = icons.get(status, "ℹ️")
    color = colors.get(status, "blue")
    console.print(f"[{color}]{icon} {message}[/{color}]")
```

7. **show_spinner()** - Wraps line 121 in main.py:
```python
def show_spinner(console: Console, message: str = "Processing..."):
    """Context manager for showing spinner during long operations"""
    return console.status(f"[cyan]{message}[/cyan]", spinner="dots")
```

### Step 3: Update main.py (40 min)

**File**: [src/main.py](../../../src/main.py)

**Changes by line number**:

1. **Add imports** (after line 11):
```python
from rich.console import Console
from src.ui.console import (
    print_welcome,
    get_user_input,
    print_agent_response,
    print_error,
    print_status,
    show_spinner,
)

# Create console instance
console = Console()
```

2. **Update _print_welcome()** (lines 33-51):
```python
def _print_welcome():
    """Display welcome message and instructions"""
    print_welcome(console)
```

3. **Update database error** (line 73):
```python
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    print_error(console, "Failed to initialize database", hint=str(e))
    return
```

4. **Add session status** (after line 81):
```python
logger.info(f"Creating new agent session: {session_id}")
print_status(console, f"Session created: {session_id[:8]}...", "success")
```

5. **Update agent error** (lines 87-88):
```python
except Exception as e:
    logger.error(f"Failed to initialize agent: {e}")
    print_error(
        console,
        "Failed to start agent",
        hint="Please ensure Ollama is running on http://localhost:11434"
    )
    return
```

6. **Update user input** (line 95):
```python
user_input = get_user_input(console)
```

7. **Update /exit command** (lines 102-104):
```python
if user_input.lower() == "/exit":
    print_status(console, "Thank you for using our service. Goodbye!", "success")
    logger.info(f"Session {session_id} ended by user")
    break
```

8. **Update /reset command** (lines 112-116):
```python
if user_input.lower() == "/reset":
    session_id = str(uuid.uuid4())
    agent = ReturnAgent(session_id=session_id)
    print_status(console, "Conversation reset. Let's start over!", "success")
    print_welcome(console)
    continue
```

9. **Add spinner to agent processing** (lines 120-124):
```python
logger.debug(f"User input: {user_input}")

# Show spinner while agent processes
with show_spinner(console, "🤔 Agent is thinking..."):
    response = agent.run(user_input)

# Display agent response with Rich formatting
print_agent_response(console, response)
```

10. **Update KeyboardInterrupt** (lines 126-129):
```python
except KeyboardInterrupt:
    print_status(console, "Session interrupted. Your conversation has been saved.", "info")
    logger.info(f"Session {session_id} interrupted by user")
    break
```

11. **Update general error handling** (lines 131-134):
```python
except Exception as e:
    logger.error(f"Unexpected error in main loop: {e}")
    print_error(console, str(e), hint="Check logs/agent.log for details")
    print_status(console, "Attempting to continue...", "warning")
```

### Step 4: Testing (30 min)

**Manual Test Cases**:
1. Start agent: `uv run python -m src.main`
2. Check welcome screen displays with Rich Panel
3. Test user input: "I want to return order 77893"
4. Verify spinner appears during processing
5. Check agent response renders in green panel
6. Test /help command
7. Test /reset command
8. Test /exit command
9. Test Ctrl+C handling
10. Verify error display (stop Ollama, restart agent)

**Automated Tests**:
```bash
# Verify Phase 4.5 tests still pass
uv run pytest tests/test_scenarios.py -v

# Run full test suite
uv run pytest -v
```

---

## Files Summary

### Files to Create
1. **src/ui/__init__.py** (15 lines) - Module initialization with exports
2. **src/ui/console.py** (~200 lines) - Rich UI components implementation

### Files to Modify
1. **pyproject.toml** (1 line) - Add `rich>=13.7.0` to dependencies
2. **src/main.py** (~30-40 lines changed) - Update to use Rich components

**Total New Code**: ~215 lines
**Total Modified Lines**: ~40 lines
**Net Change**: Professional CLI with minimal code impact

---

## Success Metrics

### Visual Quality
- ✅ Welcome screen uses Rich Panel with blue border
- ✅ User prompts styled in cyan with emoji
- ✅ Agent responses in green panels with markdown rendering
- ✅ Errors in red panels with helpful hints
- ✅ Spinner displays during 2-10s agent processing
- ✅ Status messages color-coded (green/blue/yellow/red)

### Functionality
- ✅ All commands work (/exit, /help, /reset)
- ✅ Logging unchanged and functional
- ✅ Error handling preserved
- ✅ Session management unchanged
- ✅ All 124 Phase 4.5 tests pass

### Code Quality
- ✅ UI separated into src/ui/ module
- ✅ Components reusable and documented
- ✅ No breaking changes
- ✅ Follows existing patterns
- ✅ Type hints included

---

## Next Steps

1. ✅ Review this updated plan
2. Add Rich dependency: `uv add rich`
3. Create `src/ui/__init__.py` with exports
4. Create `src/ui/console.py` with all 8 functions
5. Update `src/main.py` with Rich integration
6. Test all CLI interactions manually
7. Run Phase 4.5 tests: `uv run pytest tests/test_scenarios.py -v`
8. Create implementation summary document
9. Commit changes with detailed message
