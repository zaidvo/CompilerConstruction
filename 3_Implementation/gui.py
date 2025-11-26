#!/usr/bin/env python3
"""
CalcScript++ Compiler - Graphical User Interface
A professional GUI for the CalcScript++ compiler with all compilation phases visible
Features explicit static typing and manual math implementations
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from pathlib import Path
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / '2_Compiler_Phases' / 'Phase1_Lexical_Analysis'))
sys.path.insert(0, str(Path(__file__).parent.parent / '2_Compiler_Phases' / 'Phase2_Syntax_Analysis'))
sys.path.insert(0, str(Path(__file__).parent.parent / '2_Compiler_Phases' / 'Phase3_Semantic_Analysis'))
sys.path.insert(0, str(Path(__file__).parent.parent / '2_Compiler_Phases' / 'Phase4_Intermediate_Code'))
sys.path.insert(0, str(Path(__file__).parent.parent / '2_Compiler_Phases' / 'Phase5_Optimization'))
sys.path.insert(0, str(Path(__file__).parent.parent / '2_Compiler_Phases' / 'Phase6_Code_Generation'))

from lexer import Lexer  # type: ignore
from parser import Parser  # type: ignore
from semantic_analyzer import SemanticAnalyzer  # type: ignore
from ir_generator import IRGenerator  # type: ignore
from optimizer import Optimizer  # type: ignore
from interpreter import Interpreter  # type: ignore


class CompilerGUI:
    """Professional GUI for CalcScript++ Compiler"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("CalcScript++ Compiler IDE")
        self.root.geometry("1400x900")
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Variables
        self.current_file = None
        self.tokens = None
        self.ast = None
        self.tac = None
        self.optimized_tac = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Compile menu
        compile_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Compile", menu=compile_menu)
        compile_menu.add_command(label="Compile & Run", command=self.compile_and_run, accelerator="F5")
        compile_menu.add_command(label="Compile Only", command=self.compile_only, accelerator="F6")
        compile_menu.add_separator()
        compile_menu.add_command(label="Show Tokens", command=self.show_tokens)
        compile_menu.add_command(label="Show AST", command=self.show_ast)
        compile_menu.add_command(label="Show TAC", command=self.show_tac)
        compile_menu.add_command(label="Show Optimized TAC", command=self.show_optimized_tac)
        
        # Examples menu
        examples_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Examples", menu=examples_menu)
        examples_menu.add_command(label="Arithmetic", command=lambda: self.load_example("tests/test1_arithmetic.calc"))
        examples_menu.add_command(label="Loops & Conditionals", command=lambda: self.load_example("tests/test2_loops_conditionals.calc"))
        examples_menu.add_command(label="Arrays", command=lambda: self.load_example("tests/test4_arrays.calc"))
        examples_menu.add_command(label="While Loops", command=lambda: self.load_example("tests/test5_while_loop.calc"))
        examples_menu.add_separator()
        examples_menu.add_command(label="Simple Typed Example", command=lambda: self.load_example("test_simple_typed.calc"))
        examples_menu.add_command(label="Manual Math Functions", command=lambda: self.load_example("test_manual_math.calc"))
        examples_menu.add_command(label="Matrix Operations", command=lambda: self.load_example("test_matrix_operations.calc"))
        examples_menu.add_command(label="Matrix Operators (+, -, *, ^t, ^-1)", command=lambda: self.load_example("test_matrix_operators.calc"))
        examples_menu.add_separator()
        examples_menu.add_command(label="Compliance Test", command=lambda: self.load_example("COMPLIANCE_TEST.calc"))
        examples_menu.add_command(label="Example", command=lambda: self.load_example("example.calc"))
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Language Reference", command=self.show_language_reference)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Editor
        left_panel = ttk.Frame(main_container)
        main_container.add(left_panel, weight=2)
        
        # Editor toolbar
        editor_toolbar = ttk.Frame(left_panel)
        editor_toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(editor_toolbar, text="Source Code Editor", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        ttk.Button(editor_toolbar, text="▶ Run (F5)", command=self.compile_and_run).pack(side=tk.RIGHT, padx=2)
        ttk.Button(editor_toolbar, text="🔧 Compile (F6)", command=self.compile_only).pack(side=tk.RIGHT, padx=2)
        ttk.Button(editor_toolbar, text="💾 Save", command=self.save_file).pack(side=tk.RIGHT, padx=2)
        ttk.Button(editor_toolbar, text="📂 Open", command=self.open_file).pack(side=tk.RIGHT, padx=2)
        
        # Editor with line numbers
        editor_frame = ttk.Frame(left_panel)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Line numbers
        self.line_numbers = tk.Text(editor_frame, width=4, padx=3, takefocus=0, border=0,
                                     background='lightgray', state='disabled', wrap='none')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Editor
        self.editor = scrolledtext.ScrolledText(editor_frame, wrap=tk.NONE, undo=True,
                                                 font=('Consolas', 11))
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.editor.bind('<KeyRelease>', self.update_line_numbers)
        self.editor.bind('<MouseWheel>', self.update_line_numbers)
        
        # Syntax highlighting
        self.setup_syntax_highlighting()
        
        # Right panel - Compilation phases
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=1)
        
        # Notebook for phases
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Output tab
        output_frame = ttk.Frame(self.notebook)
        self.notebook.add(output_frame, text="📤 Output")
        
        ttk.Label(output_frame, text="Program Output", font=('Arial', 10, 'bold')).pack(pady=5)
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, 
                                                      font=('Consolas', 10), height=15)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tokens tab
        tokens_frame = ttk.Frame(self.notebook)
        self.notebook.add(tokens_frame, text="🔤 Tokens")
        
        ttk.Label(tokens_frame, text="Phase 1: Lexical Analysis", font=('Arial', 10, 'bold')).pack(pady=5)
        self.tokens_text = scrolledtext.ScrolledText(tokens_frame, wrap=tk.WORD,
                                                      font=('Consolas', 9))
        self.tokens_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # AST tab
        ast_frame = ttk.Frame(self.notebook)
        self.notebook.add(ast_frame, text="🌳 AST")
        
        ttk.Label(ast_frame, text="Phase 2: Syntax Analysis", font=('Arial', 10, 'bold')).pack(pady=5)
        self.ast_text = scrolledtext.ScrolledText(ast_frame, wrap=tk.WORD,
                                                   font=('Consolas', 9))
        self.ast_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Semantic tab
        semantic_frame = ttk.Frame(self.notebook)
        self.notebook.add(semantic_frame, text="✓ Semantic")
        
        ttk.Label(semantic_frame, text="Phase 3: Semantic Analysis", font=('Arial', 10, 'bold')).pack(pady=5)
        self.semantic_text = scrolledtext.ScrolledText(semantic_frame, wrap=tk.WORD,
                                                        font=('Consolas', 9))
        self.semantic_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # TAC tab
        tac_frame = ttk.Frame(self.notebook)
        self.notebook.add(tac_frame, text="📝 TAC")
        
        ttk.Label(tac_frame, text="Phase 4: Intermediate Code", font=('Arial', 10, 'bold')).pack(pady=5)
        self.tac_text = scrolledtext.ScrolledText(tac_frame, wrap=tk.WORD,
                                                   font=('Consolas', 9))
        self.tac_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Optimized TAC tab
        opt_frame = ttk.Frame(self.notebook)
        self.notebook.add(opt_frame, text="⚡ Optimized")
        
        ttk.Label(opt_frame, text="Phase 5: Optimization", font=('Arial', 10, 'bold')).pack(pady=5)
        self.opt_text = scrolledtext.ScrolledText(opt_frame, wrap=tk.WORD,
                                                   font=('Consolas', 9))
        self.opt_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<F5>', lambda e: self.compile_and_run())
        self.root.bind('<F6>', lambda e: self.compile_only())
        
        # Initial content
        self.load_welcome_message()
        self.update_line_numbers()
    
    def setup_syntax_highlighting(self):
        """Setup syntax highlighting for CalcScript+"""
        # Keywords
        self.editor.tag_config('keyword', foreground='blue', font=('Consolas', 11, 'bold'))
        self.editor.tag_config('string', foreground='green')
        self.editor.tag_config('comment', foreground='gray', font=('Consolas', 11, 'italic'))
        self.editor.tag_config('number', foreground='purple')
        
        self.keywords = ['int', 'long', 'float', 'char', 'string', 'boolean', 'bool', 'array', 'matrix',
                        'print', 'repeat', 'times', 'if', 'else',
                        'function', 'return', 'end', 'while', 'input', 'break', 'continue',
                        'true', 'false', 'and', 'or', 'not']
    
    def highlight_syntax(self, event=None):
        """Apply syntax highlighting"""
        # Remove existing tags
        for tag in ['keyword', 'string', 'comment', 'number']:
            self.editor.tag_remove(tag, '1.0', tk.END)
        
        content = self.editor.get('1.0', tk.END)
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Comments
            if '#' in line:
                comment_start = line.index('#')
                self.editor.tag_add('comment', f'{i}.{comment_start}', f'{i}.end')
            
            # Strings
            in_string = False
            for j, char in enumerate(line):
                if char == '"':
                    if not in_string:
                        string_start = j
                        in_string = True
                    else:
                        self.editor.tag_add('string', f'{i}.{string_start}', f'{i}.{j+1}')
                        in_string = False
            
            # Keywords
            words = line.split()
            col = 0
            for word in words:
                if word in self.keywords:
                    start = line.find(word, col)
                    if start != -1:
                        self.editor.tag_add('keyword', f'{i}.{start}', f'{i}.{start+len(word)}')
                        col = start + len(word)
    
    def update_line_numbers(self, event=None):
        """Update line numbers"""
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        
        line_count = self.editor.get('1.0', tk.END).count('\n')
        line_numbers_string = '\n'.join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.insert('1.0', line_numbers_string)
        self.line_numbers.config(state='disabled')
        
        # Apply syntax highlighting
        self.highlight_syntax()
    
    def new_file(self):
        """Create a new file"""
        if messagebox.askyesno("New File", "Clear current content?"):
            self.editor.delete('1.0', tk.END)
            self.current_file = None
            self.clear_outputs()
            self.status_bar.config(text="New file")
    
    def open_file(self):
        """Open a file"""
        filename = filedialog.askopenfilename(
            title="Open CalcScript++ File",
            filetypes=[("CalcScript++ Files", "*.calc"), ("All Files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.editor.delete('1.0', tk.END)
                self.editor.insert('1.0', content)
                self.current_file = filename
                self.status_bar.config(text=f"Opened: {filename}")
                self.update_line_numbers()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file:\n{e}")
    
    def save_file(self):
        """Save the current file"""
        if self.current_file:
            try:
                content = self.editor.get('1.0', tk.END)
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_bar.config(text=f"Saved: {self.current_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{e}")
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """Save file with a new name"""
        filename = filedialog.asksaveasfilename(
            title="Save CalcScript++ File",
            defaultextension=".calc",
            filetypes=[("CalcScript++ Files", "*.calc"), ("All Files", "*.*")]
        )
        if filename:
            self.current_file = filename
            self.save_file()
    
    def load_example(self, filename):
        """Load an example file"""
        try:
            # Build the full path relative to the project root
            project_root = Path(__file__).parent.parent
            example_path = project_root / '4_Submission' / 'test_cases' / filename
            
            with open(example_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.editor.delete('1.0', tk.END)
            self.editor.insert('1.0', content)
            self.current_file = str(example_path)
            self.status_bar.config(text=f"Loaded example: {filename}")
            self.update_line_numbers()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load example:\n{e}")
    
    def load_welcome_message(self):
        """Load welcome message"""
        welcome = """# Welcome to CalcScript++ Compiler IDE!
# 
# This is a complete compiler with all 6 phases:
# 1. Lexical Analysis (Tokenization)
# 2. Syntax Analysis (Parsing)
# 3. Semantic Analysis (Type Checking)
# 4. Intermediate Code Generation (TAC)
# 5. Optimization
# 6. Code Generation (Execution)
#
# CalcScript++ uses EXPLICIT TYPING - all variables must declare their type!
#
# Try the examples from the Examples menu or write your own code!
#
# Quick Example:

int x = 10
int y = 20
int total = x + y

print "Sum is:"
print total

if total > 25:
    print "Greater than 25!"
else:
    print "Not greater"
end

# Press F5 to compile and run!
"""
        self.editor.insert('1.0', welcome)
        self.update_line_numbers()
    
    def clear_outputs(self):
        """Clear all output windows"""
        for text_widget in [self.output_text, self.tokens_text, self.ast_text,
                           self.semantic_text, self.tac_text, self.opt_text]:
            text_widget.delete('1.0', tk.END)
    
    def compile_and_run(self):
        """Compile and execute the program"""
        self.clear_outputs()
        self.status_bar.config(text="Compiling...")
        self.root.update()
        
        source_code = self.editor.get('1.0', tk.END)
        
        try:
            # Phase 1: Lexical Analysis
            lexer = Lexer(source_code)
            self.tokens = lexer.tokenize()
            self.show_tokens()
            
            # Phase 2: Syntax Analysis
            parser = Parser(self.tokens)
            self.ast = parser.parse()
            self.show_ast()
            
            # Phase 3: Semantic Analysis
            analyzer = SemanticAnalyzer()
            analyzer.analyze(self.ast)
            self.semantic_text.insert('1.0', "[OK] Semantic analysis passed\n\n")
            self.semantic_text.insert(tk.END, "Symbol Table:\n")
            self.semantic_text.insert(tk.END, "=" * 70 + "\n")
            self.semantic_text.insert(tk.END, f"{'Name':<20} {'Type':<15} {'Value Type':<15} {'Scope'}\n")
            self.semantic_text.insert(tk.END, "-" * 70 + "\n")
            
            # Separate built-in functions from user-defined symbols
            builtins = {k: v for k, v in analyzer.global_scope.symbols.items() if v['type'] == 'function' and k in ['sum', 'max', 'min', 'mean', 'median', 'stdev', 'variance', 'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'sinh', 'cosh', 'tanh', 'exp', 'ln', 'lg', 'log', 'log10', 'log2', 'sqrt', 'cbrt', 'floor', 'ceil', 'round', 'abs', 'factorial', 'gcd', 'lcm', 'pi', 'e', 'radians', 'degrees', 'matrix_det', 'matrix_trace']}
            user_defined = {k: v for k, v in analyzer.global_scope.symbols.items() if k not in builtins}
            
            # Show user-defined symbols first
            if user_defined:
                for name, info in user_defined.items():
                    sym_type = info.get('type', 'unknown')
                    val_type = info.get('value_type', 'unknown')
                    scope = info.get('scope_level', 0)
                    self.semantic_text.insert(tk.END, f"{name:<20} {sym_type:<15} {val_type:<15} {scope}\n")
            
            # Show summary of built-in functions
            if builtins:
                self.semantic_text.insert(tk.END, "\n" + "=" * 70 + "\n")
                self.semantic_text.insert(tk.END, f"Built-in Functions: {len(builtins)} functions available\n")
                self.semantic_text.insert(tk.END, "-" * 70 + "\n")
                
                # Group by category
                categories = {
                    'Array': ['sum', 'max', 'min'],
                    'Statistics': ['mean', 'median', 'stdev', 'variance'],
                    'Trigonometry': ['sin', 'cos', 'tan', 'asin', 'acos', 'atan'],
                    'Hyperbolic': ['sinh', 'cosh', 'tanh'],
                    'Exponential/Log': ['exp', 'ln', 'lg', 'log', 'log10', 'log2'],
                    'Roots': ['sqrt', 'cbrt'],
                    'Rounding': ['floor', 'ceil', 'round', 'abs'],
                    'Number Theory': ['factorial', 'gcd', 'lcm'],
                    'Constants': ['pi', 'e'],
                    'Angle Mode': ['radians', 'degrees'],
                    'Matrix': ['matrix_det', 'matrix_trace']
                }
                
                for category, funcs in categories.items():
                    available = [f for f in funcs if f in builtins]
                    if available:
                        self.semantic_text.insert(tk.END, f"{category}: {', '.join(available)}\n")
            
            # Phase 4: IR Generation
            ir_gen = IRGenerator()
            self.tac = ir_gen.generate(self.ast)
            self.show_tac()
            
            # Phase 5: Optimization
            optimizer = Optimizer()
            self.optimized_tac = optimizer.optimize(self.tac)
            self.show_optimized_tac()
            
            # Phase 6: Execution
            self.output_text.insert('1.0', "=== Program Output ===\n\n")
            interpreter = Interpreter()
            
            # Redirect stdout to capture output
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            try:
                interpreter.execute(self.optimized_tac)
                output = sys.stdout.getvalue()
                self.output_text.insert(tk.END, output)
            finally:
                sys.stdout = old_stdout
            
            self.status_bar.config(text="✓ Compilation and execution successful")
            self.notebook.select(0)  # Show output tab
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.output_text.insert('1.0', error_msg)
            self.status_bar.config(text="✗ Compilation failed")
            messagebox.showerror("Compilation Error", error_msg)
    
    def compile_only(self):
        """Compile without executing"""
        self.clear_outputs()
        self.status_bar.config(text="Compiling...")
        self.root.update()
        
        source_code = self.editor.get('1.0', tk.END)
        
        try:
            # Phase 1: Lexical Analysis
            lexer = Lexer(source_code)
            self.tokens = lexer.tokenize()
            self.show_tokens()
            
            # Phase 2: Syntax Analysis
            parser = Parser(self.tokens)
            self.ast = parser.parse()
            self.show_ast()
            
            # Phase 3: Semantic Analysis
            analyzer = SemanticAnalyzer()
            analyzer.analyze(self.ast)
            self.semantic_text.insert('1.0', "[OK] Semantic analysis passed\n\n")
            self.semantic_text.insert(tk.END, "Symbol Table:\n")
            self.semantic_text.insert(tk.END, "=" * 70 + "\n")
            self.semantic_text.insert(tk.END, f"{'Name':<20} {'Type':<15} {'Value Type':<15} {'Scope'}\n")
            self.semantic_text.insert(tk.END, "-" * 70 + "\n")
            
            # Separate built-in functions from user-defined symbols
            builtins = {k: v for k, v in analyzer.global_scope.symbols.items() if v['type'] == 'function' and k in ['sum', 'max', 'min', 'mean', 'median', 'stdev', 'variance', 'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'sinh', 'cosh', 'tanh', 'exp', 'ln', 'lg', 'log', 'log10', 'log2', 'sqrt', 'cbrt', 'floor', 'ceil', 'round', 'abs', 'factorial', 'gcd', 'lcm', 'pi', 'e', 'radians', 'degrees', 'matrix_det', 'matrix_trace']}
            user_defined = {k: v for k, v in analyzer.global_scope.symbols.items() if k not in builtins}
            
            # Show user-defined symbols first
            if user_defined:
                for name, info in user_defined.items():
                    sym_type = info.get('type', 'unknown')
                    val_type = info.get('value_type', 'unknown')
                    scope = info.get('scope_level', 0)
                    self.semantic_text.insert(tk.END, f"{name:<20} {sym_type:<15} {val_type:<15} {scope}\n")
            
            # Show summary of built-in functions
            if builtins:
                self.semantic_text.insert(tk.END, "\n" + "=" * 70 + "\n")
                self.semantic_text.insert(tk.END, f"Built-in Functions: {len(builtins)} functions available\n")
                self.semantic_text.insert(tk.END, "-" * 70 + "\n")
                
                # Group by category
                categories = {
                    'Array': ['sum', 'max', 'min'],
                    'Statistics': ['mean', 'median', 'stdev', 'variance'],
                    'Trigonometry': ['sin', 'cos', 'tan', 'asin', 'acos', 'atan'],
                    'Hyperbolic': ['sinh', 'cosh', 'tanh'],
                    'Exponential/Log': ['exp', 'ln', 'lg', 'log', 'log10', 'log2'],
                    'Roots': ['sqrt', 'cbrt'],
                    'Rounding': ['floor', 'ceil', 'round', 'abs'],
                    'Number Theory': ['factorial', 'gcd', 'lcm'],
                    'Constants': ['pi', 'e'],
                    'Angle Mode': ['radians', 'degrees'],
                    'Matrix': ['matrix_det', 'matrix_trace']
                }
                
                for category, funcs in categories.items():
                    available = [f for f in funcs if f in builtins]
                    if available:
                        self.semantic_text.insert(tk.END, f"{category}: {', '.join(available)}\n")
            
            # Phase 4: IR Generation
            ir_gen = IRGenerator()
            self.tac = ir_gen.generate(self.ast)
            self.show_tac()
            
            # Phase 5: Optimization
            optimizer = Optimizer()
            self.optimized_tac = optimizer.optimize(self.tac)
            self.show_optimized_tac()
            
            self.output_text.insert('1.0', "✓ Compilation successful (not executed)\n")
            self.status_bar.config(text="✓ Compilation successful")
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.output_text.insert('1.0', error_msg)
            self.status_bar.config(text="✗ Compilation failed")
            messagebox.showerror("Compilation Error", error_msg)
    
    def show_tokens(self):
        """Display tokens"""
        if self.tokens:
            self.tokens_text.delete('1.0', tk.END)
            self.tokens_text.insert('1.0', "Tokens Generated:\n")
            self.tokens_text.insert(tk.END, "=" * 60 + "\n\n")
            for token in self.tokens:
                if token.type.name != 'EOF':
                    self.tokens_text.insert(tk.END, f"{token}\n")
    
    def show_ast(self):
        """Display AST"""
        if self.ast:
            self.ast_text.delete('1.0', tk.END)
            self.ast_text.insert('1.0', "Abstract Syntax Tree:\n")
            self.ast_text.insert(tk.END, "=" * 60 + "\n\n")
            self.print_ast(self.ast, 0)
    
    def print_ast(self, node, indent):
        """Recursively print AST"""
        prefix = "  " * indent
        node_name = node.__class__.__name__
        self.ast_text.insert(tk.END, f"{prefix}{node_name}\n")
        
        if hasattr(node, '__dict__'):
            for key, value in node.__dict__.items():
                if isinstance(value, list):
                    if value and hasattr(value[0], '__class__'):
                        self.ast_text.insert(tk.END, f"{prefix}  {key}:\n")
                        for item in value:
                            self.print_ast(item, indent + 2)
                elif hasattr(value, '__class__') and 'Node' in value.__class__.__name__:
                    self.ast_text.insert(tk.END, f"{prefix}  {key}:\n")
                    self.print_ast(value, indent + 2)
    
    def show_tac(self):
        """Display TAC"""
        if self.tac:
            self.tac_text.delete('1.0', tk.END)
            self.tac_text.insert('1.0', "Three-Address Code:\n")
            self.tac_text.insert(tk.END, "=" * 60 + "\n\n")
            for i, instr in enumerate(self.tac):
                self.tac_text.insert(tk.END, f"{i:3d}: {instr}\n")
    
    def show_optimized_tac(self):
        """Display optimized TAC"""
        if self.optimized_tac:
            self.opt_text.delete('1.0', tk.END)
            self.opt_text.insert('1.0', "Optimized Three-Address Code:\n")
            self.opt_text.insert(tk.END, "=" * 60 + "\n\n")
            for i, instr in enumerate(self.optimized_tac):
                self.opt_text.insert(tk.END, f"{i:3d}: {instr}\n")
            
            # Show optimization stats
            original_count = len(self.tac) if self.tac else 0
            optimized_count = len(self.optimized_tac)
            reduction = original_count - optimized_count
            
            self.opt_text.insert(tk.END, f"\n{'=' * 60}\n")
            self.opt_text.insert(tk.END, f"Original instructions: {original_count}\n")
            self.opt_text.insert(tk.END, f"Optimized instructions: {optimized_count}\n")
            self.opt_text.insert(tk.END, f"Reduction: {reduction} instructions\n")
    
    def show_language_reference(self):
        """Show language reference"""
        ref_window = tk.Toplevel(self.root)
        ref_window.title("CalcScript++ Language Reference")
        ref_window.geometry("800x600")
        
        text = scrolledtext.ScrolledText(ref_window, wrap=tk.WORD, font=('Consolas', 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        reference = """
CalcScript++ Language Reference
===============================

TYPE KEYWORDS:
  int            - Integer type
  long           - Long integer type
  float          - Floating point type
  char           - Character type
  string         - String type
  boolean/bool   - Boolean type
  array          - Array type
  matrix         - Matrix type

KEYWORDS:
  print          - Print statement
  repeat...times - Repeat loop
  if             - If statement
  else           - Else statement
  function       - Function definition
  return         - Return statement
  end            - End block
  while          - While loop
  input          - Input statement
  break          - Break statement
  continue       - Continue statement
  true           - True (boolean)
  false          - False (boolean)

OPERATORS:
  Arithmetic: +, -, *, /, %, ^
  Comparison: >, <, >=, <=, ==, !=
  Logical: and, or, not
  Assignment: =

BUILT-IN FUNCTIONS:

Array Functions:
  sum(arr)       - Sum of array elements
  max(arr)       - Maximum value in array
  min(arr)       - Minimum value in array

Statistical Functions:
  mean(arr)      - Average of array elements
  median(arr)    - Median of array elements
  stdev(arr)     - Standard deviation
  variance(arr)  - Variance of array

Trigonometric (supports radians/degrees):
  radians()      - Set angle mode to radians
  degrees()      - Set angle mode to degrees
  sin(x), cos(x), tan(x)
  asin(x), acos(x), atan(x)
  sinh(x), cosh(x), tanh(x)

Exponential & Logarithmic:
  exp(x)         - e^x
  ln(x)          - Natural logarithm (base e)
  lg(x)          - Base-10 logarithm
  log(x, base)   - Custom base logarithm
  log10(x)       - Base-10 logarithm
  log2(x)        - Base-2 logarithm

Power & Roots:
  sqrt(x)        - Square root
  cbrt(x)        - Cube root

Rounding:
  floor(x)       - Round down
  ceil(x)        - Round up
  round(x)       - Round to nearest
  abs(x)         - Absolute value

Number Theory:
  factorial(n)   - n! (factorial)
  gcd(a, b)      - Greatest common divisor
  lcm(a, b)      - Least common multiple

Matrix Operations:
  M1 + M2            - Matrix addition (replaces matrix_add)
  M1 - M2            - Matrix subtraction (replaces matrix_sub)
  M1 * M2            - Matrix multiplication (replaces matrix_mul)
  M ^ t              - Matrix transpose (replaces matrix_transpose)
  M ^ -1             - Matrix inverse
  matrix_det(A)      - Determinant (utility function)
  matrix_trace(A)    - Trace (utility function)

Constants:
  pi()           - π (3.14159...)
  e()            - e (2.71828...)

EXAMPLES:

1. Variables (EXPLICIT TYPING REQUIRED):
   int x = 10
   string name = "Ali"
   float pi_value = 3.14159
   boolean is_valid = true

2. Conditionals:
   if x > 5:
       print "Greater"
   else:
       print "Smaller"
   end

3. Loops:
   repeat 5 times:
       print "Hello"
   end

4. Functions:
   function int add(int a, int b):
       return a + b
   end

5. Arrays:
   array arr = [1, 2, 3]
   int total = sum(arr)

6. Math Functions:
   degrees()  # Set to degree mode
   int angle = 90
   float result = sin(angle)  # sin(90°)
   
   radians()  # Set to radian mode
   float x = log(8, 2)  # log base 2 of 8 = 3
   
7. Matrices with Operators:
   matrix M1 = [[1, 2], [3, 4]]
   matrix M2 = [[5, 6], [7, 8]]
   matrix M3 = M1 + M2  # Matrix addition
   matrix M4 = M1 * M2  # Matrix multiplication
   matrix MT = M1 ^ t   # Transpose
   matrix MI = M1 ^ -1  # Inverse
"""
        text.insert('1.0', reference)
        text.config(state='disabled')
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About CalcScript++ Compiler",
            "CalcScript++ Compiler IDE\n\n"
            "A complete 6-phase compiler for CalcScript++\n"
            "programming language with explicit static typing.\n\n"
            "Features:\n"
            "• Explicit type system (int, float, string, boolean, array, matrix)\n"
            "• Manual math implementations (no Python wrappers)\n"
            "• VM-based execution\n"
            "• 30+ built-in mathematical functions\n\n"
            "Phases:\n"
            "1. Lexical Analysis\n"
            "2. Syntax Analysis\n"
            "3. Semantic Analysis\n"
            "4. Intermediate Code Generation\n"
            "5. Optimization\n"
            "6. Code Generation/Execution\n\n"
            "Version 2.0\n"
            "University Compiler Project"
        )


def main():
    """Main entry point for GUI"""
    root = tk.Tk()
    app = CompilerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
