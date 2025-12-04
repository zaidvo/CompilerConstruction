# ============================================================================
# AST NODE DEFINITIONS
# ============================================================================
# This module defines all Abstract Syntax Tree node classes
# Each node represents a syntactic construct in CalcScript+

from dataclasses import dataclass
from typing import List, Optional, Any


# Base class for all AST nodes
class ASTNode:
    """Base class for all AST nodes"""
    pass


# ============================================================================
# STATEMENT NODES
# ============================================================================

@dataclass
class ProgramNode(ASTNode):
    """Root node representing the entire program"""
    statements: List[ASTNode]


@dataclass
class VarDeclNode(ASTNode):
    """Variable declaration with type: int x = 10"""
    var_type: str  # int, long, float, string, boolean, array, matrix
    name: str
    value: ASTNode
    line: int = 0
    column: int = 0


@dataclass
class AssignmentNode(ASTNode):
    """Assignment: x = 20 or arr[0] = 5"""
    name: str
    value: ASTNode
    index: Optional[ASTNode] = None  # For array assignment
    line: int = 0
    column: int = 0


@dataclass
class PrintNode(ASTNode):
    """Print statement: dikhao x"""
    expression: ASTNode
    line: int = 0
    column: int = 0


@dataclass
class InputNode(ASTNode):
    """Input statement: bolo x"""
    name: str


@dataclass
class IfNode(ASTNode):
    """If-else statement: agar condition: ... magar: ... khatam"""
    condition: ASTNode
    then_block: List[ASTNode]
    else_block: Optional[List[ASTNode]] = None


@dataclass
class RepeatNode(ASTNode):
    """Repeat loop: dubara kro 5 itni dafa: ... khatam"""
    count: ASTNode
    body: List[ASTNode]


@dataclass
class WhileNode(ASTNode):
    """While loop: KrtayRaho condition: ... khatam"""
    condition: ASTNode
    body: List[ASTNode]


@dataclass
class ForNode(ASTNode):
    """For loop: for int i = 0; i < 10; i = i + 1: ... end"""
    init: ASTNode  # Initialization statement (VarDeclNode or AssignmentNode)
    condition: ASTNode  # Condition expression
    update: ASTNode  # Update statement (AssignmentNode)
    body: List[ASTNode]


@dataclass
class FuncDefNode(ASTNode):
    """Function definition: function int func(int a, int b): ... end"""
    return_type: str  # int, long, float, string, boolean, array, matrix
    name: str
    parameters: List[tuple]  # List of (type, name) tuples
    body: List[ASTNode]


@dataclass
class ReturnNode(ASTNode):
    """Return statement: wapis value"""
    value: ASTNode


@dataclass
class BreakNode(ASTNode):
    """Break statement: toro"""
    pass


@dataclass
class ContinueNode(ASTNode):
    """Continue statement: ChaltayRho"""
    pass


# ============================================================================
# EXPRESSION NODES
# ============================================================================

@dataclass
class BinaryOpNode(ASTNode):
    """Binary operation: left op right"""
    operator: str
    left: ASTNode
    right: ASTNode


@dataclass
class UnaryOpNode(ASTNode):
    """Unary operation: op operand"""
    operator: str
    operand: ASTNode


@dataclass
class LiteralNode(ASTNode):
    """Literal value: number, string, or boolean"""
    value: Any


@dataclass
class IdentifierNode(ASTNode):
    """Variable reference"""
    name: str
    line: int = 0
    column: int = 0


@dataclass
class ArrayLiteralNode(ASTNode):
    """Array literal: [1, 2, 3]"""
    elements: List[ASTNode]


@dataclass
class ArrayAccessNode(ASTNode):
    """Array access: arr[index]"""
    name: str
    index: ASTNode


@dataclass
class FuncCallNode(ASTNode):
    """Function call: func(arg1, arg2)"""
    name: str
    arguments: List[ASTNode]
    line: int = 0
    column: int = 0
