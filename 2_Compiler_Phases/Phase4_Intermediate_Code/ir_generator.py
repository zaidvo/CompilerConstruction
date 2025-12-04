# ============================================================================
# PHASE 4: INTERMEDIATE CODE GENERATION
# ============================================================================
# This module generates Three-Address Code (TAC) from the AST

from typing import List, Optional
from dataclasses import dataclass
from ast_nodes import *


@dataclass
class TACInstruction:
    """Represents a single TAC instruction"""
    op: str  # Operation: assign, add, sub, mul, div, etc.
    arg1: Optional[str] = None
    arg2: Optional[str] = None
    result: Optional[str] = None
    
    def __str__(self):
        if self.op == 'label':
            return f"{self.result}:"
        elif self.op == 'goto':
            return f"goto {self.result}"
        elif self.op == 'if_false':
            return f"if_false {self.arg1} goto {self.result}"
        elif self.op == 'if_true':
            return f"if_true {self.arg1} goto {self.result}"
        elif self.op == 'param':
            return f"param {self.arg1}"
        elif self.op == 'call':
            if self.result:
                return f"{self.result} = call {self.arg1}, {self.arg2}"
            return f"call {self.arg1}, {self.arg2}"
        elif self.op == 'return':
            return f"return {self.arg1}"
        elif self.op == 'print':
            return f"print {self.arg1}"
        elif self.op == 'input':
            return f"input {self.result}"
        elif self.op == 'array_store':
            return f"{self.result}[{self.arg1}] = {self.arg2}"
        elif self.op == 'array_load':
            return f"{self.result} = {self.arg1}[{self.arg2}]"
        elif self.op == 'array_literal':
            return f"{self.result} = [{self.arg1}]"
        elif self.op in ('assign', '='):
            return f"{self.result} = {self.arg1}"
        elif self.arg2:
            return f"{self.result} = {self.arg1} {self.op} {self.arg2}"
        else:
            return f"{self.result} = {self.op} {self.arg1}"


class IRGenerator:
    """Generates Three-Address Code from AST"""
    
    def __init__(self):
        self.instructions: List[TACInstruction] = []
        self.temp_counter = 0
        self.label_counter = 0
        self.loop_stack = []  # Stack of (continue_label, break_label) tuples
        self.scope_depth = 0  # Track scope depth for variable naming
        self.var_scopes = [{}]  # Stack of scopes, each is a dict mapping var_name to scoped_name
    
    def new_temp(self) -> str:
        """Generate a new temporary variable"""
        self.temp_counter += 1
        return f"t{self.temp_counter}"
    
    def new_label(self) -> str:
        """Generate a new label"""
        self.label_counter += 1
        return f"L{self.label_counter}"
    
    def emit(self, op: str, arg1=None, arg2=None, result=None):
        """Emit a TAC instruction"""
        instr = TACInstruction(op, arg1, arg2, result)
        self.instructions.append(instr)
        return instr
    
    def enter_scope(self):
        """Enter a new scope"""
        self.scope_depth += 1
        self.var_scopes.append({})  # New scope dictionary
    
    def exit_scope(self):
        """Exit current scope"""
        if self.scope_depth <= 0 or len(self.var_scopes) <= 1:
            return  # Don't exit if we're at global scope
        
        self.var_scopes.pop()  # Remove current scope
        self.scope_depth -= 1
    
    def get_scoped_name(self, var_name: str) -> str:
        """Get the scoped name for a variable (search from innermost to outermost)"""
        # Search from innermost scope to outermost
        for scope in reversed(self.var_scopes):
            if var_name in scope:
                return scope[var_name]
        # Not found in any scope, return original name (global)
        return var_name
    
    def declare_scoped_var(self, var_name: str) -> str:
        """Declare a variable in current scope with unique name"""
        if self.scope_depth > 0:
            scoped_name = f"{var_name}__scope{self.scope_depth}_{self.temp_counter}"
            self.var_scopes[-1][var_name] = scoped_name  # Add to current scope
            return scoped_name
        # Global scope
        self.var_scopes[0][var_name] = var_name
        return var_name
    
    def generate(self, node: ASTNode) -> List[TACInstruction]:
        """Generate TAC for the entire program"""
        self.visit(node)
        return self.instructions
    
    def visit(self, node: ASTNode) -> Optional[str]:
        """Visit a node and return the result location"""
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, None)
        if visitor:
            return visitor(node)
        raise Exception(f"No visit method for {node.__class__.__name__}")
    
    # ========================================================================
    # STATEMENT VISITORS
    # ========================================================================
    
    def visit_ProgramNode(self, node: ProgramNode):
        """Visit program node"""
        for statement in node.statements:
            self.visit(statement)
    
    def visit_VarDeclNode(self, node: VarDeclNode):
        """Visit variable declaration"""
        value_loc = self.visit(node.value)
        # Declare variable with scoped name if in nested scope
        scoped_name = self.declare_scoped_var(node.name)
        self.emit('assign', value_loc, None, scoped_name)
    
    def visit_AssignmentNode(self, node: AssignmentNode):
        """Visit assignment"""
        value_loc = self.visit(node.value)
        
        # Get scoped name for the variable
        scoped_name = self.get_scoped_name(node.name)
        
        if node.index:
            # Array assignment: arr[index] = value
            index_loc = self.visit(node.index)
            self.emit('array_store', index_loc, value_loc, scoped_name)
        else:
            # Simple assignment: x = value
            self.emit('assign', value_loc, None, scoped_name)
    
    def visit_PrintNode(self, node: PrintNode):
        """Visit print statement - supports single or multiple expressions"""
        # Handle both single expression and list of expressions
        if isinstance(node.expression, list):
            for expr in node.expression:
                expr_loc = self.visit(expr)
                self.emit('print', expr_loc)
        else:
            expr_loc = self.visit(node.expression)
            self.emit('print', expr_loc)
    
    def visit_InputNode(self, node: InputNode):
        """Visit input statement"""
        # Get scoped name for the variable
        scoped_name = self.get_scoped_name(node.name)
        self.emit('input', None, None, scoped_name)
    
    def visit_IfNode(self, node: IfNode):
        """Visit if statement"""
        cond_loc = self.visit(node.condition)
        
        else_label = self.new_label()
        end_label = self.new_label()
        
        # If condition is false, jump to else or end
        if node.else_block:
            self.emit('if_false', cond_loc, None, else_label)
        else:
            self.emit('if_false', cond_loc, None, end_label)
        
        # Then block
        for stmt in node.then_block:
            self.visit(stmt)
        
        # Jump to end after then block
        if node.else_block:
            self.emit('goto', None, None, end_label)
            
            # Else block
            self.emit('label', None, None, else_label)
            for stmt in node.else_block:
                self.visit(stmt)
        
        # End label
        self.emit('label', None, None, end_label)
    
    def visit_RepeatNode(self, node: RepeatNode):
        """Visit repeat loop"""
        count_loc = self.visit(node.count)
        
        # Create loop counter
        counter = self.new_temp()
        self.emit('assign', '0', None, counter)
        
        start_label = self.new_label()
        end_label = self.new_label()
        
        # Push loop context for break/continue
        self.loop_stack.append((start_label, end_label))
        
        # Loop start
        self.emit('label', None, None, start_label)
        
        # Check condition: counter < count
        cond_temp = self.new_temp()
        self.emit('<', counter, count_loc, cond_temp)
        self.emit('if_false', cond_temp, None, end_label)
        
        # Loop body
        for stmt in node.body:
            self.visit(stmt)
        
        # Increment counter
        one_temp = self.new_temp()
        self.emit('assign', '1', None, one_temp)
        new_counter = self.new_temp()
        self.emit('+', counter, one_temp, new_counter)
        self.emit('assign', new_counter, None, counter)
        
        # Jump back to start
        self.emit('goto', None, None, start_label)
        
        # End label
        self.emit('label', None, None, end_label)
        
        # Pop loop context
        self.loop_stack.pop()
    
    def visit_ForNode(self, node: ForNode):
        """Visit for loop: for int i = 0; i < 10; i = i + 1: ... end"""
        # Enter new scope for loop variable
        self.enter_scope()
        
        # Generate initialization code (now in loop scope)
        self.visit(node.init)
        
        start_label = self.new_label()
        update_label = self.new_label()
        end_label = self.new_label()
        
        # Push loop context for break/continue
        self.loop_stack.append((update_label, end_label))
        
        # Loop start label
        self.emit('label', None, None, start_label)
        
        # Check condition
        cond_loc = self.visit(node.condition)
        self.emit('if_false', cond_loc, None, end_label)
        
        # Loop body
        for stmt in node.body:
            self.visit(stmt)
        
        # Update label (for continue)
        self.emit('label', None, None, update_label)
        
        # Update statement (e.g., i = i + 1)
        self.visit(node.update)
        
        # Jump back to start
        self.emit('goto', None, None, start_label)
        
        # End label (for break)
        self.emit('label', None, None, end_label)
        
        # Pop loop context
        self.loop_stack.pop()
        
        # Exit scope
        self.exit_scope()
    
    def visit_WhileNode(self, node: WhileNode):
        """Visit while loop"""
        start_label = self.new_label()
        end_label = self.new_label()
        
        # Push loop context for break/continue
        self.loop_stack.append((start_label, end_label))
        
        # Loop start
        self.emit('label', None, None, start_label)
        
        # Check condition
        cond_loc = self.visit(node.condition)
        self.emit('if_false', cond_loc, None, end_label)
        
        # Loop body
        for stmt in node.body:
            self.visit(stmt)
        
        # Jump back to start
        self.emit('goto', None, None, start_label)
        
        # End label
        self.emit('label', None, None, end_label)
        
        # Pop loop context
        self.loop_stack.pop()
    
    def visit_FuncDefNode(self, node: FuncDefNode):
        """Visit function definition"""
        # Skip function body - don't generate code for it inline
        # Jump over function definition
        skip_label = self.new_label()
        self.emit('goto', None, None, skip_label)
        
        # Function label
        func_label = f"func_{node.name}"
        self.emit('label', None, None, func_label)
        
        # Function body
        for stmt in node.body:
            self.visit(stmt)
        
        # Implicit return 0 if no return statement
        self.emit('return', '0')
        
        # Skip label - continue after function definition
        self.emit('label', None, None, skip_label)
    
    def visit_ReturnNode(self, node: ReturnNode):
        """Visit return statement"""
        value_loc = self.visit(node.value)
        self.emit('return', value_loc)
    
    def visit_BreakNode(self, node: BreakNode):
        """Visit break statement"""
        if not self.loop_stack:
            raise Exception("'break' statement outside loop")
        _, break_label = self.loop_stack[-1]
        self.emit('goto', None, None, break_label)
    
    def visit_ContinueNode(self, node: ContinueNode):
        """Visit continue statement"""
        if not self.loop_stack:
            raise Exception("'continue' statement outside loop")
        continue_label, _ = self.loop_stack[-1]
        self.emit('goto', None, None, continue_label)
    
    # ========================================================================
    # EXPRESSION VISITORS
    # ========================================================================
    
    def visit_BinaryOpNode(self, node: BinaryOpNode) -> str:
        """Visit binary operation"""
        left_loc = self.visit(node.left)
        right_loc = self.visit(node.right)
        
        result = self.new_temp()
        self.emit(node.operator, left_loc, right_loc, result)
        return result
    
    def visit_UnaryOpNode(self, node: UnaryOpNode) -> str:
        """Visit unary operation"""
        operand_loc = self.visit(node.operand)
        
        result = self.new_temp()
        self.emit(node.operator, operand_loc, None, result)
        return result
    
    def visit_LiteralNode(self, node: LiteralNode) -> str:
        """Visit literal"""
        # Return the literal value as a string
        if isinstance(node.value, bool):
            return 'true' if node.value else 'false'
        elif isinstance(node.value, str):
            return f'"{node.value}"'
        else:
            return str(node.value)
    
    def visit_IdentifierNode(self, node: IdentifierNode) -> str:
        """Visit identifier"""
        # Return scoped name if variable is in a nested scope
        return self.get_scoped_name(node.name)
    
    def visit_ArrayLiteralNode(self, node: ArrayLiteralNode) -> str:
        """Visit array literal"""
        # Generate code for each element
        element_locs = [self.visit(elem) for elem in node.elements]
        
        # Create array
        result = self.new_temp()
        elements_str = ', '.join(element_locs)
        self.emit('array_literal', elements_str, None, result)
        return result
    
    def visit_ArrayAccessNode(self, node: ArrayAccessNode) -> str:
        """Visit array access"""
        index_loc = self.visit(node.index)
        
        result = self.new_temp()
        self.emit('array_load', node.name, index_loc, result)
        return result
    
    def visit_FuncCallNode(self, node: FuncCallNode) -> str:
        """Visit function call"""
        # Push arguments
        for arg in node.arguments:
            arg_loc = self.visit(arg)
            self.emit('param', arg_loc)
        
        # Call function
        result = self.new_temp()
        num_args = str(len(node.arguments))
        self.emit('call', node.name, num_args, result)
        return result
