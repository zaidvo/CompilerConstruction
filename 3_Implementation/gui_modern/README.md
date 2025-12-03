# Modern GUI for CalcScript++ Compiler

## Overview

This is a completely redesigned GUI for the CalcScript++ compiler featuring a unique **purple-gold-teal** color scheme with a modern, professional interface. The GUI maintains all original compiler functionality while providing an enhanced user experience.

## Design Features

### 🎨 Color Scheme

- **Deep Purple** (#6200EA) - Primary accent color
- **Gold** (#FFD700) - Highlights and RUN ALL button
- **Teal** (#00D4AA) - Phase buttons and accents
- **Dark Navy** (#1e1e2e) - Editor background
- **Darker Navy** (#181825) - Panel backgrounds

### 🎯 Key Features

1. **Horizontal Split-Pane Layout**

   - Left side: Source code editor with line numbers
   - Right side: Collapsible compilation results sections

2. **Syntax Highlighting**

   - Hot Pink (#FF1493) - Keywords
   - Golden Yellow (#FFD700) - Numbers
   - Bright Green (#00FF7F) - Strings
   - Cyan (#00FFFF) - Comments
   - Light Gray - Identifiers
   - Coral - Operators

3. **Phase Execution Buttons**

   - ➊ LEX (Cyan) - Lexical Analysis
   - ➋ PARSE (Purple) - Syntax Analysis
   - ➌ CHECK (Orange) - Semantic Analysis
   - ➍ IR (Coral) - Intermediate Code Generation
   - ➎ OPT (Green) - Optimization
   - ➏ RUN (Pink) - Code Execution
   - **▶ RUN ALL PHASES** (Gold) - Execute all phases

4. **Collapsible Output Sections**

   - 🔤 Tokens (Lexical Analysis) - Table view with index, type, value, line, column
   - 🌳 AST (Syntax Tree) - Tree view of abstract syntax tree
   - ✓ Semantic Analysis - Scope and symbol table display
   - ⚙ IR Code (TAC) - Three-address code listing
   - ⚡ Optimizer Log - Optimization statistics and log
   - 💾 Bytecode - Instruction table with # and Label columns
   - 📤 Output - Program execution results (terminal-style)
   - ⚠ Errors - Error table with Phase, Type, Message, Line, Column

5. **File Operations**
   - 🆕 New - Create new file
   - 📂 Open - Open existing .calc file
   - 💾 Save - Save current file
   - 💾 Save As - Save with new name
   - Example Programs Dropdown - Quick access to test cases

## File Structure

```
gui_modern/
├── __init__.py              # Package initialization
├── main_window.py           # Main GUI window and orchestration
├── theme.py                 # Color scheme and styling constants
├── code_editor.py           # Code editor with syntax highlighting and line numbers
├── output_sections.py       # Collapsible sections for output display
├── phase_toolbar.py         # Phase execution buttons toolbar
├── phase_service.py         # Service for executing compiler phases
└── formatters.py            # Output formatters for each phase
```

## How to Use

### Launch the GUI

```bash
cd 3_Implementation
python launch_modern_gui.py
```

Or use the old launcher if you want to switch back:

```bash
python gui_modular.py
```

### Running the Compiler

**Option 1: Run All Phases**

1. Write or load CalcScript++ code in the editor
2. Click the large **"▶ RUN ALL PHASES"** button (gold, top-right)
3. All phases execute sequentially
4. Results appear in collapsible sections
5. Output section auto-expands with program results

**Option 2: Step-by-Step Execution**

1. Click individual phase buttons from left to right:
   - **➊ LEX** - Tokenize the source code
   - **➋ PARSE** - Build the abstract syntax tree
   - **➌ CHECK** - Perform semantic analysis
   - **➍ IR** - Generate intermediate representation
   - **➎ OPT** - Optimize the code
   - **➏ RUN** - Execute the program
2. Each phase auto-expands its corresponding section
3. Must run phases in order (dependencies enforced)

### Loading Examples

1. Use the dropdown menu above the editor: "Select Example..."
2. Choose from available test cases:
   - `example.calc` - Basic examples
   - `test_for_loops.calc` - For loop demonstrations
   - `test_matrix_operations.calc` - Matrix operations
   - `test_simple_typed.calc` - Type system examples

### Viewing Results

- **Automatic Expansion**: Sections auto-expand when data is populated
- **Manual Toggle**: Click section headers to expand/collapse
- **Scrolling**: Each section has its own scrollbar for long output
- **Arrow Indicators**: ▶ (collapsed) ▼ (expanded)

## Features Comparison

| Feature             | Old GUI           | Modern GUI                           |
| ------------------- | ----------------- | ------------------------------------ |
| Color Scheme        | Standard          | Purple-Gold-Teal                     |
| Layout              | Tabbed            | Split-pane with collapsible sections |
| Phase Execution     | Combined          | Individual phase buttons             |
| Syntax Highlighting | Basic             | Advanced with custom colors          |
| Line Numbers        | No                | Yes                                  |
| Error Display       | Mixed with output | Dedicated error section              |
| Visual Feedback     | Limited           | Hover effects, color coding          |
| Status Bar          | Basic             | Enhanced with file info              |

## Compiler Functionality

**IMPORTANT**: All compiler functionality remains **100% identical** to the original implementation:

- Same lexer, parser, semantic analyzer, IR generator, optimizer, and interpreter
- Same error handling and recovery
- Same output and results
- Same support for all language features:
  - For loops
  - Matrix operations
  - Type checking
  - Error recovery
  - All operators and expressions

## Technical Details

### Dependencies

- Python 3.7+
- tkinter (standard library)
- No external packages required (ttkbootstrap not needed)

### Custom Components

1. **LineNumberCanvas**: Custom canvas widget for line numbers
2. **SyntaxHighlightingText**: Enhanced Text widget with real-time highlighting
3. **CollapsibleSection**: Expandable/collapsible panel with header
4. **PhaseButton**: Custom button with hover effects

### Theme System

The `ModernTheme` class centralizes all colors and styling:

- Easy to modify colors
- Consistent appearance across all components
- Supports dark theme optimized for long coding sessions

## Keyboard Shortcuts

- **Ctrl+N**: New file
- **Ctrl+O**: Open file
- **Ctrl+S**: Save file
- **Return**: Auto-indent in editor
- **Tab**: Insert 4 spaces

## Status Bar

Shows current status:

- File name (if loaded)
- Compilation status
- Phase completion indicators (✓ or ✗)

## Error Handling

Errors are displayed in dedicated sections:

- **Compilation Errors**: Shown in Errors section with full details
- **Runtime Errors**: Shown in Output section with error messages
- **Phase-specific Errors**: Each phase reports its own errors

## Customization

To modify colors, edit `theme.py`:

```python
class ModernTheme:
    DEEP_PURPLE = '#6200EA'  # Change primary color
    GOLD = '#FFD700'         # Change accent color
    # ... etc
```

## Notes

- The GUI auto-saves layout preferences
- Sections remember their expanded/collapsed state during a session
- Smooth scrolling in all panels
- Proper padding and spacing for professional look
- Hover effects on all interactive elements

## Troubleshooting

**GUI doesn't launch:**

- Ensure Python 3.7+ is installed
- Check that tkinter is available: `python -c "import tkinter"`

**Compiler errors:**

- The compiler backend is unchanged
- Refer to original documentation for language syntax
- Check the Errors section for detailed error information

**Display issues:**

- Adjust window size (default 1600x900)
- Use collapsible sections to manage space
- Scroll within sections for long output

## Credits

- Original Compiler: CalcScript++ 6-Phase Compiler
- Modern GUI Design: Custom implementation
- Theme: Purple-Gold-Teal color scheme
