"""
Main Window for Modern GUI
Brings together all components with unique purple-gold-teal design
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
import sys

# Import modern GUI components
from .theme import ModernTheme
from .code_editor import CodeEditor
from .output_sections import OutputSections
from .phase_toolbar import PhaseToolbar
from .phase_service import PhaseExecutionService
from .formatters import (
    TokensFormatter, ASTFormatter, SemanticFormatter,
    IRFormatter, OptimizerFormatter, BytecodeFormatter, ErrorsFormatter
)


class ModernCompilerGUI:
    """Modern GUI for CalcScript++ Compiler with unique design"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("CalcScript++ Compiler - Modern Edition")
        self.root.geometry("1600x900")
        self.root.configure(bg=ModernTheme.DARKER_NAVY)
        
        # State
        self.current_file = None
        self.phase_service = PhaseExecutionService()
        
        # Configure styles
        self._configure_styles()
        
        # Build UI
        self._build_ui()
        
        # Load welcome code
        self._load_welcome_code()
    
    def _configure_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame styles
        style.configure('Dark.TFrame', background=ModernTheme.DARK_NAVY)
        style.configure('Panel.TFrame', background=ModernTheme.PANEL_BG)
    
    def _build_ui(self):
        """Build the user interface"""
        # Top toolbar with phase buttons
        self.phase_toolbar = PhaseToolbar(
            self.root,
            {
                'lex': self.run_phase_lex,
                'parse': self.run_phase_parse,
                'check': self.run_phase_check,
                'ir': self.run_phase_ir,
                'opt': self.run_phase_opt,
                'run': self.run_phase_run,
                'run_all': self.run_all_phases
            }
        )
        self.phase_toolbar.pack(fill=tk.X, side=tk.TOP)
        
        # Editor toolbar (above editor)
        self.editor_toolbar = self._create_editor_toolbar()
        self.editor_toolbar.pack(fill=tk.X, side=tk.TOP)
        
        # Main content area - horizontal split
        self.main_paned = tk.PanedWindow(
            self.root,
            orient=tk.HORIZONTAL,
            bg=ModernTheme.DARKER_NAVY,
            sashwidth=5,
            sashrelief=tk.RAISED,
            bd=0
        )
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Code editor
        left_panel = tk.Frame(self.main_paned, bg=ModernTheme.DARK_NAVY)
        self.main_paned.add(left_panel, width=750)
        
        # Editor label
        editor_label = tk.Label(
            left_panel,
            text="📝 Source Code Editor",
            bg=ModernTheme.SECTION_HEADER,
            fg=ModernTheme.TEXT_FG,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_LARGE, "bold"),
            anchor=tk.W,
            padx=10,
            pady=8
        )
        editor_label.pack(fill=tk.X)
        
        # Code editor
        self.editor = CodeEditor(left_panel)
        self.editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right panel - Output sections
        right_panel = tk.Frame(self.main_paned, bg=ModernTheme.DARKER_NAVY)
        self.main_paned.add(right_panel, width=750)
        
        # Output label
        output_label = tk.Label(
            right_panel,
            text="📊 Compilation Results",
            bg=ModernTheme.SECTION_HEADER,
            fg=ModernTheme.TEXT_FG,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_LARGE, "bold"),
            anchor=tk.W,
            padx=10,
            pady=8
        )
        output_label.pack(fill=tk.X)
        
        # Output sections
        self.output_sections = OutputSections(right_panel)
        self.output_sections.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready | No file loaded",
            bg=ModernTheme.SECTION_HEADER,
            fg=ModernTheme.TEXT_FG,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE),
            anchor=tk.W,
            padx=10,
            pady=5
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def _create_editor_toolbar(self):
        """Create toolbar above editor with file operations"""
        toolbar = tk.Frame(self.root, bg=ModernTheme.PANEL_BG, height=45)
        toolbar.pack_propagate(False)
        
        # Example programs dropdown
        tk.Label(
            toolbar,
            text="Examples:",
            bg=ModernTheme.PANEL_BG,
            fg=ModernTheme.TEXT_FG,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE)
        ).pack(side=tk.LEFT, padx=(10, 5), pady=10)
        
        self.example_var = tk.StringVar(value="Select Example...")
        example_menu = ttk.Combobox(
            toolbar,
            textvariable=self.example_var,
            state='readonly',
            width=25
        )
        example_menu['values'] = [
            'example.calc',
            'test_for_loops.calc',
            'test_matrix_operations.calc',
            'test_simple_typed.calc'
        ]
        example_menu.bind('<<ComboboxSelected>>', self._on_example_selected)
        example_menu.pack(side=tk.LEFT, padx=5, pady=10)
        
        # File operation buttons
        btn_configs = [
            ('🆕 New', self.new_file),
            ('📂 Open', self.open_file),
            ('💾 Save', self.save_file),
            ('💾 Save As...', self.save_file_as)
        ]
        
        for text, command in btn_configs:
            btn = tk.Button(
                toolbar,
                text=text,
                bg=ModernTheme.DEEP_PURPLE,
                fg=ModernTheme.TEXT_FG,
                font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE),
                relief=tk.FLAT,
                bd=0,
                padx=12,
                pady=6,
                cursor="hand2",
                command=command
            )
            btn.pack(side=tk.LEFT, padx=5, pady=10)
            
            # Hover effects
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg=ModernTheme.LIGHT_PURPLE))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(bg=ModernTheme.DEEP_PURPLE))
        
        return toolbar
    
    def _load_welcome_code(self):
        """Load welcome/example code"""
        welcome = """# Welcome to CalcScript++ Compiler - Modern Edition!
# 
# This compiler has 6 phases:
# Phase 1: Lexical Analysis (Tokenization)
# Phase 2: Syntax Analysis (AST Generation)
# Phase 3: Semantic Analysis (Type Checking)
# Phase 4: IR Generation (Three-Address Code)
# Phase 5: Optimization (Code Improvement)
# Phase 6: Code Execution (Interpreter)
#
# Example with FOR LOOPS:

int sum = 0
for int i = 1; i <= 10; i = i + 1:
    sum = sum + i
end

print "Sum from 1 to 10:"
print sum

# Click "▶ RUN ALL PHASES" to compile and execute!
# Or click individual phase buttons to see step-by-step results.
"""
        self.editor.set_content(welcome)
    
    def _on_example_selected(self, event=None):
        """Load selected example"""
        example_name = self.example_var.get()
        if example_name and example_name != "Select Example...":
            self.load_example(example_name)
    
    # =========================================================================
    # FILE OPERATIONS
    # =========================================================================
    
    def new_file(self):
        """Create new file"""
        if messagebox.askyesno("New File", "Clear current content?"):
            self.editor.clear()
            self.current_file = None
            self.output_sections.clear_all()
            self.phase_service.reset()
            self.status_bar.config(text="Ready | New file")
    
    def open_file(self):
        """Open file"""
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
                self.output_sections.clear_all()
                self.phase_service.reset()
                self.status_bar.config(text=f"Ready | {Path(filename).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file:\n{e}")
    
    def save_file(self):
        """Save current file"""
        if self.current_file:
            try:
                content = self.editor.get_content()
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_bar.config(text=f"Saved | {Path(self.current_file).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{e}")
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """Save file as"""
        filename = filedialog.asksaveasfilename(
            title="Save CalcScript++ File",
            defaultextension=".calc",
            filetypes=[("CalcScript++ Files", "*.calc"), ("All Files", "*.*")]
        )
        if filename:
            self.current_file = filename
            self.save_file()
    
    def load_example(self, filename):
        """Load example file"""
        try:
            project_root = Path(__file__).parent.parent.parent
            example_path = project_root / '4_Submission' / 'test_cases' / filename
            
            if example_path.exists():
                with open(example_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.editor.set_content(content)
                self.current_file = str(example_path)
                self.output_sections.clear_all()
                self.phase_service.reset()
                self.status_bar.config(text=f"Ready | Example: {filename}")
            else:
                messagebox.showerror("Error", f"Example file not found: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load example:\n{e}")
    
    # =========================================================================
    # PHASE EXECUTION
    # =========================================================================
    
    def run_phase_lex(self):
        """Run Phase 1: Lexical Analysis"""
        source_code = self.editor.get_content()
        self.output_sections.clear_all()
        
        self.status_bar.config(text="Running Phase 1: Lexical Analysis...")
        self.root.update()
        
        result = self.phase_service.execute_phase_lex(source_code)
        
        if result['success']:
            # Format and display tokens
            formatted = TokensFormatter.format(result['tokens'])
            self.output_sections.set_content('tokens', formatted, auto_expand=True)
            self.status_bar.config(text="✓ Phase 1 Complete: Lexical Analysis")
        else:
            # Show error
            self._show_errors(result.get('errors', []))
            self.status_bar.config(text="✗ Phase 1 Failed: Lexical Analysis")
    
    def run_phase_parse(self):
        """Run Phase 2: Syntax Analysis"""
        if not self.phase_service.tokens:
            messagebox.showwarning("Warning", "Please run Phase 1 (LEX) first.")
            return
        
        self.status_bar.config(text="Running Phase 2: Syntax Analysis...")
        self.root.update()
        
        result = self.phase_service.execute_phase_parse()
        
        if result['success']:
            # Format and display AST
            formatted = ASTFormatter.format(result['ast'])
            self.output_sections.set_content('ast', formatted, auto_expand=True)
            self.status_bar.config(text="✓ Phase 2 Complete: Syntax Analysis")
        else:
            # Show error
            self._show_errors(result.get('errors', []))
            self.status_bar.config(text="✗ Phase 2 Failed: Syntax Analysis")
    
    def run_phase_check(self):
        """Run Phase 3: Semantic Analysis"""
        if not self.phase_service.ast:
            messagebox.showwarning("Warning", "Please run Phase 2 (PARSE) first.")
            return
        
        self.status_bar.config(text="Running Phase 3: Semantic Analysis...")
        self.root.update()
        
        result = self.phase_service.execute_phase_check()
        
        if result['success']:
            # Format and display semantic info
            formatted = SemanticFormatter.format(result['semantic_info'])
            self.output_sections.set_content('semantic', formatted, auto_expand=True)
            self.status_bar.config(text="✓ Phase 3 Complete: Semantic Analysis")
        else:
            # Show error
            self._show_errors(result.get('errors', []))
            self.status_bar.config(text="✗ Phase 3 Failed: Semantic Analysis")
    
    def run_phase_ir(self):
        """Run Phase 4: IR Generation"""
        if not self.phase_service.ast:
            messagebox.showwarning("Warning", "Please run Phase 3 (CHECK) first.")
            return
        
        self.status_bar.config(text="Running Phase 4: IR Generation...")
        self.root.update()
        
        result = self.phase_service.execute_phase_ir()
        
        if result['success']:
            # Format and display IR
            formatted = IRFormatter.format(result['tac'])
            self.output_sections.set_content('ir', formatted, auto_expand=True)
            self.status_bar.config(text="✓ Phase 4 Complete: IR Generation")
        else:
            # Show error
            self._show_errors(result.get('errors', []))
            self.status_bar.config(text="✗ Phase 4 Failed: IR Generation")
    
    def run_phase_opt(self):
        """Run Phase 5: Optimization"""
        if not self.phase_service.tac:
            messagebox.showwarning("Warning", "Please run Phase 4 (IR) first.")
            return
        
        self.status_bar.config(text="Running Phase 5: Optimization...")
        self.root.update()
        
        result = self.phase_service.execute_phase_opt()
        
        if result['success']:
            # Format and display optimization log
            formatted = OptimizerFormatter.format(result['optimized_tac'], result['original_tac'])
            self.output_sections.set_content('optimizer', formatted, auto_expand=True)
            
            # Also show bytecode
            bytecode_formatted = BytecodeFormatter.format(result['optimized_tac'])
            self.output_sections.set_content('bytecode', bytecode_formatted, auto_expand=False)
            
            self.status_bar.config(text="✓ Phase 5 Complete: Optimization")
        else:
            # Show error
            self._show_errors(result.get('errors', []))
            self.status_bar.config(text="✗ Phase 5 Failed: Optimization")
    
    def _get_input_from_user(self):
        """Get input from user via dialog"""
        value = simpledialog.askstring("Input Required", "Enter a value:", parent=self.root)
        if value is None:
            return ""
        return value
    
    def run_phase_run(self):
        """Run Phase 6: Execution"""
        if not self.phase_service.optimized_tac:
            messagebox.showwarning("Warning", "Please run Phase 5 (OPT) first.")
            return
        
        self.status_bar.config(text="Running Phase 6: Execution...")
        self.root.update()
        
        result = self.phase_service.execute_phase_run(input_callback=self._get_input_from_user)
        
        # Display output
        output_text = result.get('output', '')
        if not result['success']:
            output_text += f"\n\nRuntime Error:\n{result.get('error', 'Unknown error')}"
        
        self.output_sections.set_content('output', output_text, auto_expand=True)
        
        if result['success']:
            self.status_bar.config(text="✓ Phase 6 Complete: Execution Successful")
        else:
            self._show_errors(result.get('errors', []))
            self.status_bar.config(text="✗ Phase 6 Failed: Runtime Error")
    
    def run_all_phases(self):
        """Run all phases sequentially"""
        source_code = self.editor.get_content()
        
        if not source_code.strip():
            messagebox.showwarning("Warning", "Please enter some code first.")
            return
        
        self.output_sections.clear_all()
        self.status_bar.config(text="Running all phases...")
        self.root.update()
        
        # Execute all phases
        results = self.phase_service.execute_all_phases(source_code, input_callback=self._get_input_from_user)
        
        # Display results for each phase
        if 'lex' in results and results['lex']['success']:
            formatted = TokensFormatter.format(results['lex']['tokens'])
            self.output_sections.set_content('tokens', formatted, auto_expand=False)
        
        if 'parse' in results and results['parse']['success']:
            formatted = ASTFormatter.format(results['parse']['ast'])
            self.output_sections.set_content('ast', formatted, auto_expand=False)
        
        if 'check' in results and results['check']['success']:
            formatted = SemanticFormatter.format(results['check']['semantic_info'])
            self.output_sections.set_content('semantic', formatted, auto_expand=False)
        
        if 'ir' in results and results['ir']['success']:
            formatted = IRFormatter.format(results['ir']['tac'])
            self.output_sections.set_content('ir', formatted, auto_expand=False)
        
        if 'opt' in results and results['opt']['success']:
            formatted = OptimizerFormatter.format(
                results['opt']['optimized_tac'],
                results['opt']['original_tac']
            )
            self.output_sections.set_content('optimizer', formatted, auto_expand=False)
            
            bytecode_formatted = BytecodeFormatter.format(results['opt']['optimized_tac'])
            self.output_sections.set_content('bytecode', bytecode_formatted, auto_expand=False)
        
        if 'run' in results:
            output_text = results['run'].get('output', '')
            if not results['run']['success']:
                output_text += f"\n\nRuntime Error:\n{results['run'].get('error', 'Unknown error')}"
            self.output_sections.set_content('output', output_text, auto_expand=True)
        
        # Show errors if any
        errors = self.phase_service.get_errors()
        if errors:
            self._show_errors(errors)
            self.status_bar.config(text="✗ Compilation Failed - Check errors")
        else:
            self.status_bar.config(text="✓ All Phases Complete - Program Executed Successfully")
    
    def _show_errors(self, errors):
        """Display errors in errors section"""
        formatted = ErrorsFormatter.format(errors)
        self.output_sections.set_content('errors', formatted, auto_expand=True)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = ModernCompilerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
