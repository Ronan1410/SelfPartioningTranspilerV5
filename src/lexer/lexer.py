"""
A pragmatic, small Python lexer (not a full CPython tokenizer).
Produces a list of Token(type, value, line, col).

Usage:
    from src.lexer.lexer import Lexer
    tokens = Lexer(code).tokenize()
"""

from dataclasses import dataclass
from typing import List, Optional
from .tokenizer_rules import KEYWORDS, OPERATORS, DELIMITERS

@dataclass
class Token:
    type: str
    value: object
    line: int
    col: int

    def __repr__(self):
        return f"Token({self.type!r}, {self.value!r}, line={self.line}, col={self.col})"

class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.col = 0
        self.N = len(code)

    def _peek(self, n=0) -> Optional[str]:
        i = self.pos + n
        if i < self.N:
            return self.code[i]
        return None

    def _advance(self, n=1):
        for _ in range(n):
            if self.pos < self.N:
                c = self.code[self.pos]
                self.pos += 1
                if c == "\n":
                    self.line += 1
                    self.col = 0
                else:
                    self.col += 1

    def _skip_whitespace_and_comments(self):
        while True:
            c = self._peek()
            if c is None:
                return
            # spaces and tabs and carriage returns
            if c in " \t\r":
                self._advance()
                continue
            # newline - treat as delimiter token NEWLINE
            if c == "\n":
                # emit NEWLINE token as separate token
                return
            # comment
            if c == "#":
                # skip until newline or EOF
                while self._peek() not in (None, "\n"):
                    self._advance()
                continue
            break

    def _read_identifier_or_keyword(self) -> Token:
        start_col = self.col
        start = self.pos
        while True:
            c = self._peek()
            if c is None or not (c.isalnum() or c == "_"):
                break
            self._advance()
        txt = self.code[start:self.pos]
        if txt in KEYWORDS:
            t = "KEYWORD"
        elif txt in OPERATORS:
            t = "OP"
        else:
            t = "IDENT"
        return Token(t, txt, self.line, start_col)

    def _read_number(self) -> Token:
        start_col = self.col
        start = self.pos
        has_dot = False
        while True:
            c = self._peek()
            if c is None:
                break
            if c == "." and not has_dot:
                has_dot = True
                self._advance()
                continue
            if c.isdigit():
                self._advance()
                continue
            break
        txt = self.code[start:self.pos]
        val = float(txt) if has_dot else int(txt)
        return Token("NUMBER", val, self.line, start_col)

    def _read_string(self) -> Token:
        quote = self._peek()
        start_col = self.col
        self._advance()  # skip opening quote
        buf = []
        while True:
            c = self._peek()
            if c is None:
                # unterminated string -> return what we have
                break
            if c == "\\":
                self._advance()
                nxt = self._peek()
                if nxt is None:
                    break
                # simple escapes
                esc_map = {"n":"\n","t":"\t","r":"\r","'":"'",'"':'"', "\\":"\\"}
                if nxt in esc_map:
                    buf.append(esc_map[nxt])
                else:
                    buf.append(nxt)
                self._advance()
                continue
            if c == quote:
                self._advance()
                break
            buf.append(c)
            self._advance()
        return Token("STRING", "".join(buf), self.line, start_col)

    def _try_multi_char_operator(self) -> Optional[Token]:
        # check 3,2,1 char ops (we only defined common ones)
        for length in (3,2):
            s = "".join(self._peek(i) or "" for i in range(length))
            if s in OPERATORS:
                start_col = self.col
                self._advance(length)
                return Token("OP", s, self.line, start_col)
        # single char operator
        c = self._peek()
        if c in OPERATORS:
            start_col = self.col
            self._advance()
            return Token("OP", c, self.line, start_col)
        return None

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while self.pos < self.N:
            self._skip_whitespace_and_comments()
            c = self._peek()
            if c is None:
                break
            # newlines as tokens (useful for simple parsers)
            if c == "\n":
                tokens.append(Token("NEWLINE", "\\n", self.line, self.col))
                self._advance()
                continue
            # identifiers / keywords
            if c.isalpha() or c == "_":
                tok = self._read_identifier_or_keyword()
                tokens.append(tok)
                continue
            # numbers
            if c.isdigit():
                tok = self._read_number()
                tokens.append(tok)
                continue
            # strings
            if c in ("'", '"'):
                tok = self._read_string()
                tokens.append(tok)
                continue
            # delimiters
            if c in DELIMITERS:
                tokens.append(Token("DELIM", c, self.line, self.col))
                self._advance()
                continue
            # operators (including multi-char)
            op_tok = self._try_multi_char_operator()
            if op_tok:
                tokens.append(op_tok)
                continue

            # unknown char: emit it as UNKNOWN token and advance
            tokens.append(Token("UNKNOWN", c, self.line, self.col))
            self._advance()

        # EOF token
        tokens.append(Token("EOF", None, self.line, self.col))
        return tokens
