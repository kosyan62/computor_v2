from ply import lex

tokens = (  # Operators
    "PLUS",
    "MINUS",
    "MULTIPLY",
    "MATMUL",
    "DIVIDE",
    "POWER",
    "MODULO",
    "FLOORDIV",
    # Equals
    "EQ",
    "LT",
    "GT",
    "LTE",
    "GTE",
    "NEQ",
    # Brackets
    "LPAREN",
    "RPAREN",
    "LSQBRACKET",
    "RSQBRACKET",
    # Words
    "ID",
    "NUMBER",
    # Specials
    "COMMA",
    "ASSIGNMENT",
    "SEMICOLON",
    "QUERY",
)

# Operators
t_PLUS = r"\+"
t_MINUS = r"\-"
t_MULTIPLY = r"\*"
t_DIVIDE = r"\/"
t_MODULO = r"\%"
t_FLOORDIV = r"\/\/"

# Equals
t_EQ = r"\=="
t_LT = r"\<"
t_GT = r"\>"
t_LTE = r"\<\="
t_GTE = r"\>\="
t_NEQ = r"\!\="

# Brackets
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LSQBRACKET = r"\["
t_RSQBRACKET = r"\]"

# Specials
t_COMMA = r"\,"
t_SEMICOLON = r"\;"
t_ASSIGNMENT = r"\="
t_QUERY = r"\?"

t_ignore = " \t"


def t_MATMUL(t):
    r"""\*\*"""
    return t


def t_POWER(t):
    r"""\^"""
    return t


def t_NUMBER(t):
    r"""(\d+(\.\d+)?)"""
    return t


def t_ID(t):
    r"""[a-zA-Z_][a-zA-Z_0-9]*"""
    return t


def t_newline(t):
    r"""\n+"""
    t.lexer.lineno += len(t.value)


def t_error(t):
    raise ValueError(f"Illegal character '{t.value[0]}' on position {t.lexpos}")


# Build the lexer
lexer = lex.lex()

_IMPLICIT_MULTIPLY_AFTER = ("NUMBER",)
_IMPLICIT_MULTIPLY_BEFORE = ("ID", "LPAREN")


class ImplicitMultiplyLexer:
    """Обёртка над PLY-лексером: инжектирует MULTIPLY между NUMBER и ID/LPAREN."""

    def __init__(self, inner):
        self.inner = inner
        self._queue: list = []

    def input(self, data):
        self.inner.input(data)
        self._queue = []

    def token(self):
        if self._queue:
            return self._queue.pop(0)

        tok = self.inner.token()
        if tok is None:
            return None

        if tok.type in _IMPLICIT_MULTIPLY_AFTER:
            nxt = self.inner.token()
            if nxt is not None and nxt.type in _IMPLICIT_MULTIPLY_BEFORE:
                mul = lex.LexToken()
                mul.type = "MULTIPLY"
                mul.value = "*"
                mul.lineno = tok.lineno
                mul.lexpos = tok.lexpos
                self._queue.append(mul)
                self._queue.append(nxt)

            elif nxt is not None:
                self._queue.append(nxt)

        return tok

    def __getattr__(self, name):
        return getattr(self.inner, name)
