# make src.lexer a package
from .lexer import Lexer
from .tokenizer_rules import KEYWORDS, OPERATORS, DELIMITERS
__all__ = ["Lexer", "KEYWORDS", "OPERATORS", "DELIMITERS"]
