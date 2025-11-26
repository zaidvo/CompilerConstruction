#!/usr/bin/env python3
# ============================================================================
# CALCSCRIPT+ COMPILER - MAIN ENTRY POINT
# ============================================================================
# This is the main driver program that orchestrates all compiler phases

import sys
import argparse
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / '2_Compiler_Phases' / 'Phase1_Lexical_Analysis'))
sys.path.insert(0, str(Path(__file__).parent.parent / '2_Compiler_Phases' / 'Phase2_Syntax_Analysis'))
sys.path.insert(0, str(Path(__file__).parent.parent / '2_Compiler_Phases' / 'Phase3_Semantic_Analysis'))
sys.path.insert(0, str(Path(__file__).parent.parent / '2_Compiler_Phases' / 'Phase4_Intermediate_Code'))
sys.path.insert(0, str(Path(__file__).parent.parent / '2_Compiler_Phases' / 'Phase5_Optimization'))
sys.path.insert(0, str(Path(__file__).parent.parent / '2_Compiler_Phases' / 'Phase6_Code_Generation'))

from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from ir_generator import IRGenerator
from optimizer import Optimizer
from interpreter import Interpreter


class CalcScriptCompiler:
    """Main compiler class that orchestrates all phases"""
    
    def __init__(self, source_code: str, options: dict = None):
        self.source_code = source_code
        self.options = options or {}
        
        # Compilation artifacts
        self.tokens = None
        self.ast = None
        self.tac = None
        self.optimized_tac = None
    
    def compile_and_run(self):
        """Execute all compiler phases and run the program"""
        try:
            # Phase 1: Lexical Analysis
            if self.options.get('verbose'):
                print("=" * 70)
                print("PHASE 1: LEXICAL ANALYSIS")
                print("=" * 70)
            
            lexer = Lexer(self.source_code)
            self.tokens = lexer.tokenize()
            
            if self.options.get('show_tokens'):
                print("\nTokens:")
                for token in self.tokens:
                    if token.type.name != 'EOF':
                        print(f"  {token}")
                print()
            
            # Phase 2: Syntax Analysis
            if self.options.get('verbose'):
                print("=" * 70)
                print("PHASE 2: SYNTAX ANALYSIS")
                print("=" * 70)
            
            parser = Parser(self.tokens)
            self.ast = parser.parse()
            
            if self.options.get('show_ast'):
                print("\nAbstract Syntax Tree:")
                self.print_ast(self.ast)
                print()
            
            # Phase 3: Semantic Analysis
            if self.options.get('verbose'):
                print("=" * 70)
                print("PHASE 3: SEMANTIC ANALYSIS")
                print("=" * 70)
            
            analyzer = SemanticAnalyzer()
            analyzer.analyze(self.ast)
            
            if self.options.get('verbose'):
                print("[OK] Semantic analysis passed")
                print()
            
            # Phase 4: Intermediate Code Generation
            if self.options.get('verbose'):
                print("=" * 70)
                print("PHASE 4: INTERMEDIATE CODE GENERATION")
                print("=" * 70)
            
            ir_gen = IRGenerator()
            self.tac = ir_gen.generate(self.ast)
            
            if self.options.get('show_tac'):
                print("\nThree-Address Code (Before Optimization):")
                for i, instr in enumerate(self.tac):
                    print(f"  {i:3d}: {instr}")
                print()
            
            # Phase 5: Optimization
            if self.options.get('verbose'):
                print("=" * 70)
                print("PHASE 5: OPTIMIZATION")
                print("=" * 70)
            
            optimizer = Optimizer()
            self.optimized_tac = optimizer.optimize(self.tac)
            
            if self.options.get('show_optimized') or self.options.get('verbose'):
                print("\nThree-Address Code (After Optimization):")
                for i, instr in enumerate(self.optimized_tac):
                    print(f"  {i:3d}: {instr}")
                print()
                
                if optimizer.optimizations_applied:
                    print(f"Optimizations applied: {len(optimizer.optimizations_applied)}")
                    if self.options.get('verbose'):
                        for opt in optimizer.optimizations_applied[:10]:  # Show first 10
                            print(f"  - {opt}")
                        if len(optimizer.optimizations_applied) > 10:
                            print(f"  ... and {len(optimizer.optimizations_applied) - 10} more")
                print()
            
            # Phase 6: Execution
            if self.options.get('verbose'):
                print("=" * 70)
                print("PHASE 6: EXECUTION")
                print("=" * 70)
                print()
            
            if not self.options.get('no_execute'):
                interpreter = Interpreter()
                interpreter.execute(self.optimized_tac)
            
            if self.options.get('verbose'):
                print("\n" + "=" * 70)
                print("COMPILATION SUCCESSFUL")
                print("=" * 70)
        
        except SyntaxError as e:
            print(f"\n❌ Syntax Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Error: {e}", file=sys.stderr)
            if self.options.get('verbose'):
                import traceback
                traceback.print_exc()
            sys.exit(1)
    
    def print_ast(self, node, indent=0):
        """Pretty print the AST"""
        prefix = "  " * indent
        node_name = node.__class__.__name__
        print(f"{prefix}{node_name}")
        
        # Print node attributes
        if hasattr(node, '__dict__'):
            for key, value in node.__dict__.items():
                if isinstance(value, list):
                    if value and isinstance(value[0], (ASTNode, type(node))):
                        print(f"{prefix}  {key}:")
                        for item in value:
                            self.print_ast(item, indent + 2)
                    else:
                        print(f"{prefix}  {key}: {value}")
                elif hasattr(value, '__class__') and hasattr(value.__class__, '__name__'):
                    if 'Node' in value.__class__.__name__:
                        print(f"{prefix}  {key}:")
                        self.print_ast(value, indent + 2)
                    else:
                        print(f"{prefix}  {key}: {value}")
                else:
                    print(f"{prefix}  {key}: {value}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='CalcScript+ Compiler - A compiler for the CalcScript+ language',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py program.calc                    # Compile and run
  python main.py program.calc --show-tokens      # Show tokens
  python main.py program.calc --show-ast         # Show AST
  python main.py program.calc --show-tac         # Show TAC
  python main.py program.calc --show-optimized   # Show optimized TAC
  python main.py program.calc --verbose          # Show all phases
        """
    )
    
    parser.add_argument('file', help='CalcScript+ source file')
    parser.add_argument('--show-tokens', action='store_true', help='Display tokens')
    parser.add_argument('--show-ast', action='store_true', help='Display AST')
    parser.add_argument('--show-tac', action='store_true', help='Display TAC before optimization')
    parser.add_argument('--show-optimized', action='store_true', help='Display optimized TAC')
    parser.add_argument('--no-execute', action='store_true', help='Compile only, do not execute')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output (show all phases)')
    
    args = parser.parse_args()
    
    # Read source file
    try:
        source_path = Path(args.file)
        if not source_path.exists():
            print(f"Error: File '{args.file}' not found", file=sys.stderr)
            sys.exit(1)
        
        source_code = source_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Compile and run
    options = {
        'show_tokens': args.show_tokens,
        'show_ast': args.show_ast,
        'show_tac': args.show_tac,
        'show_optimized': args.show_optimized,
        'no_execute': args.no_execute,
        'verbose': args.verbose,
    }
    
    compiler = CalcScriptCompiler(source_code, options)
    compiler.compile_and_run()


if __name__ == '__main__':
    main()
