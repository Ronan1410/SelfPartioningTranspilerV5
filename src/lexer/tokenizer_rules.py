# small set of tokenization helpers for the simple lexer

KEYWORDS = {
    "def", "return", "if", "elif", "else", "for", "while",
    "import", "from", "as", "class", "with", "try", "except",
    "finally", "raise", "yield", "lambda", "pass", "break", "continue",
    "async", "await", "global", "nonlocal"
}

# single- and two-char operators supported
OPERATORS = {
    "+", "-", "*", "/", "%", "//", "**",
    "=", "==", "!=", "<", ">", "<=", ">=", "+=", "-=", "*=", "/=",
    "and", "or", "not", "|", "&", "^", "~", "<<", ">>"
}

DELIMITERS = {
    "(", ")", "[", "]", "{", "}", ",", ":", ".", ";"
}
