from .AST import (
    NumberNode,
    TokenNode,
    BinaryOperationNode,
    FunctionCallNode,
    FunctionDefinition,
    MatrixNode,
    Equality,
    Unequality,
)
from ply import yacc
from .lexer import tokens, lexer as _base_lexer, ImplicitMultiplyLexer  # noqa F401

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


def p_statement_assignment(p):
    """statement : equality
    | unequality
    | expression
    | function_definition
    """
    p[0] = p[1]


def p_function_definition(p):
    """function_definition : ID LPAREN expressions_list RPAREN ASSIGNMENT expression
    | ID LPAREN RPAREN ASSIGNMENT expression
    """
    function_name = p[1]
    if len(p) == 7:
        parameters, body = p[3], p[6]
    elif len(p) == 6:
        parameters, body = [], p[5]
    else:
        raise SyntaxError("Invalid function definition")

    p[0] = FunctionDefinition(function_name, parameters, body)


def p_function_call(p):
    """function_call : ID LPAREN expressions_list RPAREN
    | ID LPAREN RPAREN
    """
    if len(p) == 5:
        p[0] = FunctionCallNode(p[1], p[3])
    elif len(p) == 4:
        p[0] = FunctionCallNode(p[1], [])
    else:
        raise SyntaxError("Invalid function call")


def p_expressions_list_single(p):
    """expressions_list : expression"""
    p[0] = [p[1]] if p[1] is not None else []


def p_expressions_list_multi(p):
    """expressions_list : expressions_list COMMA expression"""
    p[0] = p[1]
    p[0] += [p[3]]


def p_matrix_row(p):
    """matrix_row : LSQBRACKET expressions_list RSQBRACKET
    | LSQBRACKET RSQBRACKET
    """
    if len(p) == 4:
        p[0] = p[2]
    elif len(p) == 3:
        p[0] = []
    else:
        raise SyntaxError("Invalid matrix row")


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


def p_equality(p):
    """equality : ID ASSIGNMENT expression
    | expression ASSIGNMENT expression"""
    left, right = p[1], p[3]
    if isinstance(left, str):
        left = TokenNode(left)
    if isinstance(right, str):
        right = TokenNode(right)
    p[0] = Equality(left, right)


def p_expression_function_call(p):
    """expression : function_call"""
    p[0] = p[1]


def p_expression_unequality(p):
    """unequality : expression GT expression
    | expression GTE expression
    | expression LT expression
    | expression LTE expression
    | expression EQ expression
    | expression NEQ expression
    """
    p[0] = Unequality(p[1], p[2], p[3])


def p_expression_binary_expression(p):
    """expression : expression PLUS expression
    | expression MINUS expression
    | expression MULTIPLY expression
    | expression MATMUL expression
    | expression DIVIDE expression
    | expression POWER expression
    | expression MODULO expression
    | expression FLOORDIV expression
    """
    p[0] = BinaryOperationNode(p[1], p[2], p[3])


def p_expression_uminus(p):
    """expression : MINUS expression %prec UMINUS"""
    p[0] = BinaryOperationNode(NumberNode(-1.0), "*", p[2])


def p_expression_number(p):
    """expression : NUMBER"""
    p[0] = NumberNode(p[1])


def p_expression_variable(p):
    """expression : ID"""
    p[0] = TokenNode(p[1])


def p_expression_matrix(p):
    """expression : matrix"""
    p[0] = p[1]


def p_expression_group(p):
    """expression : LPAREN expression RPAREN"""
    p[0] = p[2]


def p_error(p):
    if p:
        message = f"Syntax error at '{p.value}'"
        raise SyntaxError(message)
    else:
        message = "Syntax error at EOF"
        raise SyntaxError(message)


_parser = yacc.yacc()


class _Parser:
    def parse(self, text, **kwargs):
        kwargs.setdefault("lexer", _lexer)
        return _parser.parse(text, **kwargs)


parser = _Parser()
