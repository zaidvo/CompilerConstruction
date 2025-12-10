"""
Collapsible Output Sections Component
Displays compiler phase results in expandable/collapsible sections
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
from .theme import ModernTheme


class CollapsibleSection(ttk.Frame):
    """A single collapsible section with header and content"""
    
    def __init__(self, parent, title, emoji, color, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.title = title
        self.emoji = emoji
        self.color = color
        self.is_expanded = False
        
        self.configure(style='Dark.TFrame')
        
        # Header frame
        self.header = tk.Frame(self, bg=color, height=35, cursor="hand2")
        self.header.pack(fill=tk.X, pady=(0, 1))
        self.header.pack_propagate(False)
        
        # Arrow label
        self.arrow_label = tk.Label(
            self.header,
            text="▶",
            bg=color,
            fg=ModernTheme.TEXT_FG,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_LARGE, "bold")
        )
        self.arrow_label.pack(side=tk.LEFT, padx=(10, 5))
        
        # Emoji and title
        self.title_label = tk.Label(
            self.header,
            text=f"{emoji} {title}",
            bg=color,
            fg=ModernTheme.TEXT_FG,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_LARGE, "bold"),
            anchor=tk.W
        )
        self.title_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Content frame (hidden by default)
        self.content_frame = tk.Frame(self, bg=ModernTheme.PANEL_BG)
        
        # Bind click events
        self.header.bind('<Button-1>', lambda e: self.toggle())
        self.arrow_label.bind('<Button-1>', lambda e: self.toggle())
        self.title_label.bind('<Button-1>', lambda e: self.toggle())
        
        # Hover effects
        self.header.bind('<Enter>', lambda e: self._on_hover_enter())
        self.header.bind('<Leave>', lambda e: self._on_hover_leave())
    
    def _on_hover_enter(self):
        """Handle mouse enter"""
        # Lighten the color slightly
        pass
    
    def _on_hover_leave(self):
        """Handle mouse leave"""
        pass
    
    def toggle(self):
        """Toggle section expansion"""
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()
    
    def expand(self):
        """Expand the section"""
        if not self.is_expanded:
            self.arrow_label.config(text="▼")
            self.content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.is_expanded = True
    
    def collapse(self):
        """Collapse the section"""
        if self.is_expanded:
            self.arrow_label.config(text="▶")
            self.content_frame.pack_forget()
            self.is_expanded = False
    
    def get_content_frame(self):
        """Get the content frame for adding widgets"""
        return self.content_frame


class OutputSections(tk.Frame):
    """Container for all collapsible output sections"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=ModernTheme.DARKER_NAVY, **kwargs)
        
        # Create canvas and scrollbar for scrolling
        self.canvas = tk.Canvas(self, bg=ModernTheme.DARKER_NAVY, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg=ModernTheme.DARKER_NAVY)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind canvas resize
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Enable mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Section definitions
        self.sections = {}
        self._create_sections()
    
    def _on_canvas_configure(self, event):
        """Handle canvas resize"""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _create_sections(self):
        """Create all output sections"""
        section_configs = [
            {
                'key': 'tokens',
                'title': 'Tokens (Lexical Analysis)',
                'emoji': '🔤',
                'color': ModernTheme.PHASE_LEX
            },
            {
                'key': 'ast',
                'title': 'AST (Syntax Tree)',
                'emoji': '🌳',
                'color': ModernTheme.PHASE_PARSE
            },
            {
                'key': 'semantic',
                'title': 'Semantic Analysis',
                'emoji': '✓',
                'color': ModernTheme.PHASE_CHECK
            },
            {
                'key': 'symbol_table',
                'title': 'Symbol Table (STM)',
                'emoji': '📋',
                'color': '#9B59B6'
            },
            {
                'key': 'ir',
                'title': 'IR Code (TAC)',
                'emoji': '⚙',
                'color': ModernTheme.PHASE_IR
            },
            {
                'key': 'optimizer',
                'title': 'Optimizer Log',
                'emoji': '⚡',
                'color': ModernTheme.PHASE_OPT
            },
            {
                'key': 'bytecode',
                'title': 'Bytecode',
                'emoji': '💾',
                'color': ModernTheme.PHASE_RUN
            },
            {
                'key': 'output',
                'title': 'Output',
                'emoji': '📤',
                'color': ModernTheme.SUCCESS
            },
            {
                'key': 'errors',
                'title': 'Errors',
                'emoji': '⚠',
                'color': ModernTheme.ERROR
            }
        ]
        
        for config in section_configs:
            section = CollapsibleSection(
                self.scrollable_frame,
                config['title'],
                config['emoji'],
                config['color']
            )
            section.pack(fill=tk.X, pady=(0, 2))
            
            # Add text widget to content
            text_widget = scrolledtext.ScrolledText(
                section.get_content_frame(),
                bg=ModernTheme.DARK_NAVY,
                fg=ModernTheme.TEXT_FG,
                font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE),
                wrap=tk.NONE,
                height=15
            )
            text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            self.sections[config['key']] = {
                'section': section,
                'text': text_widget
            }
    
    def set_content(self, key, content, auto_expand=True):
        """Set content for a section"""
        if key in self.sections:
            text_widget = self.sections[key]['text']
            text_widget.delete('1.0', tk.END)
            text_widget.insert('1.0', content)
            
            if auto_expand:
                self.sections[key]['section'].expand()
    
    def get_text_widget(self, key):
        """Get text widget for a section"""
        if key in self.sections:
            return self.sections[key]['text']
        return None
    
    def expand_section(self, key):
        """Expand a specific section"""
        if key in self.sections:
            self.sections[key]['section'].expand()
    
    def collapse_section(self, key):
        """Collapse a specific section"""
        if key in self.sections:
            self.sections[key]['section'].collapse()
    
    def clear_all(self):
        """Clear all sections"""
        for key in self.sections:
            self.sections[key]['text'].delete('1.0', tk.END)
            self.sections[key]['section'].collapse()
    
    def clear_section(self, key):
        """Clear a specific section"""
        if key in self.sections:
            self.sections[key]['text'].delete('1.0', tk.END)
