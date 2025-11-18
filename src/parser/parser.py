"""
A VERY lightweight recursive-descent parser for Python-like syntax.
Not full Python — just enough structure to support code segmentation.

Tokens come from src.lexer.lexer.Lexer
"""

from typing import List, Optional
from src.lexer.lexer import Token
from src.parser.ast_nodes import (
    Program, FunctionDef, Assign, Return, Expression,
    Call, If, For, While
)


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    # ------------------------------------------------------------
    # Utility functions
    # ------------------------------------------------------------

    def peek(self, n=0) -> Optional[Token]:
        i = self.pos + n
        if 0 <= i < len(self.tokens):
            return self.tokens[i]
        return None

    def advance(self) -> Token:
        tok = self.peek()
        self.pos += 1
        return tok

    def match(self, *types):
        tok = self.peek()
        if tok and tok.type in types:
            return self.advance()
        return None

    def expect(self, type_):
        tok = self.peek()
        if not tok or tok.type != type_:
            raise SyntaxError(f"Expected {type_}, got {tok}")
        return self.advance()

    # ------------------------------------------------------------
    # Top-level entry
    # ------------------------------------------------------------

    def parse(self) -> Program:
        body = []
        while True:
            tok = self.peek()
            if tok is None or tok.type == "EOF":
                break
            node = self.parse_statement()
            if node:
                body.append(node)
        return Program(body)

    # ------------------------------------------------------------
    # Statements
    # ------------------------------------------------------------

    def parse_statement(self):
        tok = self.peek()

        if tok.type == "KEYWORD":
            if tok.value == "def":
                return self.parse_function()
            if tok.value == "return":
                return self.parse_return()
            if tok.value == "if":
                return self.parse_if()
            if tok.value == "for":
                return self.parse_for()
            if tok.value == "while":
                return self.parse_while()

        # Assignment or expression
        return self.parse_assignment_or_expr()

    # ------------------------------------------------------------
    # def name(a, b):
    #     body...
    # ------------------------------------------------------------

    def parse_function(self):
        self.expect("KEYWORD")  # def
        name = self.expect("IDENT").value
        self.expect("DELIM")  # '('

        args = []
        while True:
            tok = self.peek()
            if tok.value == ")":
                break
            if tok.type == "IDENT":
                args.append(self.advance().value)
            if tok.value == ",":
                self.advance()
            else:
                break

        self.expect("DELIM")  # ')'
        self.expect("DELIM")  # ':'

        # skip NEWLINE(s)
        while self.match("NEWLINE"):
            pass

        # parse simple indented body: everything until dedent is faked
        body = self.parse_block()
        return FunctionDef(name, args, body)

    # ------------------------------------------------------------
    # paring a return statement
    # ------------------------------------------------------------

    def parse_return(self):
        self.expect("KEYWORD")  # return
        expr = self.parse_expression()
        return Return(expr)

    # ------------------------------------------------------------
    # if x:
    #     body
    # else:
    #     body
    # ------------------------------------------------------------

    def parse_if(self):
        self.expect("KEYWORD")  # if
        condition = self.parse_expression()
        self.expect("DELIM")  # :

        # skip newline(s)
        while self.match("NEWLINE"):
            pass

        body = self.parse_block()

        # check for optional orelse
        orelse = []
        tok = self.peek()
        if tok and tok.type == "KEYWORD" and tok.value == "else":
            self.advance()
            self.expect("DELIM")  # :
            while self.match("NEWLINE"):
                pass
            orelse = self.parse_block()

        return If(condition, body, orelse)

    # ------------------------------------------------------------
    # for x in y:
    # ------------------------------------------------------------

    def parse_for(self):
        self.expect("KEYWORD")  # for
        var = self.expect("IDENT").value
        self.expect("KEYWORD")  # in
        iterable = self.parse_expression()
        self.expect("DELIM")  # :
        while self.match("NEWLINE"):
            pass
        body = self.parse_block()
        return For(var, iterable, body)

    # ------------------------------------------------------------
    # while <cond>:
    # ------------------------------------------------------------

    def parse_while(self):
        self.expect("KEYWORD")  # while
        condition = self.parse_expression()
        self.expect("DELIM")  # :
        while self.match("NEWLINE"):
            pass
        body = self.parse_block()
        return While(condition, body)

    # ------------------------------------------------------------
    # Block = list of statements until blank line OR EOF
    # This is NOT real indentation, just pragmatic segmentation
    # ------------------------------------------------------------

    def parse_block(self):
        body = []
        while True:
            tok = self.peek()
            if tok is None:
                break
            if tok.type == "EOF":
                break
            if tok.type == "NEWLINE":
                self.advance()
                continue
            # a blank line or dedent terminates block; we simplify.
            # (Real indentation not implemented here.)
            if tok.type == "KEYWORD" and tok.value in ("def", "if", "for", "while"):
                break
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        return body

    # ------------------------------------------------------------
    # Assignment or expression
    # ------------------------------------------------------------

    def parse_assignment_or_expr(self):
        tok = self.peek()
        if tok.type == "IDENT":
            # possible assignment
            if self.peek(1) and self.peek(1).value == "=":
                name = self.advance().value
                self.advance()  # '='
                expr = self.parse_expression()
                return Assign(name, expr)

        return Expression(self.parse_expression())

    # ------------------------------------------------------------
    # Expression parsing — minimal Pratt parser
    # ------------------------------------------------------------

    def parse_expression(self):
        tok = self.peek()

        # number or string
        if tok.type in ("NUMBER", "STRING"):
            return self.advance().value

        # identifier (possibly call)
        if tok.type == "IDENT":
            ident = self.advance().value
            # function call
            if self.peek() and self.peek().value == "(":
                self.advance()  # '('
                args = []
                while True:
                    if self.peek().value == ")":
                        break
                    args.append(self.parse_expression())
                    if self.peek().value == ",":
                        self.advance()
                        continue
                    break
                self.expect("DELIM")  # ')'
                return Call(ident, args)
            return ident

        # parenthesized expression
        if tok.type == "DELIM" and tok.value == "(":
            self.advance()
            expr = self.parse_expression()
            self.expect("DELIM")  # ')'
            return expr

        # fallback
        return self.advance().value
