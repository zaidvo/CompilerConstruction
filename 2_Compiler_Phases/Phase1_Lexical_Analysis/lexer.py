# ============================================================================
# PHASE 1: LEXICAL ANALYSIS
# ============================================================================
# This module implements the lexer for CalcScript+
# It tokenizes the input source code into a stream of tokens

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    """Enumeration of all token types in CalcScript+"""
    # Keywords
    PRINT = auto()          # print statement
    REPEAT = auto()         # repeat loop
    TIMES = auto()          # times
    IF = auto()             # if statement
    ELSE = auto()           # else statement
    FUNCTION = auto()       # function definition
    RETURN = auto()         # return statement
    END = auto()            # end block
    WHILE = auto()          # while loop
    INPUT = auto()          # input statement
    BREAK = auto()          # break statement
    CONTINUE = auto()       # continue statement
    TRUE = auto()           # true boolean
    FALSE = auto()          # false boolean
    AND = auto()            # and operator
    OR = auto()             # or operator
    NOT = auto()            # not operator
    
    # Type keywords
    INT = auto()            # int type
    LONG = auto()           # long type
    FLOAT = auto()          # float type
    STRING_TYPE = auto()    # string type
    BOOLEAN = auto()        # boolean type
    ARRAY = auto()          # array type
    MATRIX = auto()         # matrix type
    
    # Literals
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()
    
    # Operators
    PLUS = auto()           # +
    MINUS = auto()          # -
    MULTIPLY = auto()       # *
    DIVIDE = auto()         # /
    MODULO = auto()         # %
    POWER = auto()          # ^
    ASSIGN = auto()         # =
    EQ = auto()             # ==
    NE = auto()             # !=
    LT = auto()             # <
    GT = auto()             # >
    LE = auto()             # <=
    GE = auto()             # >=
    
    # Delimiters
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    LBRACKET = auto()       # [
    RBRACKET = auto()       # ]
    COLON = auto()          # :
    COMMA = auto()          # ,
    
    # Special
    NEWLINE = auto()
    EOF = auto()


@dataclass
class Token:
    """Represents a single token with its type, value, and position"""
    type: TokenType
    value: any
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"


class Lexer:
    """Lexical analyzer for CalcScript+"""
    
    # Keyword mappings
    KEYWORDS = {
        'print': TokenType.PRINT,
        'repeat': TokenType.REPEAT,
        'times': TokenType.TIMES,
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'function': TokenType.FUNCTION,
        'return': TokenType.RETURN,
        'end': TokenType.END,
        'while': TokenType.WHILE,
        'input': TokenType.INPUT,
        'break': TokenType.BREAK,
        'continue': TokenType.CONTINUE,
        'true': TokenType.TRUE,
        'false': TokenType.FALSE,
        'and': TokenType.AND,
        'or': TokenType.OR,
        'not': TokenType.NOT,
        # Type keywords
        'int': TokenType.INT,
        'long': TokenType.LONG,
        'float': TokenType.FLOAT,
        'string': TokenType.STRING_TYPE,
        'boolean': TokenType.BOOLEAN,
        'array': TokenType.ARRAY,
        'matrix': TokenType.MATRIX,
    }
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def error(self, message: str):
        """Raise a lexical error with position information"""
        raise SyntaxError(f"Lexical error at line {self.line}, column {self.column}: {message}")
    
    def peek(self, offset: int = 0) -> Optional[str]:
        """Look ahead at character without consuming it"""
        pos = self.pos + offset
        return self.source[pos] if pos < len(self.source) else None
    
    def advance(self) -> Optional[str]:
        """Consume and return the current character"""
        if self.pos >= len(self.source):
            return None
        
        char = self.source[self.pos]
        self.pos += 1
        
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        return char
    
    def skip_whitespace(self):
        """Skip spaces and tabs (but not newlines)"""
        while self.peek() in ' \t':
            self.advance()
    
    def skip_comment(self):
        """Skip single-line comments starting with #"""
        if self.peek() == '#':
            while self.peek() and self.peek() != '\n':
                self.advance()
    
    def read_number(self) -> Token:
        """Read a number literal (integer or float)"""
        start_line, start_col = self.line, self.column
        num_str = ''
        
        # Handle negative numbers
        if self.peek() == '-':
            num_str += self.advance()
        
        # Read digits
        while self.peek() and self.peek().isdigit():
            num_str += self.advance()
        
        # Check for decimal point
        if self.peek() == '.' and self.peek(1) and self.peek(1).isdigit():
            num_str += self.advance()  # consume '.'
            while self.peek() and self.peek().isdigit():
                num_str += self.advance()
            value = float(num_str)
        else:
            value = int(num_str)
        
        return Token(TokenType.NUMBER, value, start_line, start_col)
    
    def read_string(self) -> Token:
        """Read a string literal enclosed in double quotes"""
        start_line, start_col = self.line, self.column
        self.advance()  # consume opening quote
        
        string_val = ''
        while self.peek() and self.peek() != '"':
            char = self.advance()
            if char == '\\':
                # Handle escape sequences
                next_char = self.advance()
                if next_char == 'n':
                    string_val += '\n'
                elif next_char == 't':
                    string_val += '\t'
                elif next_char == '"':
                    string_val += '"'
                elif next_char == '\\':
                    string_val += '\\'
                else:
                    string_val += next_char
            else:
                string_val += char
        
        if not self.peek():
            self.error("Unterminated string literal")
        
        self.advance()  # consume closing quote
        return Token(TokenType.STRING, string_val, start_line, start_col)
    
    def read_identifier(self) -> Token:
        """Read an identifier or keyword"""
        start_line, start_col = self.line, self.column
        ident = ''
        
        while self.peek() and (self.peek().isalnum() or self.peek() == '_'):
            ident += self.advance()
        
        # Check if it's a keyword
        token_type = self.KEYWORDS.get(ident, TokenType.IDENTIFIER)
        value = ident if token_type == TokenType.IDENTIFIER else ident
        
        return Token(token_type, value, start_line, start_col)
    
    def tokenize(self) -> List[Token]:
        """Main tokenization method - converts source code to token list"""
        while self.pos < len(self.source):
            self.skip_whitespace()
            self.skip_comment()
            
            if self.pos >= len(self.source):
                break
            
            char = self.peek()
            start_line, start_col = self.line, self.column
            
            # Newline
            if char == '\n':
                self.advance()
                self.tokens.append(Token(TokenType.NEWLINE, '\\n', start_line, start_col))
            
            # Numbers
            elif char.isdigit() or (char == '-' and self.peek(1) and self.peek(1).isdigit()):
                self.tokens.append(self.read_number())
            
            # Strings
            elif char == '"':
                self.tokens.append(self.read_string())
            
            # Identifiers and keywords
            elif char.isalpha() or char == '_':
                self.tokens.append(self.read_identifier())
            
            # Operators and delimiters
            elif char == '+':
                self.advance()
                self.tokens.append(Token(TokenType.PLUS, '+', start_line, start_col))
            
            elif char == '-':
                self.advance()
                self.tokens.append(Token(TokenType.MINUS, '-', start_line, start_col))
            
            elif char == '*':
                self.advance()
                self.tokens.append(Token(TokenType.MULTIPLY, '*', start_line, start_col))
            
            elif char == '/':
                self.advance()
                self.tokens.append(Token(TokenType.DIVIDE, '/', start_line, start_col))
            
            elif char == '%':
                self.advance()
                self.tokens.append(Token(TokenType.MODULO, '%', start_line, start_col))
            
            elif char == '^':
                self.advance()
                self.tokens.append(Token(TokenType.POWER, '^', start_line, start_col))
            
            elif char == '=':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.EQ, '==', start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.ASSIGN, '=', start_line, start_col))
            
            elif char == '!':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.NE, '!=', start_line, start_col))
                else:
                    self.error(f"Unexpected character '!'")
            
            elif char == '<':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.LE, '<=', start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.LT, '<', start_line, start_col))
            
            elif char == '>':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.GE, '>=', start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.GT, '>', start_line, start_col))
            
            elif char == '(':
                self.advance()
                self.tokens.append(Token(TokenType.LPAREN, '(', start_line, start_col))
            
            elif char == ')':
                self.advance()
                self.tokens.append(Token(TokenType.RPAREN, ')', start_line, start_col))
            
            elif char == '[':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACKET, '[', start_line, start_col))
            
            elif char == ']':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACKET, ']', start_line, start_col))
            
            elif char == ':':
                self.advance()
                self.tokens.append(Token(TokenType.COLON, ':', start_line, start_col))
            
            elif char == ',':
                self.advance()
                self.tokens.append(Token(TokenType.COMMA, ',', start_line, start_col))
            
            else:
                self.error(f"Unexpected character '{char}'")
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens
