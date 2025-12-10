"""
Phase Execution Service
Handles individual phase execution and results
"""
import sys
import io
from pathlib import Path

# Add compiler phases to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'Compiler' / 'Phase1_Lexical_Analysis'))
sys.path.insert(0, str(project_root / 'Compiler' / 'Phase2_Syntax_Analysis'))
sys.path.insert(0, str(project_root / 'Compiler' / 'Phase3_Semantic_Analysis'))
sys.path.insert(0, str(project_root / 'Compiler' / 'Phase4_Intermediate_Code'))
sys.path.insert(0, str(project_root / 'Compiler' / 'Phase5_Optimization'))
sys.path.insert(0, str(project_root / 'Compiler' / 'Phase6_Code_Generation'))

from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from ir_generator import IRGenerator
from optimizer import Optimizer
from interpreter import Interpreter


class PhaseExecutionService:
    """Service for executing compiler phases individually or all at once"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all compilation results"""
        self.source_code = ""
        self.tokens = None
        self.ast = None
        self.semantic_info = None
        self.tac = None
        self.optimized_tac = None
        self.bytecode = None
        self.errors = []
        self.phase_logs = {
            'lex': None,
            'parse': None,
            'check': None,
            'ir': None,
            'opt': None,
            'run': None
        }
    
    def _extract_line_col(self, error_msg):
        """Extract line and column numbers from error message"""
        import re
        # Try to find "line X, column Y" pattern
        match = re.search(r'line (\d+),?\s*column (\d+)', error_msg, re.IGNORECASE)
        if match:
            return int(match.group(1)), int(match.group(2))
        
        # Try to find "Line X" pattern
        match = re.search(r'line (\d+)', error_msg, re.IGNORECASE)
        if match:
            return int(match.group(1)), 0
        
        return 0, 0
    
    def _clean_error_message(self, error_msg):
        """Clean up error message to remove redundant info"""
        import re
        # Remove "Syntax error at line X, column Y: " prefix if present
        cleaned = re.sub(r'^(Syntax|Semantic|Lexical)\s+error\s+at\s+line\s+\d+,?\s*column\s+\d+:\s*', '', error_msg, flags=re.IGNORECASE)
        # Remove "Semantic analysis failed:" prefix if present
        cleaned = re.sub(r'^Semantic analysis failed:\s*', '', cleaned, flags=re.IGNORECASE)
        return cleaned.strip()
    
    def execute_phase_lex(self, source_code):
        """Phase 1: Lexical Analysis"""
        self.source_code = source_code
        self.errors = []
        
        try:
            lexer = Lexer(source_code)
            self.tokens = lexer.tokenize()
            self.phase_logs['lex'] = f"Lexical analysis complete. {len([t for t in self.tokens if t.type.name != 'EOF'])} tokens generated."
            return {
                'success': True,
                'tokens': self.tokens,
                'log': self.phase_logs['lex']
            }
        except Exception as e:
            error_msg = str(e)
            line, column = self._extract_line_col(error_msg)
            self.errors.append({
                'phase': 'Lexical',
                'type': 'Error',
                'message': self._clean_error_message(error_msg),
                'line': line,
                'column': column
            })
            return {
                'success': False,
                'error': error_msg,
                'errors': self.errors
            }
    
    def execute_phase_parse(self):
        """Phase 2: Syntax Analysis"""
        if not self.tokens:
            return {'success': False, 'error': 'No tokens available. Run Phase 1 first.'}
        
        try:
            parser = Parser(self.tokens)
            self.ast = parser.parse()
            self.phase_logs['parse'] = f"Syntax analysis complete. AST generated with root type: {type(self.ast).__name__}"
            return {
                'success': True,
                'ast': self.ast,
                'log': self.phase_logs['parse']
            }
        except Exception as e:
            error_msg = str(e)
            line, column = self._extract_line_col(error_msg)
            self.errors.append({
                'phase': 'Syntax',
                'type': 'Error',
                'message': self._clean_error_message(error_msg),
                'line': line,
                'column': column
            })
            return {
                'success': False,
                'error': error_msg,
                'errors': self.errors
            }
    
    def execute_phase_check(self):
        """Phase 3: Semantic Analysis"""
        if not self.ast:
            return {'success': False, 'error': 'No AST available. Run Phase 2 first.'}
        
        try:
            analyzer = SemanticAnalyzer()
            analyzer.analyze(self.ast)
            self.semantic_info = {
                'symbols': analyzer.all_symbols if hasattr(analyzer, 'all_symbols') else [],
                'errors': analyzer.errors if hasattr(analyzer, 'errors') else []
            }
            
            self.phase_logs['check'] = f"Semantic analysis complete. {len(self.semantic_info['symbols'])} symbols analyzed."
            return {
                'success': True,
                'semantic_info': self.semantic_info,
                'log': self.phase_logs['check']
            }
        except Exception as e:
            error_msg = str(e)
            
            # Try to extract structured errors from semantic analyzer
            try:
                import re
                # Parse the formatted error message
                error_blocks = error_msg.split('\n\n')
                for block in error_blocks:
                    if not block.strip() or 'Semantic analysis failed' in block:
                        continue
                    
                    # Extract error details
                    line_match = re.search(r'Line (\d+)', block)
                    col_match = re.search(r'Column (\d+)', block)
                    msg_match = re.search(r'\n  ([^\n]+?)(?:\n|$)', block)
                    suggestion_match = re.search(r'💡 Suggestion: ([^\n]+)', block)
                    
                    message = msg_match.group(1) if msg_match else block.strip()
                    line = int(line_match.group(1)) if line_match else 0
                    column = int(col_match.group(1)) if col_match else 0
                    
                    # Format message with suggestion if available
                    if suggestion_match:
                        message += f" (Suggestion: {suggestion_match.group(1)})"
                    
                    self.errors.append({
                        'phase': 'Semantic',
                        'type': 'Error',
                        'message': message,
                        'line': line,
                        'column': column
                    })
            except:
                # Fallback: add the whole error message
                line, column = self._extract_line_col(error_msg)
                self.errors.append({
                    'phase': 'Semantic',
                    'type': 'Error',
                    'message': self._clean_error_message(error_msg),
                    'line': line,
                    'column': column
                })
            
            return {
                'success': False,
                'error': error_msg,
                'errors': self.errors
            }
    
    def execute_phase_ir(self):
        """Phase 4: Intermediate Code Generation"""
        if not self.ast:
            return {'success': False, 'error': 'No AST available. Run Phase 3 first.'}
        
        try:
            ir_gen = IRGenerator()
            self.tac = ir_gen.generate(self.ast)
            self.phase_logs['ir'] = f"IR generation complete. {len(self.tac) if self.tac else 0} TAC instructions generated."
            return {
                'success': True,
                'tac': self.tac,
                'log': self.phase_logs['ir']
            }
        except Exception as e:
            error_msg = str(e)
            line, column = self._extract_line_col(error_msg)
            self.errors.append({
                'phase': 'IR Generation',
                'type': 'Error',
                'message': self._clean_error_message(error_msg),
                'line': line,
                'column': column
            })
            return {
                'success': False,
                'error': error_msg,
                'errors': self.errors
            }
    
    def execute_phase_opt(self):
        """Phase 5: Optimization"""
        if not self.tac:
            return {'success': False, 'error': 'No TAC available. Run Phase 4 first.'}
        
        try:
            optimizer = Optimizer()
            self.optimized_tac = optimizer.optimize(self.tac)
            
            original_count = len(self.tac) if self.tac else 0
            optimized_count = len(self.optimized_tac) if self.optimized_tac else 0
            saved = original_count - optimized_count
            
            self.phase_logs['opt'] = f"Optimization complete. {saved} instructions eliminated."
            return {
                'success': True,
                'optimized_tac': self.optimized_tac,
                'original_tac': self.tac,
                'log': self.phase_logs['opt']
            }
        except Exception as e:
            error_msg = str(e)
            line, column = self._extract_line_col(error_msg)
            self.errors.append({
                'phase': 'Optimization',
                'type': 'Error',
                'message': self._clean_error_message(error_msg),
                'line': line,
                'column': column
            })
            return {
                'success': False,
                'error': error_msg,
                'errors': self.errors
            }
    
    def execute_phase_run(self, input_callback=None):
        """Phase 6: Code Execution"""
        if not self.optimized_tac:
            return {'success': False, 'error': 'No optimized code available. Run Phase 5 first.'}
        
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        try:
            interpreter = Interpreter(input_callback=input_callback)
            interpreter.execute(self.optimized_tac)
            output = sys.stdout.getvalue()
            
            self.phase_logs['run'] = f"Execution complete. Program ran successfully."
            return {
                'success': True,
                'output': output,
                'log': self.phase_logs['run']
            }
        except Exception as e:
            error_msg = str(e)
            line, column = self._extract_line_col(error_msg)
            self.errors.append({
                'phase': 'Execution',
                'type': 'Runtime Error',
                'message': self._clean_error_message(error_msg),
                'line': line,
                'column': column
            })
            return {
                'success': False,
                'error': error_msg,
                'output': sys.stdout.getvalue(),
                'errors': self.errors
            }
        finally:
            sys.stdout = old_stdout
    
    def execute_all_phases(self, source_code, input_callback=None):
        """Execute all phases sequentially"""
        results = {}
        
        # Phase 1: Lex
        result = self.execute_phase_lex(source_code)
        results['lex'] = result
        if not result['success']:
            return results
        
        # Phase 2: Parse
        result = self.execute_phase_parse()
        results['parse'] = result
        if not result['success']:
            return results
        
        # Phase 3: Semantic Check
        result = self.execute_phase_check()
        results['check'] = result
        if not result['success']:
            return results
        
        # Phase 4: IR Generation
        result = self.execute_phase_ir()
        results['ir'] = result
        if not result['success']:
            return results
        
        # Phase 5: Optimization
        result = self.execute_phase_opt()
        results['opt'] = result
        if not result['success']:
            return results
        
        # Phase 6: Execution
        result = self.execute_phase_run(input_callback=input_callback)
        results['run'] = result
        
        return results
    
    def get_errors(self):
        """Get all accumulated errors"""
        return self.errors
