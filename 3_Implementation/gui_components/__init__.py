"""
GUI Components Package
Modular components for CalcScript++ IDE
"""

from .editor_panel import EditorPanel
from .output_panel import OutputPanel
from .menu_bar import MenuBar
from .syntax_highlighter import SyntaxHighlighter

__all__ = [
    'EditorPanel',
    'OutputPanel',
    'MenuBar',
    'SyntaxHighlighter'
]
