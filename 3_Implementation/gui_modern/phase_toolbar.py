"""
Phase Buttons Toolbar
Displays individual phase execution buttons and RUN ALL button
"""
import tkinter as tk
from tkinter import ttk
from .theme import ModernTheme


class PhaseButton(tk.Button):
    """Custom styled button for phase execution"""
    
    def __init__(self, parent, text, color, command, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.base_color = color
        self.hover_color = self._lighten_color(color)
        
        self.configure(
            text=text,
            bg=color,
            fg=ModernTheme.TEXT_FG,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE, "bold"),
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2",
            command=command,
            activebackground=self.hover_color,
            activeforeground=ModernTheme.TEXT_FG
        )
        
        # Bind hover effects
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
    
    def _on_enter(self, event):
        """Handle mouse enter"""
        self.configure(bg=self.hover_color)
    
    def _on_leave(self, event):
        """Handle mouse leave"""
        self.configure(bg=self.base_color)
    
    def _lighten_color(self, color):
        """Lighten a hex color"""
        # Simple lightening by adding to each component
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, r + 30)
        g = min(255, g + 30)
        b = min(255, b + 30)
        return f'#{r:02x}{g:02x}{b:02x}'


class PhaseToolbar(tk.Frame):
    """Toolbar containing phase execution buttons"""
    
    def __init__(self, parent, phase_callbacks, **kwargs):
        super().__init__(parent, bg=ModernTheme.SECTION_HEADER, **kwargs)
        
        self.configure(height=60)
        self.pack_propagate(False)
        
        # Left side - Phase buttons
        left_frame = tk.Frame(self, bg=ModernTheme.SECTION_HEADER)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # Phase button configurations
        phase_configs = [
            {'text': '➊ LEX', 'color': ModernTheme.PHASE_LEX, 'key': 'lex'},
            {'text': '➋ PARSE', 'color': ModernTheme.PHASE_PARSE, 'key': 'parse'},
            {'text': '➌ CHECK', 'color': ModernTheme.PHASE_CHECK, 'key': 'check'},
            {'text': '➍ IR', 'color': ModernTheme.PHASE_IR, 'key': 'ir'},
            {'text': '➎ OPT', 'color': ModernTheme.PHASE_OPT, 'key': 'opt'},
            {'text': '➏ RUN', 'color': ModernTheme.PHASE_RUN, 'key': 'run'}
        ]
        
        for config in phase_configs:
            btn = PhaseButton(
                left_frame,
                config['text'],
                config['color'],
                lambda k=config['key']: phase_callbacks[k]()
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # Right side - RUN ALL button
        right_frame = tk.Frame(self, bg=ModernTheme.SECTION_HEADER)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        self.run_all_button = PhaseButton(
            right_frame,
            '▶ RUN ALL PHASES',
            ModernTheme.GOLD,
            phase_callbacks['run_all']
        )
        self.run_all_button.configure(
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_LARGE, "bold"),
            padx=25,
            pady=10
        )
        self.run_all_button.pack(side=tk.RIGHT)
