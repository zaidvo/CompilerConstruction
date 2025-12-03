#!/usr/bin/env python3
"""
Modern GUI Launcher for CalcScript++ Compiler
Launch this file to start the modern GUI
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from gui_modern import ModernCompilerGUI
import tkinter as tk


if __name__ == '__main__':
    root = tk.Tk()
    app = ModernCompilerGUI(root)
    root.mainloop()
