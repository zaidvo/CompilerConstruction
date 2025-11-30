#!/usr/bin/env python3
"""
CalcScript++ Compiler - Modular GUI
A professional modular GUI for the CalcScript++ compiler
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import sys

# Add compiler phases to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / '2_Compiler_Phases' / 'Phase1_Lexical_Analysis'))
sys.path.insert(0, str(project_root / '2_Compiler_Phases' / 'Phase2_Syntax_Analysis'))
sys.path.insert(0, str(project_root / '2_Compiler_Phases' / 'Phase3_Semantic_Analysis'))
sys.path.insert(0, str(project_root / '2_Compiler_Phases' / 'Phase4_Intermediate_Code'))
sys.path.insert(0, str(project_root / '2_Compiler_Phases' / 'Phase5_Optimization'))
sys.path.insert(0, str(project_root / '2_Compiler_Phases' / 'Phase6_Code_Generation'))

# Import compiler modules
from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from ir_generator import IRGenerator
from optimizer import Optimizer
from interpreter import Interpreter

# Import GUI components
from gui_components import EditorPanel, OutputPanel, MenuBar
from gui_components.compiler_service import CompilerService

# Import error handler if available
try:
    from error_handler import reset_error_handler
except ImportError:
    reset_error_handler = lambda x: None


class CompilerGUI:
    """Professional modular GUI for CalcScript++ Compiler"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("CalcScript++ Compiler IDE")
        self.root.geometry("1400x900")
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # State variables
        self.current_file = None
        
        # Compiler service
        self.compiler = CompilerService(
            Lexer, Parser, SemanticAnalyzer,
            IRGenerator, Optimizer, Interpreter
        )
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Menu bar
        self.menu_bar = MenuBar(self.root, self._get_menu_callbacks())
        
        # Main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Editor
        left_panel = ttk.Frame(main_container)
        main_container.add(left_panel, weight=2)
        
        self.editor = EditorPanel(left_panel)
        
        # Add toolbar buttons
        self.editor.add_toolbar_button("▶ Run (F5)", self.compile_and_run)
        self.editor.add_toolbar_button("🔧 Compile (F6)", self.compile_only)
        self.editor.add_toolbar_button("💾 Save", self.save_file)
        self.editor.add_toolbar_button("📂 Open", self.open_file)
        
        self.editor.pack(fill=tk.BOTH, expand=True)
        
        # Right panel - Output
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=1)
        
        self.output = OutputPanel(right_panel)
        self.output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", 
                                    relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Keyboard shortcuts
        self._setup_shortcuts()
        
        # Load welcome message
        self.load_welcome_message()
    
    def _get_menu_callbacks(self):
        """Get callbacks for menu items"""
        return {
            'new_file': self.new_file,
            'open_file': self.open_file,
            'save_file': self.save_file,
            'save_file_as': self.save_file_as,
            'compile_and_run': self.compile_and_run,
            'compile_only': self.compile_only,
            'show_tokens': self.show_tokens,
            'show_ast': self.show_ast,
            'show_tac': self.show_tac,
            'show_optimized_tac': self.show_optimized_tac,
            'load_example': self.load_example,
            'show_language_reference': self.show_language_reference,
            'show_about': self.show_about
        }
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<F5>', lambda e: self.compile_and_run())
        self.root.bind('<F6>', lambda e: self.compile_only())
    
    # =========================================================================
    # FILE OPERATIONS
    # =========================================================================
    
    def new_file(self):
        """Create a new file"""
        if messagebox.askyesno("New File", "Clear current content?"):
            self.editor.clear()
            self.current_file = None
            self.output.clear_all()
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
                self.editor.set_content(content)
                self.current_file = filename
                self.status_bar.config(text=f"Opened: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file:\n{e}")
    
    def save_file(self):
        """Save the current file"""
        if self.current_file:
            try:
                content = self.editor.get_content()
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
            example_path = project_root / '4_Submission' / 'test_cases' / filename
            with open(example_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.editor.set_content(content)
            self.current_file = str(example_path)
            self.status_bar.config(text=f"Loaded example: {filename}")
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
# Quick Example with FOR LOOPS:

int sum = 0
for int i = 1; i <= 10; i = i + 1:
    sum = sum + i
end

print "Sum from 1 to 10:"
print sum

# Press F5 to compile and run!
"""
        self.editor.set_content(welcome)
    
    # =========================================================================
    # COMPILATION
    # =========================================================================
    
    def compile_and_run(self):
        """Compile and execute the program"""
        self.output.clear_all()
        self.status_bar.config(text="Compiling...")
        self.root.update()
        
        source_code = self.editor.get_content()
        
        try:
            # Compile
            results = self.compiler.compile(source_code)
            
            if results['errors']:
                self._show_compilation_error(results['errors'])
                return
            
            # Show compilation phases
            self._display_tokens(results['tokens'])
            self._display_ast(results['ast'])
            self._display_semantic(results['semantic_info'])
            self._display_tac(results['tac'])
            self._display_optimized_tac(results['optimized_tac'])
            
            # Execute
            output_widget = self.output.get_widget('output')
            output_widget.insert('1.0', "=== Program Output ===\n\n")
            
            program_output = self.compiler.execute()
            output_widget.insert(tk.END, program_output)
            
            self.status_bar.config(text="✓ Compilation and execution successful")
            self.output.switch_to_tab('output')
            
        except Exception as e:
            self._show_compilation_error(str(e))
    
    def compile_only(self):
        """Compile without executing"""
        self.output.clear_all()
        self.status_bar.config(text="Compiling...")
        self.root.update()
        
        source_code = self.editor.get_content()
        
        try:
            # Compile
            results = self.compiler.compile(source_code)
            
            if results['errors']:
                self._show_compilation_error(results['errors'])
                return
            
            # Show compilation phases
            self._display_tokens(results['tokens'])
            self._display_ast(results['ast'])
            self._display_semantic(results['semantic_info'])
            self._display_tac(results['tac'])
            self._display_optimized_tac(results['optimized_tac'])
            
            output_widget = self.output.get_widget('output')
            output_widget.insert('1.0', "✓ Compilation successful (not executed)\n")
            self.status_bar.config(text="✓ Compilation successful")
            
        except Exception as e:
            self._show_compilation_error(str(e))
    
    def _show_compilation_error(self, error):
        """Display compilation error"""
        error_msg = f"Error: {error}"
        output_widget = self.output.get_widget('output')
        output_widget.insert('1.0', error_msg)
        self.status_bar.config(text="✗ Compilation failed")
        messagebox.showerror("Compilation Error", error_msg)
    
    # =========================================================================
    # DISPLAY METHODS
    # =========================================================================
    
    def _display_tokens(self, tokens):
        """Display tokens in tokens tab"""
        from gui_components.formatters import TokenFormatter
        formatter = TokenFormatter()
        text = formatter.format(tokens)
        self.output.get_widget('tokens').insert('1.0', text)
    
    def _display_ast(self, ast):
        """Display AST in AST tab"""
        from gui_components.formatters import ASTFormatter
        formatter = ASTFormatter()
        text = formatter.format(ast)
        self.output.get_widget('ast').insert('1.0', text)
    
    def _display_semantic(self, semantic_info):
        """Display semantic analysis results"""
        from gui_components.formatters import SemanticFormatter
        formatter = SemanticFormatter()
        text = formatter.format(semantic_info)
        self.output.get_widget('semantic').insert('1.0', text)
    
    def _display_tac(self, tac):
        """Display TAC"""
        from gui_components.formatters import TACFormatter
        formatter = TACFormatter()
        text = formatter.format(tac)
        self.output.get_widget('tac').insert('1.0', text)
    
    def _display_optimized_tac(self, optimized_tac):
        """Display optimized TAC"""
        from gui_components.formatters import OptimizedTACFormatter
        formatter = OptimizedTACFormatter()
        text = formatter.format(optimized_tac, self.compiler.get_tac())
        self.output.get_widget('optimized').insert('1.0', text)
    
    def show_tokens(self):
        """Switch to tokens tab"""
        self.output.switch_to_tab('tokens')
    
    def show_ast(self):
        """Switch to AST tab"""
        self.output.switch_to_tab('ast')
    
    def show_tac(self):
        """Switch to TAC tab"""
        self.output.switch_to_tab('tac')
    
    def show_optimized_tac(self):
        """Switch to optimized TAC tab"""
        self.output.switch_to_tab('optimized')
    
    # =========================================================================
    # HELP DIALOGS
    # =========================================================================
    
    def show_language_reference(self):
        """Show language reference"""
        from gui_components.dialogs import LanguageReferenceDialog
        LanguageReferenceDialog(self.root)
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About CalcScript++ Compiler",
            "CalcScript++ Compiler IDE v3.0\n\n"
            "A complete 6-phase compiler with:\n"
            "• Error Recovery & Smart Suggestions\n"
            "• For-Loop Support\n"
            "• Matrix Operations\n\n"
            "University Compiler Project"
        )


def main():
    """Main entry point for GUI"""
    root = tk.Tk()
    app = CompilerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
