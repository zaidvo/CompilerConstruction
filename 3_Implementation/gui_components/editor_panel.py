"""
Editor Panel Component
Contains the code editor with line numbers
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
from .syntax_highlighter import SyntaxHighlighter


class EditorPanel:
    """Code editor panel with line numbers"""
    
    def __init__(self, parent):
        self.parent = parent
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        
        # Toolbar
        self.toolbar = ttk.Frame(self.frame)
        self.toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.toolbar, text="Source Code Editor", 
                 font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        # Editor frame with line numbers
        editor_frame = ttk.Frame(self.frame)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Line numbers
        self.line_numbers = tk.Text(editor_frame, width=4, padx=3, takefocus=0, 
                                    border=0, background='lightgray', 
                                    state='disabled', wrap='none')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Editor
        self.editor = scrolledtext.ScrolledText(editor_frame, wrap=tk.NONE, 
                                                undo=True, font=('Consolas', 11))
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.editor.bind('<KeyRelease>', self.update_line_numbers)
        self.editor.bind('<MouseWheel>', self.update_line_numbers)
        
        # Syntax highlighter
        self.highlighter = SyntaxHighlighter(self.editor)
        
        self.update_line_numbers()
    
    def update_line_numbers(self, event=None):
        """Update line numbers"""
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        
        line_count = self.editor.get('1.0', tk.END).count('\n')
        
        for i in range(1, line_count + 1):
            self.line_numbers.insert(tk.END, f"{i:3d}\n")
        
        self.line_numbers.config(state='disabled')
        
        # Apply syntax highlighting
        self.highlighter.highlight()
    
    def get_content(self) -> str:
        """Get editor content"""
        return self.editor.get('1.0', tk.END)
    
    def set_content(self, content: str):
        """Set editor content"""
        self.editor.delete('1.0', tk.END)
        self.editor.insert('1.0', content)
        self.update_line_numbers()
    
    def clear(self):
        """Clear editor content"""
        self.editor.delete('1.0', tk.END)
        self.update_line_numbers()
    
    def add_toolbar_button(self, text: str, command, side=tk.RIGHT):
        """Add button to toolbar"""
        return ttk.Button(self.toolbar, text=text, command=command).pack(
            side=side, padx=2)
    
    def pack(self, **kwargs):
        """Pack the frame"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the frame"""
        self.frame.grid(**kwargs)
