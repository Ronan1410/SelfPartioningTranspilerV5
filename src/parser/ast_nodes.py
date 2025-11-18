"""
Simplified AST node definitions for the custom parser.
Not a full Python AST — only what we need for segmentation.
"""

from dataclasses import dataclass
from typing import List, Optional, Any


@dataclass
class ASTNode:
    pass


@dataclass
class Program(ASTNode):
    body: List[ASTNode]


@dataclass
class FunctionDef(ASTNode):
    name: str
    args: List[str]
    body: List[ASTNode]


@dataclass
class Assign(ASTNode):
    target: str
    value: Any


@dataclass
class Return(ASTNode):
    value: Any


@dataclass
class Expression(ASTNode):
    value: Any


@dataclass
class Call(ASTNode):
    func: str
    args: List[Any]


@dataclass
class If(ASTNode):
    condition: Any
    body: List[ASTNode]
    orelse: List[ASTNode]


@dataclass
class For(ASTNode):
    var: str
    iter: Any
    body: List[ASTNode]


@dataclass
class While(ASTNode):
    condition: Any
    body: List[ASTNode]
