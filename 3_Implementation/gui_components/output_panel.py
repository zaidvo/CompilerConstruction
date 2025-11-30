"""
Output Panel Component
Contains tabbed interface for compiler phases output
"""
import tkinter as tk
from tkinter import ttk, scrolledtext


class OutputPanel:
    """Tabbed output panel for compilation phases"""
    
    def __init__(self, parent):
        self.parent = parent
        
        # Create notebook for phases
        self.notebook = ttk.Notebook(parent)
        
        # Create tabs
        self.tabs = {}
        self._create_tab('output', '📤 Output', "Program Output")
        self._create_tab('tokens', '🔤 Tokens', "Phase 1: Lexical Analysis")
        self._create_tab('ast', '🌳 AST', "Phase 2: Syntax Analysis")
        self._create_tab('semantic', '✓ Semantic', "Phase 3: Semantic Analysis")
        self._create_tab('tac', '📝 TAC', "Phase 4: Intermediate Code")
        self._create_tab('optimized', '⚡ Optimized', "Phase 5: Optimization")
    
    def _create_tab(self, key: str, tab_label: str, title: str):
        """Create a single tab with text widget"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=tab_label)
        
        ttk.Label(frame, text=title, font=('Arial', 10, 'bold')).pack(pady=5)
        
        text_widget = scrolledtext.ScrolledText(frame, wrap=tk.WORD, 
                                                font=('Consolas', 9))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tabs[key] = text_widget
    
    def get_widget(self, key: str) -> scrolledtext.ScrolledText:
        """Get text widget for specific tab"""
        return self.tabs.get(key)
    
    def clear_all(self):
        """Clear all output tabs"""
        for widget in self.tabs.values():
            widget.delete('1.0', tk.END)
    
    def switch_to_tab(self, key: str):
        """Switch to specific tab"""
        tab_names = list(self.tabs.keys())
        if key in tab_names:
            self.notebook.select(tab_names.index(key))
    
    def pack(self, **kwargs):
        """Pack the notebook"""
        self.notebook.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the notebook"""
        self.notebook.grid(**kwargs)
