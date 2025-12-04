# ============================================================================
# PHASE 2: SYNTAX ANALYSIS
# ============================================================================
# This module implements the parser for CalcScript+
# It builds an Abstract Syntax Tree (AST) from the token stream

from typing import List, Optional
from lexer import Token, TokenType
from ast_nodes import *


class Parser:
    """Recursive descent parser for CalcScript+"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None
    
    def error(self, message: str):
        """Raise a syntax error with position information"""
        if self.current_token:
            raise SyntaxError(
                f"Syntax error at line {self.current_token.line}, "
                f"column {self.current_token.column}: {message}"
            )
        else:
            raise SyntaxError(f"Syntax error: {message}")
    
    def peek(self, offset: int = 0) -> Optional[Token]:
        """Look ahead at token without consuming it"""
        pos = self.pos + offset
        return self.tokens[pos] if pos < len(self.tokens) else None
    
    def advance(self) -> Token:
        """Consume and return the current token"""
        token = self.current_token
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None
        return token
    
    def expect(self, token_type: TokenType) -> Token:
        """Consume a token of the expected type or raise error"""
        if self.current_token and self.current_token.type == token_type:
            return self.advance()
        
        # Provide detailed error message
        if self.current_token:
            actual = self.current_token.type.name
            value = f" '{self.current_token.value}'" if self.current_token.value else ""
            self.error(f"Expected {token_type.name}, got {actual}{value}")
        else:
            self.error(f"Expected {token_type.name}, got EOF")
    
    def skip_newlines(self):
        """Skip any newline tokens"""
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
    
    def parse(self) -> ProgramNode:
        """Parse the entire program"""
        statements = []
        self.skip_newlines()
        
        while self.current_token and self.current_token.type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                # Handle multiple declarations from parse_var_decl
                if isinstance(stmt, list):
                    statements.extend(stmt)
                else:
                    statements.append(stmt)
            self.skip_newlines()
        
        return ProgramNode(statements)
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement"""
        self.skip_newlines()
        
        if not self.current_token or self.current_token.type == TokenType.EOF:
            return None
        
        token_type = self.current_token.type
        
        # Type keywords indicate variable declaration
        if token_type in (TokenType.INT, TokenType.LONG, TokenType.FLOAT, 
                         TokenType.STRING_TYPE, TokenType.BOOLEAN, 
                         TokenType.ARRAY, TokenType.MATRIX):
            return self.parse_var_decl()
        elif token_type == TokenType.PRINT:
            return self.parse_print()
        elif token_type == TokenType.INPUT:
            return self.parse_input()
        elif token_type == TokenType.IF:
            return self.parse_if()
        elif token_type == TokenType.REPEAT:
            return self.parse_repeat()
        elif token_type == TokenType.WHILE:
            return self.parse_while()
        elif token_type == TokenType.FOR:
            return self.parse_for()
        elif token_type == TokenType.FUNCTION:
            return self.parse_function_def()
        elif token_type == TokenType.RETURN:
            return self.parse_return()
        elif token_type == TokenType.BREAK:
            self.advance()
            return BreakNode()
        elif token_type == TokenType.CONTINUE:
            self.advance()
            return ContinueNode()
        elif token_type == TokenType.IDENTIFIER:
            # Could be assignment or function call
            if self.peek(1) and self.peek(1).type in (TokenType.ASSIGN, TokenType.LBRACKET):
                return self.parse_assignment()
            elif self.peek(1) and self.peek(1).type == TokenType.LPAREN:
                func_call = self.parse_function_call()
                return func_call
            else:
                self.error(f"Unexpected identifier '{self.current_token.value}'")
        else:
            self.error(f"Unexpected token {token_type.name}")
    
    def parse_var_decl(self):
        """Parse variable declaration: int x = expr OR int x OR int x=1, y=2, z"""
        # Parse type keyword
        var_type = self.current_token.value
        self.advance()  # consume type keyword
        
        declarations = []
        
        # Parse first declaration
        name_token = self.expect(TokenType.IDENTIFIER)
        
        # Check if there's an initialization
        if self.current_token and self.current_token.type == TokenType.ASSIGN:
            self.advance()  # consume ASSIGN
            value = self.parse_expression()
        else:
            # No initialization - use default value based on type
            value = self._get_default_value(var_type)
        
        declarations.append(VarDeclNode(var_type, name_token.value, value, name_token.line, name_token.column))
        
        # Check for additional declarations separated by commas
        while self.current_token and self.current_token.type == TokenType.COMMA:
            self.advance()  # consume COMMA
            
            name_token = self.expect(TokenType.IDENTIFIER)
            
            # Check if there's an initialization
            if self.current_token and self.current_token.type == TokenType.ASSIGN:
                self.advance()  # consume ASSIGN
                value = self.parse_expression()
            else:
                # No initialization - use default value based on type
                value = self._get_default_value(var_type)
            
            declarations.append(VarDeclNode(var_type, name_token.value, value, name_token.line, name_token.column))
        
        # Return single declaration or list
        if len(declarations) == 1:
            return declarations[0]
        else:
            return declarations
    
    def _get_default_value(self, var_type):
        """Get default value for a given type"""
        if var_type in ('int', 'long'):
            return LiteralNode(0)
        elif var_type == 'float':
            return LiteralNode(0.0)
        elif var_type == 'string':
            return LiteralNode("")
        elif var_type == 'boolean':
            return LiteralNode(False)
        elif var_type in ('array', 'matrix'):
            return ArrayLiteralNode([])
        else:
            return LiteralNode(0)  # Default to 0
    
    def parse_assignment(self) -> AssignmentNode:
        """Parse assignment: x = expr or x[index] = expr"""
        name_token = self.expect(TokenType.IDENTIFIER)
        
        # Check for array assignment
        if self.current_token and self.current_token.type == TokenType.LBRACKET:
            self.advance()
            index = self.parse_expression()
            self.expect(TokenType.RBRACKET)
            self.expect(TokenType.ASSIGN)
            value = self.parse_expression()
            return AssignmentNode(name_token.value, value, index, name_token.line, name_token.column)
        else:
            self.expect(TokenType.ASSIGN)
            value = self.parse_expression()
            return AssignmentNode(name_token.value, value, None, name_token.line, name_token.column)
    
    def parse_print(self) -> PrintNode:
        """Parse print statement: print expr OR print x, y, z"""
        print_token = self.current_token
        self.expect(TokenType.PRINT)
        
        expressions = []
        
        # Parse first expression
        expr = self.parse_expression()
        expressions.append(expr)
        
        # Check for additional expressions separated by commas
        while self.current_token and self.current_token.type == TokenType.COMMA:
            self.advance()  # consume COMMA
            expr = self.parse_expression()
            expressions.append(expr)
        
        # Return single print or multi-print
        line = print_token.line if print_token else 0
        column = print_token.column if print_token else 0
        if len(expressions) == 1:
            return PrintNode(expressions[0], line, column)
        else:
            return PrintNode(expressions, line, column)
    
    def parse_input(self) -> InputNode:
        """Parse input statement: input x"""
        self.expect(TokenType.INPUT)
        name_token = self.expect(TokenType.IDENTIFIER)
        return InputNode(name_token.value)
    
    def parse_if(self) -> IfNode:
        """Parse if statement: if expr: ... [else: ...] end"""
        self.expect(TokenType.IF)
        condition = self.parse_expression()
        if self.current_token and self.current_token.type != TokenType.COLON:
            self.error(f"Expected ':' after if condition, got {self.current_token.type.name}")
        self.expect(TokenType.COLON)
        self.skip_newlines()
        
        then_block = []
        while self.current_token and self.current_token.type not in (TokenType.ELSE, TokenType.END):
            if self.current_token.type == TokenType.EOF:
                self.error("Missing 'end' or 'else' keyword for if statement")
            stmt = self.parse_statement()
            if stmt:
                then_block.append(stmt)
            self.skip_newlines()
        
        else_block = None
        if self.current_token and self.current_token.type == TokenType.ELSE:
            self.advance()
            if self.current_token and self.current_token.type != TokenType.COLON:
                self.error(f"Expected ':' after 'else', got {self.current_token.type.name}")
            self.expect(TokenType.COLON)
            self.skip_newlines()
            
            else_block = []
            while self.current_token and self.current_token.type != TokenType.END:
                if self.current_token.type == TokenType.EOF:
                    self.error("Missing 'end' keyword for if-else statement")
                stmt = self.parse_statement()
                if stmt:
                    else_block.append(stmt)
                self.skip_newlines()
        
        if not self.current_token or self.current_token.type == TokenType.EOF:
            self.error("Missing 'end' keyword for if statement")
        self.expect(TokenType.END)
        return IfNode(condition, then_block, else_block)
    
    def parse_repeat(self) -> RepeatNode:
        """Parse repeat loop: repeat expr times: ... end"""
        self.expect(TokenType.REPEAT)
        count = self.parse_expression()
        self.expect(TokenType.TIMES)
        self.expect(TokenType.COLON)
        self.skip_newlines()
        
        body = []
        iteration_count = 0
        max_iterations = 1000
        while self.current_token and self.current_token.type != TokenType.END:
            if self.current_token.type == TokenType.EOF:
                self.error("Missing 'end' keyword for repeat loop")
            iteration_count += 1
            if iteration_count > max_iterations:
                self.error("Infinite loop detected while parsing repeat loop. Check for missing 'end' keyword.")
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            self.skip_newlines()
        
        self.expect(TokenType.END)
        return RepeatNode(count, body)
    
    def parse_while(self) -> WhileNode:
        """Parse while loop: while expr: ... end"""
        self.expect(TokenType.WHILE)
        condition = self.parse_expression()
        self.expect(TokenType.COLON)
        self.skip_newlines()
        
        body = []
        while self.current_token and self.current_token.type != TokenType.END:
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            self.skip_newlines()
        
        self.expect(TokenType.END)
        return WhileNode(condition, body)
    
    def parse_for(self) -> ForNode:
        """Parse for loop: for int i = 0; i < 10; i = i + 1: ... end"""
        self.expect(TokenType.FOR)
        
        # Parse initialization (variable declaration or assignment)
        init_stmt = None
        if self.current_token and self.current_token.type in (TokenType.INT, TokenType.LONG,
                                                                TokenType.FLOAT, TokenType.STRING_TYPE,
                                                                TokenType.BOOLEAN, TokenType.ARRAY,
                                                                TokenType.MATRIX):
            init_stmt = self.parse_var_decl()
        elif self.current_token and self.current_token.type == TokenType.IDENTIFIER:
            init_stmt = self.parse_assignment()
        else:
            self.error("Expected variable declaration or assignment in for-loop initialization")
        
        self.expect(TokenType.SEMICOLON)
        
        # Parse condition
        condition = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        
        # Parse update statement (assignment)
        update_stmt = None
        if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
            update_stmt = self.parse_assignment()
        else:
            self.error("Expected assignment in for-loop update")
        
        self.expect(TokenType.COLON)
        self.skip_newlines()
        
        # Parse body
        body = []
        iteration_count = 0
        max_iterations = 1000
        while self.current_token and self.current_token.type != TokenType.END:
            if self.current_token.type == TokenType.EOF:
                self.error("Missing 'end' keyword for for loop")
            iteration_count += 1
            if iteration_count > max_iterations:
                self.error("Infinite loop detected while parsing for loop. Check for missing 'end' keyword.")
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            self.skip_newlines()
        
        self.expect(TokenType.END)
        return ForNode(init_stmt, condition, update_stmt, body)
    
    def parse_function_def(self) -> FuncDefNode:
        """Parse function definition: function int name(int a, int b): ... end"""
        self.expect(TokenType.FUNCTION)
        
        # Parse return type
        if self.current_token.type in (TokenType.INT, TokenType.LONG, TokenType.FLOAT,
                                       TokenType.STRING_TYPE, TokenType.BOOLEAN,
                                       TokenType.ARRAY, TokenType.MATRIX, TokenType.VOID):
            return_type = self.current_token.value
            self.advance()
        else:
            self.error("Expected return type after 'function' keyword")
        
        # Parse function name
        name_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.LPAREN)
        
        # Parse typed parameters
        parameters = []
        if self.current_token and self.current_token.type in (TokenType.INT, TokenType.LONG,
                                                               TokenType.FLOAT, TokenType.STRING_TYPE,
                                                               TokenType.BOOLEAN, TokenType.ARRAY,
                                                               TokenType.MATRIX):
            param_type = self.current_token.value
            self.advance()
            param_name = self.expect(TokenType.IDENTIFIER).value
            parameters.append((param_type, param_name))
            
            while self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()
                param_type = self.current_token.value
                self.advance()
                param_name = self.expect(TokenType.IDENTIFIER).value
                parameters.append((param_type, param_name))
        
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.COLON)
        self.skip_newlines()
        
        body = []
        loop_safety = 0
        while self.current_token and self.current_token.type != TokenType.END:
            if self.current_token.type == TokenType.EOF:
                self.error(f"Missing 'end' keyword for function '{name_token.value}'. Check for missing 'end' in if/else blocks.")
            loop_safety += 1
            if loop_safety > 500:
                self.error(f"Parser stuck in infinite loop in function '{name_token.value}'. Likely missing 'end' keyword.")
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            self.skip_newlines()
        
        self.expect(TokenType.END)
        return FuncDefNode(return_type, name_token.value, parameters, body)
    
    def parse_return(self) -> ReturnNode:
        """Parse return statement: return expr"""
        self.expect(TokenType.RETURN)
        value = self.parse_expression()
        return ReturnNode(value)
    
    def parse_function_call(self) -> FuncCallNode:
        """Parse function call: name(args)"""
        name_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.LPAREN)
        
        arguments = []
        if self.current_token and self.current_token.type != TokenType.RPAREN:
            arguments.append(self.parse_expression())
            while self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()
                arguments.append(self.parse_expression())
        
        self.expect(TokenType.RPAREN)
        return FuncCallNode(name_token.value, arguments)
    
    # ========================================================================
    # EXPRESSION PARSING (with proper precedence)
    # ========================================================================
    
    def parse_expression(self) -> ASTNode:
        """Parse expression (lowest precedence)"""
        return self.parse_logical_or()
    
    def parse_logical_or(self) -> ASTNode:
        """Parse logical OR: expr or expr"""
        left = self.parse_logical_and()
        
        while self.current_token and self.current_token.type == TokenType.OR:
            op = self.advance().value
            right = self.parse_logical_and()
            left = BinaryOpNode(op, left, right)
        
        return left
    
    def parse_logical_and(self) -> ASTNode:
        """Parse logical AND: expr and expr"""
        left = self.parse_equality()
        
        while self.current_token and self.current_token.type == TokenType.AND:
            op = self.advance().value
            right = self.parse_equality()
            left = BinaryOpNode(op, left, right)
        
        return left
    
    def parse_equality(self) -> ASTNode:
        """Parse equality: expr == expr, expr != expr"""
        left = self.parse_comparison()
        
        while self.current_token and self.current_token.type in (TokenType.EQ, TokenType.NE):
            op = self.advance().value
            right = self.parse_comparison()
            left = BinaryOpNode(op, left, right)
        
        return left
    
    def parse_comparison(self) -> ASTNode:
        """Parse comparison: expr > expr, expr < expr, etc."""
        left = self.parse_additive()
        
        while self.current_token and self.current_token.type in (TokenType.GT, TokenType.LT, TokenType.GE, TokenType.LE):
            op = self.advance().value
            right = self.parse_additive()
            left = BinaryOpNode(op, left, right)
        
        return left
    
    def parse_additive(self) -> ASTNode:
        """Parse addition/subtraction: expr + expr, expr - expr"""
        left = self.parse_multiplicative()
        
        while self.current_token and self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            right = self.parse_multiplicative()
            left = BinaryOpNode(op, left, right)
        
        return left
    
    def parse_multiplicative(self) -> ASTNode:
        """Parse multiplication/division/modulo: expr * expr, expr / expr, expr % expr"""
        left = self.parse_exponentiation()
        
        while self.current_token and self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op = self.advance().value
            right = self.parse_exponentiation()
            left = BinaryOpNode(op, left, right)
        
        return left
    
    def parse_exponentiation(self) -> ASTNode:
        """Parse exponentiation: expr ^ expr (right associative)"""
        left = self.parse_unary()
        
        if self.current_token and self.current_token.type == TokenType.POWER:
            op = self.advance().value  # consume '^'
            
            # Check for special matrix operations: ^t (transpose) or ^-1 (inverse)
            if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                if self.current_token.value == 't':
                    self.advance()  # consume 't'
                    return BinaryOpNode('^', left, LiteralNode('t'))
                else:
                    # Regular exponentiation with identifier
                    right = self.parse_exponentiation()
                    return BinaryOpNode(op, left, right)
            elif self.current_token and self.current_token.type == TokenType.MINUS:
                # Check for ^-1 (inverse)
                self.advance()  # consume '-'
                if self.current_token and self.current_token.type == TokenType.NUMBER and self.current_token.value == 1:
                    self.advance()  # consume '1'
                    return BinaryOpNode('^', left, LiteralNode(-1))
                else:
                    # It's a negative exponent
                    right = UnaryOpNode('-', self.parse_exponentiation())
                    return BinaryOpNode('^', left, right)
            else:
                # Regular exponentiation
                right = self.parse_exponentiation()  # Right associative
                return BinaryOpNode(op, left, right)
        
        return left
    
    def parse_unary(self) -> ASTNode:
        """Parse unary operations: -expr, not expr"""
        if self.current_token and self.current_token.type in (TokenType.MINUS, TokenType.NOT):
            op = self.advance().value
            operand = self.parse_unary()
            return UnaryOpNode(op, operand)
        
        return self.parse_primary()
    
    def parse_primary(self) -> ASTNode:
        """Parse primary expressions: literals, identifiers, function calls, array access, etc."""
        if not self.current_token:
            self.error("Unexpected end of input")
        
        token_type = self.current_token.type
        
        # Number literal
        if token_type == TokenType.NUMBER:
            value = self.advance().value
            return LiteralNode(value)
        
        # String literal
        elif token_type == TokenType.STRING:
            value = self.advance().value
            return LiteralNode(value)
        
        # Boolean literal
        elif token_type in (TokenType.TRUE, TokenType.FALSE):
            value = True if token_type == TokenType.TRUE else False
            self.advance()
            return LiteralNode(value)
        
        # Identifier (variable, function call, or array access)
        elif token_type == TokenType.IDENTIFIER:
            name = self.advance().value
            
            # Function call
            if self.current_token and self.current_token.type == TokenType.LPAREN:
                # Get line/column from the identifier token we just consumed
                line = self.tokens[self.pos - 1].line if self.pos > 0 else 0
                column = self.tokens[self.pos - 1].column if self.pos > 0 else 0
                self.expect(TokenType.LPAREN)
                arguments = []
                if self.current_token and self.current_token.type != TokenType.RPAREN:
                    arguments.append(self.parse_expression())
                    while self.current_token and self.current_token.type == TokenType.COMMA:
                        self.advance()
                        arguments.append(self.parse_expression())
                self.expect(TokenType.RPAREN)
                return FuncCallNode(name, arguments, line, column)
            
            # Array access
            elif self.current_token and self.current_token.type == TokenType.LBRACKET:
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                return ArrayAccessNode(name, index)
            
            # Simple identifier
            else:
                # Get line/column from the token we just consumed
                line = self.tokens[self.pos - 1].line if self.pos > 0 else 0
                column = self.tokens[self.pos - 1].column if self.pos > 0 else 0
                return IdentifierNode(name, line, column)
        
        # Array literal
        elif token_type == TokenType.LBRACKET:
            self.advance()
            elements = []
            if self.current_token and self.current_token.type != TokenType.RBRACKET:
                elements.append(self.parse_expression())
                while self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()
                    elements.append(self.parse_expression())
            self.expect(TokenType.RBRACKET)
            return ArrayLiteralNode(elements)
        
        # Parenthesized expression
        elif token_type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        else:
            self.error(f"Unexpected token {token_type.name}")
