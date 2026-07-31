from ply import yacc

from .AST import (
    BinaryOperationNode,
    ComparisonNode,
    Equality,
    FunctionCallNode,
    FunctionDefinitionNode,
    MatrixNode,
    NumberNode,
    QueryNode,
    SolveNode,
    UnaryMinusNode,
    UnaryPlusNode,
    VariableNode,
)
from .lexer import ImplicitMultiplyLexer, tokens  # noqa F401
from .lexer import lexer as _base_lexer

_lexer = ImplicitMultiplyLexer(_base_lexer)

# Parsing rules
precedence = (
    ("nonassoc", "GT", "GTE", "LT", "LTE", "EQ", "NEQ"),
    ("left", "PLUS", "MINUS"),
    ("left", "MULTIPLY", "MATMUL", "DIVIDE", "FLOORDIV", "MODULO"),
    ("right", "UMINUS"),
    ("right", "POWER"),
)

start = "statement"

# --- Statement (top level) ---

def p_statement(p):
    """statement : equality
    | unequality
    | expression
    | function_definition
    """
    p[0] = p[1]


def p_equality(p):
    """equality : ID ASSIGNMENT expression
    | expression ASSIGNMENT expression
    """
    left = VariableNode(p[1]) if isinstance(p[1], str) else p[1]
    p[0] = Equality(left, p[3])


def p_unequality(p):
    """unequality : expression GT expression
    | expression GTE expression
    | expression LT expression
    | expression LTE expression
    | expression EQ expression
    | expression NEQ expression
    """
    p[0] = ComparisonNode(p[1], p[2], p[3])


def p_query(p):
    """statement : ID ASSIGNMENT QUERY
    | expression ASSIGNMENT QUERY
    | ID LPAREN expressions_list RPAREN ASSIGNMENT QUERY
    | ID LPAREN RPAREN ASSIGNMENT QUERY
    """
    if len(p) == 7:
        expr = FunctionCallNode(p[1], p[3])
    elif len(p) == 6:
        expr = FunctionCallNode(p[1], [])
    else:
        expr = VariableNode(p[1]) if isinstance(p[1], str) else p[1]
    p[0] = QueryNode(expr)


def p_solve(p):
    """statement : ID LPAREN expressions_list RPAREN ASSIGNMENT expression QUERY
    | ID LPAREN RPAREN ASSIGNMENT expression QUERY
    | ID ASSIGNMENT expression QUERY
    | expression ASSIGNMENT expression QUERY
    """
    if len(p) == 8:
        p[0] = SolveNode(FunctionCallNode(p[1], p[3]), p[6])
    elif len(p) == 7:
        p[0] = SolveNode(FunctionCallNode(p[1], []), p[5])
    elif len(p) == 5 and isinstance(p[1], str):
        p[0] = SolveNode(VariableNode(p[1]), p[3])
    else:
        p[0] = SolveNode(p[1], p[3])


# --- Functions ---

def p_function_definition(p):
    """function_definition : ID LPAREN expressions_list RPAREN ASSIGNMENT expression
    | ID LPAREN RPAREN ASSIGNMENT expression
    """
    if len(p) == 7:
        parameters, body = p[3], p[6]
    else:
        parameters, body = [], p[5]
    p[0] = FunctionDefinitionNode(p[1], parameters, body)


def p_function_call(p):
    """function_call : ID LPAREN expressions_list RPAREN
    | ID LPAREN RPAREN
    """
    if len(p) == 5:
        p[0] = FunctionCallNode(p[1], p[3])
    else:
        p[0] = FunctionCallNode(p[1], [])


# --- Atoms (primaries) and power ---

def p_atom_number(p):
    """atom : NUMBER"""
    p[0] = NumberNode(p[1])


def p_atom_variable(p):
    """atom : ID"""
    p[0] = VariableNode(p[1])


def p_atom_group(p):
    """atom : LPAREN expression RPAREN"""
    p[0] = p[2]


def p_atom_function_call(p):
    """atom : function_call"""
    p[0] = p[1]


def p_atom_matrix(p):
    """atom : matrix"""
    p[0] = p[1]


def p_atom_power(p):
    """atom : atom POWER power_rhs"""
    p[0] = BinaryOperationNode(p[1], p[2], p[3])


def p_power_rhs_atom(p):
    """power_rhs : atom"""
    p[0] = p[1]


def p_power_rhs_uminus(p):
    """power_rhs : MINUS atom %prec UMINUS"""
    p[0] = UnaryMinusNode(p[2])


def p_power_rhs_uplus(p):
    """power_rhs : PLUS atom %prec UMINUS"""
    p[0] = UnaryPlusNode(p[2])


# --- Expressions ---

def p_expression_atom(p):
    """expression : atom"""
    p[0] = p[1]


def p_expression_binary(p):
    """expression : expression PLUS expression
    | expression MINUS expression
    | expression MULTIPLY expression
    | expression MATMUL expression
    | expression DIVIDE expression
    | expression MODULO expression
    | expression FLOORDIV expression
    """
    p[0] = BinaryOperationNode(p[1], p[2], p[3])


def p_expression_uminus(p):
    """expression : MINUS atom %prec UMINUS"""
    p[0] = UnaryMinusNode(p[2])


def p_expression_uplus(p):
    """expression : PLUS atom %prec UMINUS"""
    p[0] = UnaryPlusNode(p[2])


# --- Matrix ---

def p_matrix_row(p):
    """matrix_row : LSQBRACKET expressions_list RSQBRACKET
    | LSQBRACKET RSQBRACKET
    """
    p[0] = p[2] if len(p) == 4 else []


def p_matrix_column_single(p):
    """matrix_column : matrix_row"""
    p[0] = [p[1]]


def p_matrix_column_multi(p):
    """matrix_column : matrix_column SEMICOLON matrix_row"""
    p[0] = p[1]
    p[0] += [p[3]]


def p_matrix(p):
    """matrix : LSQBRACKET matrix_column RSQBRACKET"""
    p[0] = MatrixNode(p[2])


# --- Helpers - expressions_list ---

def p_expressions_list_single(p):
    """expressions_list : expression"""
    p[0] = [p[1]] if p[1] is not None else []


def p_expressions_list_multi(p):
    """expressions_list : expressions_list COMMA expression"""
    p[0] = p[1]
    p[0] += [p[3]]


# --- Error ---

def p_error(p):
    if p:
        raise SyntaxError(f"Syntax error at '{p.value}'")
    raise SyntaxError("Syntax error at EOF")


_parser = yacc.yacc()


class _Parser:
    def parse(self, text, **kwargs):
        kwargs.setdefault("lexer", _lexer)
        return _parser.parse(text, **kwargs)


parser = _Parser()