"""
Syntax Highlighter for CalcScript++
Handles syntax highlighting with configurable keywords and styles
"""
import tkinter as tk
from tkinter import scrolledtext


class SyntaxHighlighter:
    """Syntax highlighter for CalcScript++ code"""
    
    def __init__(self, text_widget: scrolledtext.ScrolledText):
        self.text_widget = text_widget
        self.keywords = [
            'int', 'long', 'float', 'char', 'string', 'boolean', 'bool', 
            'array', 'matrix', 'print', 'repeat', 'times', 'if', 'else', 
            'for', 'function', 'return', 'end', 'while', 'input', 'break', 
            'continue', 'true', 'false', 'and', 'or', 'not'
        ]
        
        self.setup_tags()
    
    def setup_tags(self):
        """Setup text widget tags for syntax highlighting"""
        self.text_widget.tag_config('keyword', foreground='blue', 
                                    font=('Consolas', 11, 'bold'))
        self.text_widget.tag_config('string', foreground='green')
        self.text_widget.tag_config('comment', foreground='gray', 
                                    font=('Consolas', 11, 'italic'))
        self.text_widget.tag_config('number', foreground='purple')
    
    def highlight(self, event=None):
        """Apply syntax highlighting to the entire text"""
        # Remove existing tags
        for tag in ['keyword', 'string', 'comment', 'number']:
            self.text_widget.tag_remove(tag, '1.0', tk.END)
        
        content = self.text_widget.get('1.0', tk.END)
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Comments
            if '#' in line:
                comment_start = line.index('#')
                self.text_widget.tag_add('comment', f'{i}.{comment_start}', f'{i}.end')
            
            # Strings
            in_string = False
            string_start = 0
            for j, char in enumerate(line):
                if char == '"':
                    if not in_string:
                        string_start = j
                        in_string = True
                    else:
                        self.text_widget.tag_add('string', f'{i}.{string_start}', 
                                                f'{i}.{j+1}')
                        in_string = False
            
            # Keywords
            words = line.split()
            col = 0
            for word in words:
                if word in self.keywords:
                    start = line.find(word, col)
                    if start != -1:
                        self.text_widget.tag_add('keyword', f'{i}.{start}', 
                                                f'{i}.{start+len(word)}')
                        col = start + len(word)
            
            # Numbers
            import re
            for match in re.finditer(r'\b\d+\.?\d*\b', line):
                start, end = match.span()
                self.text_widget.tag_add('number', f'{i}.{start}', f'{i}.{end}')
