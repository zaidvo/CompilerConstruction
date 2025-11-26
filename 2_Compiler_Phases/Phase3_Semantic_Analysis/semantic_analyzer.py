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
    
    def define(self, name: str, symbol_type: str, value_type: str = None):
        """Define a new symbol in the current scope"""
        if name in self.symbols:
            raise NameError(f"Symbol '{name}' already defined in current scope")
        self.symbols[name] = {
            'type': symbol_type,  # 'variable' or 'function'
            'value_type': value_type,  # 'number', 'string', 'boolean', 'array'
            'scope_level': self.scope_level
        }
    
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
        self.errors: List[str] = []
        
        # No built-in functions - users must define everything themselves
    
    def error(self, message: str):
        """Record a semantic error"""
        self.errors.append(f"Semantic error: {message}")
    
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
            error_msg = "\n".join(self.errors)
            raise Exception(f"Semantic analysis failed:\n{error_msg}")
    
    def visit(self, node: ASTNode) -> str:
        """Visit a node and return its type"""
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node: ASTNode):
        """Default visitor for unhandled nodes"""
        raise Exception(f"No visit method for {node.__class__.__name__}")
    
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
            self.error(f"Variable '{node.name}' already declared in current scope")
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
        
        # Define variable in symbol table with declared type
        self.current_scope.define(node.name, 'variable', declared_type)
        return 'void'
    
    def visit_AssignmentNode(self, node: AssignmentNode) -> str:
        """Visit assignment"""
        # Check if variable exists
        if not self.current_scope.exists(node.name):
            self.error(f"Variable '{node.name}' not declared")
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
        """Visit print statement"""
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
        
        # Visit then block
        for stmt in node.then_block:
            self.visit(stmt)
        
        # Visit else block if present
        if node.else_block:
            for stmt in node.else_block:
                self.visit(stmt)
        return 'void'
    
    def visit_RepeatNode(self, node: RepeatNode) -> str:
        """Visit repeat loop"""
        # Check count type
        count_type = self.visit(node.count)
        if count_type not in ('number', 'unknown'):
            self.error(f"Repeat count must be a number, got {count_type}")
        
        # Visit body
        old_in_loop = self.in_loop
        self.in_loop = True
        for stmt in node.body:
            self.visit(stmt)
        self.in_loop = old_in_loop
        return 'void'
    
    def visit_WhileNode(self, node: WhileNode) -> str:
        """Visit while loop"""
        # Check condition type
        cond_type = self.visit(node.condition)
        if cond_type not in ('boolean', 'number', 'unknown'):
            self.error(f"While condition must be boolean, got {cond_type}")
        
        # Visit body
        old_in_loop = self.in_loop
        self.in_loop = True
        for stmt in node.body:
            self.visit(stmt)
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
            'matrix': 'array'
        }
        
        return_value_type = type_map.get(node.return_type, 'unknown')
        
        # Define function in global scope (before visiting body to allow recursion)
        self.global_scope.symbols[node.name] = {
            'type': 'function',
            'value_type': return_value_type,
            'return_type': node.return_type,
            'scope_level': 0
        }
        
        # Enter function scope
        self.enter_scope()
        old_in_function = self.in_function
        self.in_function = True
        
        # Define parameters with their types
        for param_type, param_name in node.parameters:
            param_value_type = type_map.get(param_type, 'number')
            self.current_scope.define(param_name, 'variable', param_value_type)
        
        # Visit body
        for stmt in node.body:
            self.visit(stmt)
        
        # Exit function scope
        self.in_function = old_in_function
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
            self.error(f"Variable '{node.name}' not declared")
            return 'unknown'
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
            self.error(f"Function '{node.name}' not defined")
            return 'number'  # Assume number to allow compilation to continue
        
        # Visit arguments
        for arg in node.arguments:
            self.visit(arg)
        
        # Return the function's value type
        return symbol.get('value_type', 'number')
