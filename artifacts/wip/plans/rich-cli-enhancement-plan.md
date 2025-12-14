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

## Next Steps

1. Review and approve this plan
2. Add Rich dependency: `uv add rich`
3. Create `src/ui/rich_console.py` module
4. Update `src/main.py` with Rich integration
5. Test all CLI interactions
6. Update README with CLI enhancement notes
7. Commit changes
