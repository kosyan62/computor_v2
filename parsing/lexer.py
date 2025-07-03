import ply.lex as lex

tokens = (  # Operators
    'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'POWER', 'MODULO', 'FLOORDIV',

    # Equals
    'EQ', 'LT', 'GT', 'LTE', 'GTE', 'NEQ',

    # Brackets
    'LPAREN', 'RPAREN', 'LSQBRACKET', 'RSQBRACKET',

    # Words
    'ID', 'NUMBER',

    # Specials
    'COMMA', 'ASSIGNMENT', 'SEMICOLON'
)

# Operators
t_PLUS = r'\+'
t_MINUS = r'\-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'\/'
t_POWER = r'\^|\*\*'
t_MODULO = r'\%'
t_FLOORDIV = r'\/\/'

# Equals
t_EQ = r'\=='
t_LT = r'\<'
t_GT = r'\>'
t_LTE = r'\<\='
t_GTE = r'\>\='
t_NEQ = r'\!\='

# Brackets
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LSQBRACKET = r'\['
t_RSQBRACKET = r'\]'

# Specials
t_COMMA = r'\,'
t_SEMICOLON = r'\;'
t_ASSIGNMENT = r'\='

t_ignore = ' \t'

def t_NUMBER(t):
    r"""(\d+(\.\d+)?)"""
    t.value = float(t.value)
    return t

def t_ID(t):
    r"""[a-zA-Z_][a-zA-Z_0-9]*"""
    return t


def t_newline(t):
    r"""n+"""
    t.lexer.lineno += len(t.value)


def t_error(t):
    raise ValueError("Illegal character '%s' on position %d" % (t.value[0], t.lexpos))


# Build the lexer
lexer = lex.lex()
