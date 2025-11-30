"""
Dialog Windows
Custom dialog windows for GUI
"""
import tkinter as tk
from tkinter import scrolledtext


class LanguageReferenceDialog:
    """Language reference dialog"""
    
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("CalcScript++ Language Reference")
        self.window.geometry("800x600")
        
        text = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, 
                                        font=('Consolas', 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        reference = """
CalcScript++ Language Reference
===============================

TYPE KEYWORDS:
  int, long, float, char, string, boolean, array, matrix

CONTROL STRUCTURES:
  if condition:
      ...
  else:
      ...
  end
  
  while condition:
      ...
  end
  
  for initialization; condition; update:
      ...
  end
  
  repeat count times:
      ...
  end

FUNCTIONS:
  function return_type name(type param1, type param2):
      ...
      return value
  end

OPERATORS:
  Arithmetic: +, -, *, /, %, ^
  Comparison: >, <, >=, <=, ==, !=
  Logical: and, or, not

FOR-LOOP EXAMPLES:

  # Basic for-loop
  for int i = 0; i < 10; i = i + 1:
      print i
  end
  
  # With break
  for int i = 0; i < 100; i = i + 1:
      if i == 10:
          break
      end
  end
  
  # With continue
  for int i = 0; i < 20; i = i + 1:
      if i % 2 == 0:
          continue
      end
      print i  # Only odd numbers
  end

DEBUGGING:
  • Click line numbers to set breakpoints (🔴)
  • Press F7 to start debugging
  • F8 - Step Over
  • F9 - Step Into
  • F5 - Resume

BUILT-IN FUNCTIONS:
  Array: sum(arr), max(arr), min(arr), mean(arr), median(arr)
  Math: sin(x), cos(x), tan(x), sqrt(x), exp(x), ln(x), log(x, base)
  Matrix: M1 + M2, M1 * M2, M ^ t (transpose), M ^ -1 (inverse)

For complete documentation, see ENHANCED_FEATURES_README.md
"""
        text.insert('1.0', reference)
        text.config(state='disabled')
