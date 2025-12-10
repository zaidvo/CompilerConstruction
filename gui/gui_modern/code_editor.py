"""
Custom Code Editor with Syntax Highlighting and Line Numbers
"""
import tkinter as tk
from tkinter import ttk, font
from .theme import ModernTheme
import re


class LineNumberCanvas(tk.Canvas):
    """Canvas for displaying line numbers"""
    
    def __init__(self, parent, text_widget, **kwargs):
        super().__init__(parent, **kwargs)
        self.text_widget = text_widget
        self.configure(
            width=50,
            bg=ModernTheme.DARKER_NAVY,
            bd=0,
            highlightthickness=0
        )
    
    def redraw(self, *args):
        """Redraw line numbers"""
        self.delete("all")
        
        # Get visible line range
        i = self.text_widget.index("@0,0")
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(
                2, y,
                anchor="nw",
                text=linenum,
                fill=ModernTheme.TEXT_DISABLED,
                font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE)
            )
            i = self.text_widget.index("%s+1line" % i)


class SyntaxHighlightingText(tk.Text):
    """Text widget with syntax highlighting for CalcScript++"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Configure colors
        self.configure(
            bg=ModernTheme.DARK_NAVY,
            fg=ModernTheme.TEXT_FG,
            insertbackground=ModernTheme.GOLD,
            selectbackground=ModernTheme.DEEP_PURPLE,
            selectforeground=ModernTheme.TEXT_FG,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE),
            wrap=tk.NONE,
            undo=True,
            maxundo=-1,
            insertwidth=2,
            spacing1=2,
            spacing3=2
        )
        
        # Configure tags for syntax highlighting
        self.tag_configure("keyword", foreground=ModernTheme.SYNTAX_KEYWORD, font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE, "bold"))
        self.tag_configure("number", foreground=ModernTheme.SYNTAX_NUMBER)
        self.tag_configure("string", foreground=ModernTheme.SYNTAX_STRING)
        self.tag_configure("comment", foreground=ModernTheme.SYNTAX_COMMENT, font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE, "italic"))
        self.tag_configure("operator", foreground=ModernTheme.SYNTAX_OPERATOR)
        
        # Keywords
        self.keywords = [
            'int', 'long', 'float', 'string', 'boolean', 'array', 'matrix',
            'if', 'else', 'while', 'for', 'repeat', 'times', 'function', 
            'return', 'end', 'print', 'input', 'break', 'continue', 
            'true', 'false', 'and', 'or', 'not'
        ]
        
        # Bind events for auto-highlighting
        self.bind('<KeyRelease>', self._on_key_release)
        self.bind('<Return>', self._on_return)
    
    def _on_key_release(self, event=None):
        """Highlight syntax on key release"""
        self.after(1, self.highlight_syntax)
    
    def _on_return(self, event=None):
        """Auto-indent on return"""
        # Get current line
        line = self.get("insert linestart", "insert lineend")
        # Count leading spaces
        indent = len(line) - len(line.lstrip())
        # Check if line ends with colon (for blocks)
        if line.rstrip().endswith(':'):
            indent += 4
        # Insert newline and indent
        self.insert("insert", "\n" + " " * indent)
        return "break"
    
    def highlight_syntax(self):
        """Apply syntax highlighting to all text"""
        # Remove all existing tags
        for tag in ["keyword", "number", "string", "comment", "operator"]:
            self.tag_remove(tag, "1.0", tk.END)
        
        content = self.get("1.0", tk.END)
        
        # Highlight comments (# to end of line)
        for match in re.finditer(r'#.*$', content, re.MULTILINE):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.tag_add("comment", start_idx, end_idx)
        
        # Highlight strings
        for match in re.finditer(r'"[^"]*"', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.tag_add("string", start_idx, end_idx)
        
        # Highlight numbers
        for match in re.finditer(r'\b\d+\.?\d*\b', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.tag_add("number", start_idx, end_idx)
        
        # Highlight keywords
        for keyword in self.keywords:
            pattern = r'\b' + keyword + r'\b'
            for match in re.finditer(pattern, content, re.IGNORECASE):
                start_idx = f"1.0+{match.start()}c"
                end_idx = f"1.0+{match.end()}c"
                self.tag_add("keyword", start_idx, end_idx)
        
        # Highlight operators
        operators = [r'\+', r'-', r'\*', r'/', r'%', r'=', r'<', r'>', r'!', r'&', r'\|']
        for op in operators:
            for match in re.finditer(op, content):
                start_idx = f"1.0+{match.start()}c"
                end_idx = f"1.0+{match.end()}c"
                self.tag_add("operator", start_idx, end_idx)


class CodeEditor(ttk.Frame):
    """Complete code editor with line numbers and syntax highlighting"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.configure(style='Dark.TFrame')
        
        # Create text widget
        self.text_widget = SyntaxHighlightingText(self)
        
        # Create line numbers
        self.line_numbers = LineNumberCanvas(self, self.text_widget)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Create scrollbars
        self.v_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.text_widget.yview)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.h_scrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.text_widget.xview)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Pack text widget
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        self.text_widget.configure(
            yscrollcommand=self._on_text_scroll,
            xscrollcommand=self.h_scrollbar.set
        )
        
        # Bind events
        self.text_widget.bind('<Any-KeyPress>', lambda e: self.line_numbers.after(10, self.line_numbers.redraw))
        self.text_widget.bind('<MouseWheel>', lambda e: self.line_numbers.after(10, self.line_numbers.redraw))
        
        # Initial draw
        self.line_numbers.redraw()
    
    def _on_text_scroll(self, *args):
        """Handle text scrolling"""
        self.v_scrollbar.set(*args)
        self.line_numbers.redraw()
    
    def get_content(self):
        """Get editor content"""
        return self.text_widget.get("1.0", tk.END).rstrip()
    
    def set_content(self, content):
        """Set editor content"""
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", content)
        self.text_widget.highlight_syntax()
        self.line_numbers.redraw()
    
    def clear(self):
        """Clear editor"""
        self.text_widget.delete("1.0", tk.END)
        self.line_numbers.redraw()
