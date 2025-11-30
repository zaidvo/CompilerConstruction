"""
Compiler Service
Handles compilation and execution logic
"""
from typing import List, Optional
import sys
import io


class CompilerService:
    """Service for compiling and executing CalcScript++ code"""
    
    def __init__(self, lexer_class, parser_class, semantic_analyzer_class,
                 ir_generator_class, optimizer_class, interpreter_class):
        self.Lexer = lexer_class
        self.Parser = parser_class
        self.SemanticAnalyzer = semantic_analyzer_class
        self.IRGenerator = ir_generator_class
        self.Optimizer = optimizer_class
        self.Interpreter = interpreter_class
        
        # Compilation results
        self.tokens = None
        self.ast = None
        self.tac = None
        self.optimized_tac = None
        self.analyzer = None
    
    def compile(self, source_code: str) -> dict:
        """
        Compile source code through all phases
        
        Returns:
            dict with keys: tokens, ast, semantic_info, tac, optimized_tac, errors
        """
        results = {
            'tokens': None,
            'ast': None,
            'semantic_info': None,
            'tac': None,
            'optimized_tac': None,
            'errors': None
        }
        
        try:
            # Phase 1: Lexical Analysis
            lexer = self.Lexer(source_code)
            self.tokens = lexer.tokenize()
            results['tokens'] = self.tokens
            
            # Phase 2: Syntax Analysis
            parser = self.Parser(self.tokens)
            self.ast = parser.parse()
            results['ast'] = self.ast
            
            # Phase 3: Semantic Analysis
            self.analyzer = self.SemanticAnalyzer()
            self.analyzer.analyze(self.ast)
            results['semantic_info'] = {
                'symbols': self.analyzer.all_symbols,
                'errors': self.analyzer.errors
            }
            
            # Phase 4: IR Generation
            ir_gen = self.IRGenerator()
            self.tac = ir_gen.generate(self.ast)
            results['tac'] = self.tac
            
            # Phase 5: Optimization
            optimizer = self.Optimizer()
            self.optimized_tac = optimizer.optimize(self.tac)
            results['optimized_tac'] = self.optimized_tac
            
        except Exception as e:
            results['errors'] = str(e)
        
        return results
    
    def execute(self) -> str:
        """
        Execute compiled code
        
        Returns:
            Program output as string
        """
        if not self.optimized_tac:
            return "Error: No compiled code to execute"
        
        # Redirect stdout to capture output
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        try:
            interpreter = self.Interpreter()
            interpreter.execute(self.optimized_tac)
            output = sys.stdout.getvalue()
            return output
        except Exception as e:
            return f"Runtime Error: {str(e)}"
        finally:
            sys.stdout = old_stdout
    
    def get_tokens(self):
        """Get tokens from last compilation"""
        return self.tokens
    
    def get_ast(self):
        """Get AST from last compilation"""
        return self.ast
    
    def get_tac(self):
        """Get TAC from last compilation"""
        return self.tac
    
    def get_optimized_tac(self):
        """Get optimized TAC from last compilation"""
        return self.optimized_tac
    
    def get_semantic_info(self):
        """Get semantic analysis information"""
        if self.analyzer:
            return self.analyzer.all_symbols
        return []
