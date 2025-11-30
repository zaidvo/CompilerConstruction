"""
Menu Bar Component
Application menu with File, Compile, Examples, and Help menus
"""
import tkinter as tk
from tkinter import messagebox


class MenuBar:
    """Application menu bar"""
    
    def __init__(self, root, callbacks):
        """
        Initialize menu bar
        
        Args:
            root: Root window
            callbacks: Dict of callback functions for menu items
        """
        self.root = root
        self.callbacks = callbacks
        
        self.menubar = tk.Menu(root)
        root.config(menu=self.menubar)
        
        self._create_file_menu()
        self._create_compile_menu()
        self._create_examples_menu()
        self._create_help_menu()
    
    def _create_file_menu(self):
        """Create File menu"""
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        
        file_menu.add_command(label="New", 
            command=self.callbacks.get('new_file'), accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", 
            command=self.callbacks.get('open_file'), accelerator="Ctrl+O")
        file_menu.add_command(label="Save", 
            command=self.callbacks.get('save_file'), accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", 
            command=self.callbacks.get('save_file_as'))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
    
    def _create_compile_menu(self):
        """Create Compile menu"""
        compile_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Compile", menu=compile_menu)
        
        compile_menu.add_command(label="Compile & Run", 
            command=self.callbacks.get('compile_and_run'), accelerator="F5")
        compile_menu.add_command(label="Compile Only", 
            command=self.callbacks.get('compile_only'), accelerator="F6")
        
        compile_menu.add_separator()
        compile_menu.add_command(label="Show Tokens", 
            command=self.callbacks.get('show_tokens'))
        compile_menu.add_command(label="Show AST", 
            command=self.callbacks.get('show_ast'))
        compile_menu.add_command(label="Show TAC", 
            command=self.callbacks.get('show_tac'))
        compile_menu.add_command(label="Show Optimized TAC", 
            command=self.callbacks.get('show_optimized_tac'))
    
    def _create_examples_menu(self):
        """Create Examples menu"""
        examples_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Examples", menu=examples_menu)
        
        examples = [
            ("Arithmetic", "tests/test1_arithmetic.calc"),
            ("Loops & Conditionals", "tests/test2_loops_conditionals.calc"),
            ("Arrays", "tests/test4_arrays.calc"),
            ("While Loops", "tests/test5_while_loop.calc"),
            ("For Loops", "test_for_loops.calc"),
            None,  # Separator
            ("Simple Typed Example", "test_simple_typed.calc"),
            ("Manual Math Functions", "test_manual_math.calc"),
            ("Matrix Operations", "test_matrix_operations.calc"),
            ("Matrix Operators (+, -, *, ^t, ^-1)", "test_matrix_operators.calc"),
            None,  # Separator
            ("Example", "example.calc"),
        ]
        
        for example in examples:
            if example is None:
                examples_menu.add_separator()
            else:
                label, filename = example
                examples_menu.add_command(label=label, 
                    command=lambda f=filename: self.callbacks.get('load_example')(f))
    
    def _create_help_menu(self):
        """Create Help menu"""
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        
        help_menu.add_command(label="Language Reference", 
            command=self.callbacks.get('show_language_reference'))
        help_menu.add_command(label="About", 
            command=self.callbacks.get('show_about'))
