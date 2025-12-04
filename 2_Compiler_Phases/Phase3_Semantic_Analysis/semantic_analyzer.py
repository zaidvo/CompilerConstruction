# ============================================================================
# PHASE 3: SEMANTIC ANALYSIS
# ============================================================================
# This module implements semantic analysis for CalcScript+
# It performs type checking, scope resolution, and builds symbol tables

from typing import Dict, List, Optional, Any
from ast_nodes import *


class SymbolTable:
    """Symbol table for tracking variables and functions"""
    
    def __init__(self, parent: Optional['SymbolTable'] = None):
        self.symbols: Dict[str, Dict[str, Any]] = {}
        self.parent = parent
        self.scope_level = 0 if parent is None else parent.scope_level + 1
    
    def define(self, name: str, symbol_type: str, value_type: str = None, init_value=None, line_number=None):
        """Define a new symbol in the current scope"""
        if name in self.symbols:
            raise NameError(f"Symbol '{name}' already defined in current scope")
        self.symbols[name] = {
            'type': symbol_type,  # 'variable' or 'function'
            'value_type': value_type,  # 'number', 'string', 'boolean', 'array'
            'scope_level': self.scope_level,
            'init_value': init_value,  # Initial value or expression
            'line_number': line_number,  # Line where declared
            'is_initialized': init_value is not None,
            'is_used': False  # Track if variable is used
        }
    
    def mark_used(self, name: str):
        """Mark a symbol as used"""
        symbol = self.lookup(name)
        if symbol and name in self.symbols:
            self.symbols[name]['is_used'] = True
        elif symbol and self.parent:
            self.parent.mark_used(name)
    
    def lookup(self, name: str) -> Optional[Dict[str, Any]]:
        """Look up a symbol in current scope or parent scopes"""
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent:
            return self.parent.lookup(name)
        return None
    
    def exists(self, name: str) -> bool:
        """Check if symbol exists in any scope"""
        return self.lookup(name) is not None


class SemanticAnalyzer:
    """Semantic analyzer for CalcScript+"""
    
    def __init__(self):
        self.global_scope = SymbolTable()
        self.current_scope = self.global_scope
        self.in_function = False
        self.in_loop = False
        self.errors: List[Dict[str, Any]] = []  # Store structured error info
        self.all_symbols = []  # Track all symbols across all scopes
        self.current_node = None  # Track current node being analyzed
        self.current_function = None  # Track current function name
        
        # No built-in functions - users must define everything themselves
    
    def error(self, message: str, node: ASTNode = None, suggestion: str = None):
        """Record a semantic error with location information"""
        # Use provided node or current node
        error_node = node if node else self.current_node
        
        # Get line and column if available
        line = getattr(error_node, 'line', 0) if error_node else 0
        column = getattr(error_node, 'column', 0) if error_node else 0
        
        error_info = {
            'message': message,
            'line': line,
            'column': column,
            'suggestion': suggestion,
            'context': self._get_error_context()
        }
        self.errors.append(error_info)
    
    def _get_error_context(self) -> str:
        """Get context information for error message"""
        context_parts = []
        if self.current_function:
            context_parts.append(f"in function '{self.current_function}'")
        if self.in_loop:
            context_parts.append("in loop")
        return " ".join(context_parts) if context_parts else ""
    
    def enter_scope(self):
        """Enter a new scope"""
        self.current_scope = SymbolTable(self.current_scope)
    
    def exit_scope(self):
        """Exit current scope"""
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent
    
    def analyze(self, node: ASTNode):
        """Main analysis entry point"""
        self.visit(node)
        
        if self.errors:
            error_messages = []
            for i, err in enumerate(self.errors, 1):
                msg = f"Error {i}:"
                if err['line']:
                    msg += f" Line {err['line']}"
                    if err['column']:
                        msg += f", Column {err['column']}"
                msg += f"\n  {err['message']}"
                if err.get('context'):
                    msg += f" ({err['context']})"
                if err.get('suggestion'):
                    msg += f"\n  💡 Suggestion: {err['suggestion']}"
                error_messages.append(msg)
            
            full_error = "Semantic analysis failed:\n\n" + "\n\n".join(error_messages)
            raise Exception(full_error)
    
    def get_expr_string(self, node) -> str:
        """Convert expression node to readable string"""
        if node is None:
            return 'null'
        
        node_class = node.__class__.__name__
        
        if node_class == 'NumberNode':
            return str(node.value)
        elif node_class == 'StringNode':
            return f'"{node.value}"'
        elif node_class == 'BooleanNode':
            return str(node.value).lower()
        elif node_class == 'IdentifierNode':
            return node.name
        elif node_class == 'BinaryOpNode':
            left = self.get_expr_string(node.left)
            right = self.get_expr_string(node.right)
            return f"({left} {node.operator} {right})"
        elif node_class == 'UnaryOpNode':
            operand = self.get_expr_string(node.operand)
            return f"{node.operator}({operand})"
        elif node_class == 'ArrayLiteralNode':
            if hasattr(node, 'elements'):
                elements = [self.get_expr_string(e) for e in node.elements]
                return f"[{', '.join(elements)}]"
            return '[]'
        elif node_class == 'FunctionCallNode':
            args = [self.get_expr_string(a) for a in node.arguments]
            return f"{node.name}({', '.join(args)})"
        else:
            return f"<{node_class}>"
    
    def visit(self, node: ASTNode) -> str:
        """Visit a node and return its type"""
        # Track current node for better error reporting
        old_node = self.current_node
        self.current_node = node
        
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        result = visitor(node)
        
        self.current_node = old_node
        return result
    
    def generic_visit(self, node: ASTNode):
        """Default visitor for unhandled nodes"""
        raise Exception(f"No visit method for {node.__class__.__name__}")
    
    def _find_similar_name(self, wrong_name: str, candidates: List[str]) -> Optional[str]:
        """Find the most similar name from candidates using simple distance"""
        if not candidates:
            return None
        
        def levenshtein_distance(s1: str, s2: str) -> int:
            """Calculate edit distance between two strings"""
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            if len(s2) == 0:
                return len(s1)
            
            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        # Find candidate with minimum distance
        best_match = None
        min_distance = float('inf')
        
        for candidate in candidates:
            distance = levenshtein_distance(wrong_name.lower(), candidate.lower())
            if distance < min_distance and distance <= 3:  # Only suggest if distance <= 3
                min_distance = distance
                best_match = candidate
        
        return best_match
    
    # ========================================================================
    # STATEMENT VISITORS
    # ========================================================================
    
    def visit_ProgramNode(self, node: ProgramNode) -> str:
        """Visit program node"""
        for statement in node.statements:
            self.visit(statement)
        return 'void'
    
    def visit_VarDeclNode(self, node: VarDeclNode) -> str:
        """Visit variable declaration with type"""
        # Check if variable already exists in current scope
        if node.name in self.current_scope.symbols:
            prev_decl = self.current_scope.symbols[node.name]
            line_info = f" (previously declared at line {prev_decl.get('line_number')})" if prev_decl.get('line_number') else ""
            self.error(f"Variable '{node.name}' is already declared in this scope{line_info}", node, 
                      "Use a different variable name or remove the duplicate declaration.")
            return 'void'
        
        # Get type of initialization expression
        value_type = self.visit(node.value)
        
        # Map type keywords to value types
        type_map = {
            'int': 'number',
            'long': 'number',
            'float': 'number',
            'string': 'string',
            'boolean': 'boolean',
            'array': 'array',
            'matrix': 'array'
        }
        
        declared_type = type_map.get(node.var_type, 'unknown')
        
        # Type checking: ensure value matches declared type
        if declared_type != 'unknown' and value_type != 'unknown':
            if declared_type != value_type and not (declared_type == 'number' and value_type == 'number'):
                self.error(f"Type mismatch: variable '{node.name}' declared as {node.var_type} but assigned {value_type}")
        
        # Get initialization expression as string
        init_expr = self.get_expr_string(node.value)
        
        # Get line number if available
        line_num = getattr(node, 'line', None)
        
        # Define variable in symbol table with comprehensive info
        self.current_scope.define(node.name, 'variable', declared_type, init_expr, line_num)
        
        # Track this symbol in all_symbols list
        self.all_symbols.append((node.name, {
            'type': 'variable',
            'value_type': declared_type,
            'scope_level': self.current_scope.scope_level,
            'init_value': init_expr,
            'line_number': line_num,
            'is_initialized': True,
            'is_used': False
        }))
        
        return 'void'
    
    def visit_AssignmentNode(self, node: AssignmentNode) -> str:
        """Visit assignment"""
        # Check if variable exists
        if not self.current_scope.exists(node.name):
            # Find similar variable names for suggestions
            all_vars = [name for name, info in self.all_symbols if info.get('type') == 'variable']
            suggestion = self._find_similar_name(node.name, all_vars)
            suggestion_msg = f"Did you mean '{suggestion}'?" if suggestion else "Declare the variable before assigning to it."
            
            self.error(f"Variable '{node.name}' is not declared", node, suggestion_msg)
            return 'void'
        
        # For array assignment, check index
        if node.index:
            index_type = self.visit(node.index)
            if index_type != 'number':
                self.error(f"Array index must be a number, got {index_type}")
        
        # Check value type
        self.visit(node.value)
        return 'void'
    
    def visit_PrintNode(self, node: PrintNode) -> str:
        """Visit print statement - supports single or multiple expressions"""
        # Handle both single expression and list of expressions
        if isinstance(node.expression, list):
            for expr in node.expression:
                self.visit(expr)
        else:
            self.visit(node.expression)
        return 'void'
    
    def visit_InputNode(self, node: InputNode) -> str:
        """Visit input statement"""
        # Define variable if it doesn't exist
        if not self.current_scope.exists(node.name):
            self.current_scope.define(node.name, 'variable', 'string')
        return 'void'
    
    def visit_IfNode(self, node: IfNode) -> str:
        """Visit if statement"""
        # Check condition type
        cond_type = self.visit(node.condition)
        if cond_type not in ('boolean', 'number', 'unknown'):  # Allow numbers for truthiness
            self.error(f"If condition must be boolean, got {cond_type}")
        
        # Visit then block in new scope
        self.enter_scope()
        for stmt in node.then_block:
            self.visit(stmt)
        self.exit_scope()
        
        # Visit else block if present in new scope
        if node.else_block:
            self.enter_scope()
            for stmt in node.else_block:
                self.visit(stmt)
            self.exit_scope()
        return 'void'
    
    def visit_RepeatNode(self, node: RepeatNode) -> str:
        """Visit repeat loop"""
        # Check count type
        count_type = self.visit(node.count)
        if count_type not in ('number', 'unknown'):
            self.error(f"Repeat count must be a number, got {count_type}")
        
        # Visit body in new scope
        old_in_loop = self.in_loop
        self.in_loop = True
        self.enter_scope()
        for stmt in node.body:
            self.visit(stmt)
        self.exit_scope()
        self.in_loop = old_in_loop
        return 'void'
    
    def visit_WhileNode(self, node: WhileNode) -> str:
        """Visit while loop"""
        # Check condition type
        cond_type = self.visit(node.condition)
        if cond_type not in ('boolean', 'number', 'unknown'):
            self.error(f"While condition must be boolean, got {cond_type}")
        
        # Visit body in new scope
        old_in_loop = self.in_loop
        self.in_loop = True
        self.enter_scope()
        for stmt in node.body:
            self.visit(stmt)
        self.exit_scope()
        self.in_loop = old_in_loop
        return 'void'
    
    def visit_ForNode(self, node: ForNode) -> str:
        """Visit for loop: for int i = 0; i < 10; i = i + 1: ... end"""
        # Enter new scope BEFORE initialization so loop variable is scoped to the loop
        old_in_loop = self.in_loop
        self.in_loop = True
        self.enter_scope()
        
        # Visit initialization (now in loop scope)
        self.visit(node.init)
        
        # Check condition type
        cond_type = self.visit(node.condition)
        if cond_type not in ('boolean', 'number', 'unknown'):
            self.error(f"For loop condition must be boolean, got {cond_type}")
        
        # Visit update statement
        self.visit(node.update)
        
        # Visit body (already in loop scope)
        for stmt in node.body:
            self.visit(stmt)
        
        # Exit scope
        self.exit_scope()
        self.in_loop = old_in_loop
        return 'void'
    
    def visit_FuncDefNode(self, node: FuncDefNode) -> str:
        """Visit function definition with return type and typed parameters"""
        # Check if function already exists (but allow if it's a built-in being redefined)
        existing = self.global_scope.symbols.get(node.name)
        if existing and existing['type'] == 'function' and node.name not in ('sum', 'max', 'min'):
            self.error(f"Function '{node.name}' already defined")
            return 'void'
        
        # Map return type to value type
        type_map = {
            'int': 'number',
            'long': 'number',
            'float': 'number',
            'string': 'string',
            'boolean': 'boolean',
            'array': 'array',
            'matrix': 'array',
            'void': 'void'
        }
        
        return_value_type = type_map.get(node.return_type, 'unknown')
        
        # Get line number if available
        line_num = getattr(node, 'line', None)
        
        # Define function in global scope (before visiting body to allow recursion)
        self.global_scope.symbols[node.name] = {
            'type': 'function',
            'value_type': return_value_type,
            'return_type': node.return_type,
            'scope_level': 0,
            'line_number': line_num
        }
        
        # Track this function in all_symbols list
        self.all_symbols.append((node.name, {
            'type': 'function',
            'value_type': return_value_type,
            'return_type': node.return_type,
            'scope_level': 0,
            'line_number': line_num,
            'is_initialized': True,
            'is_used': False
        }))
        
        # Enter function scope
        self.enter_scope()
        old_in_function = self.in_function
        old_function_name = self.current_function
        self.in_function = True
        self.current_function = node.name
        
        # Define parameters with their types
        for param_type, param_name in node.parameters:
            param_value_type = type_map.get(param_type, 'number')
            param_line = getattr(node, 'line', None)
            self.current_scope.define(param_name, 'variable', param_value_type)
            
            # Track parameters in all_symbols
            self.all_symbols.append((param_name, {
                'type': 'parameter',
                'value_type': param_value_type,
                'scope_level': self.current_scope.scope_level,
                'init_value': f'<param>',
                'line_number': param_line,
                'is_initialized': True,
                'is_used': False
            }))
        
        # Visit body
        for stmt in node.body:
            self.visit(stmt)
        
        # Exit function scope
        self.in_function = old_in_function
        self.current_function = old_function_name
        self.exit_scope()
        return 'void'
    
    def visit_ReturnNode(self, node: ReturnNode) -> str:
        """Visit return statement"""
        if not self.in_function:
            self.error("Return statement outside function")
        
        self.visit(node.value)
        return 'void'
    
    def visit_BreakNode(self, node: BreakNode) -> str:
        """Visit break statement"""
        if not self.in_loop:
            self.error("Break statement outside loop")
        return 'void'
    
    def visit_ContinueNode(self, node: ContinueNode) -> str:
        """Visit continue statement"""
        if not self.in_loop:
            self.error("Continue statement outside loop")
        return 'void'
    
    # ========================================================================
    # EXPRESSION VISITORS
    # ========================================================================
    
    def visit_BinaryOpNode(self, node: BinaryOpNode) -> str:
        """Visit binary operation"""
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        
        # Handle None types (shouldn't happen but be defensive)
        if left_type is None:
            left_type = 'unknown'
        if right_type is None:
            right_type = 'unknown'
        
        # Arithmetic operators
        if node.operator in ('+', '-', '*', '/', '%', '^'):
            if node.operator == '+' and left_type == 'string' and right_type == 'string':
                return 'string'  # String concatenation
            # Allow matrix operations with +, -, *
            if node.operator in ('+', '-', '*') and left_type == 'array' and right_type == 'array':
                return 'array'  # Matrix operations
            # Allow matrix transpose (^t) and inverse (^-1)
            if node.operator == '^' and left_type == 'array':
                if right_type in ('string', 'number', 'unknown'):  # ^t or ^-1
                    return 'array'
            # Allow unknown types (from function calls) to pass through
            if left_type in ('number', 'unknown') and right_type in ('number', 'unknown'):
                return 'number'
            if left_type == 'number' and right_type == 'number':
                return 'number'
            self.error(f"Invalid operands for {node.operator}: {left_type} and {right_type}")
            return 'number'
        
        # Comparison operators
        elif node.operator in ('>', '<', '>=', '<='):
            # Allow unknown types (from function calls, complex expressions) to pass through
            if left_type in ('number', 'unknown') and right_type in ('number', 'unknown'):
                return 'boolean'
            self.error(f"Invalid operands for {node.operator}: {left_type} and {right_type}")
            return 'boolean'
        
        # Equality operators
        elif node.operator in ('==', '!='):
            return 'boolean'
        
        # Logical operators
        elif node.operator in ('and', 'or'):
            # Allow unknown types to pass through (they might be boolean from complex expressions)
            if left_type in ('boolean', 'unknown') and right_type in ('boolean', 'unknown'):
                return 'boolean'
            self.error(f"Invalid operands for {node.operator}: {left_type} and {right_type}")
            return 'boolean'
        
        return 'unknown'
    
    def visit_UnaryOpNode(self, node: UnaryOpNode) -> str:
        """Visit unary operation"""
        operand_type = self.visit(node.operand)
        
        if node.operator == '-':
            if operand_type == 'number':
                return 'number'
            self.error(f"Invalid operand for unary -: {operand_type}")
            return 'number'
        
        elif node.operator == 'not':
            if operand_type == 'boolean':
                return 'boolean'
            self.error(f"Invalid operand for not: {operand_type}")
            return 'boolean'
        
        return 'unknown'
    
    def visit_LiteralNode(self, node: LiteralNode) -> str:
        """Visit literal"""
        if isinstance(node.value, bool):
            return 'boolean'
        elif isinstance(node.value, (int, float)):
            return 'number'
        elif isinstance(node.value, str):
            return 'string'
        return 'unknown'
    
    def visit_IdentifierNode(self, node: IdentifierNode) -> str:
        """Visit identifier"""
        symbol = self.current_scope.lookup(node.name)
        if not symbol:
            # Find similar variable names for suggestions
            all_vars = [name for name, info in self.all_symbols if info.get('type') == 'variable']
            suggestion = self._find_similar_name(node.name, all_vars)
            suggestion_msg = f"Did you mean '{suggestion}'?" if suggestion else "Make sure to declare the variable before using it."
            
            self.error(f"Variable '{node.name}' is not declared", node, suggestion_msg)
            return 'unknown'
        
        # Mark variable as used in symbol table
        self.current_scope.mark_used(node.name)
        
        # Mark variable as used in all_symbols list
        for i, (name, info) in enumerate(self.all_symbols):
            if name == node.name:
                info['is_used'] = True
        
        return symbol.get('value_type', 'unknown')
    
    def visit_ArrayLiteralNode(self, node: ArrayLiteralNode) -> str:
        """Visit array literal"""
        for element in node.elements:
            self.visit(element)
        return 'array'
    
    def visit_ArrayAccessNode(self, node: ArrayAccessNode) -> str:
        """Visit array access"""
        # Check if array exists
        if not self.current_scope.exists(node.name):
            self.error(f"Array '{node.name}' not declared")
        
        # Check index type
        index_type = self.visit(node.index)
        if index_type != 'number':
            self.error(f"Array index must be a number, got {index_type}")
        
        return 'unknown'  # We don't track element types
    
    def visit_FuncCallNode(self, node: FuncCallNode) -> str:
        """Visit function call"""
        # Check if function exists
        symbol = self.global_scope.lookup(node.name)
        if not symbol or symbol['type'] != 'function':
            # Find similar function names for suggestions
            all_funcs = [name for name, info in self.all_symbols if info.get('type') == 'function']
            suggestion = self._find_similar_name(node.name, all_funcs)
            suggestion_msg = f"Did you mean '{suggestion}'?" if suggestion else "Make sure to define the function before calling it."
            
            self.error(f"Function '{node.name}' is not defined", node, suggestion_msg)
            return 'number'  # Assume number to allow compilation to continue
        
        # Mark function as used in all_symbols list
        for i, (name, info) in enumerate(self.all_symbols):
            if name == node.name and info.get('type') == 'function':
                info['is_used'] = True
                break
        
        # Visit arguments
        for arg in node.arguments:
            self.visit(arg)
        
        # Return the function's value type
        return symbol.get('value_type', 'number')
