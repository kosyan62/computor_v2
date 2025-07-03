from parsing.lexer import tokens
from ply import yacc
from parsing.AST import *


# Parsing rules
precedence = (
        ('left', 'MODULO'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULTIPLY', 'DIVIDE'),
        ('right', 'POWER'),
        ('right', 'UMINUS'),
        ('left', 'GT', 'GTE', 'LT', 'LTE', 'EQ', 'NEQ')
    )


start = "statement"


def p_statement_assignment(p):
    """statement : assignment
                 | function_definition
                 | expression
                 """
    p[0] = p[1]

def p_function_definition(p):
    """function_definition : ID LPAREN expressions_list RPAREN ASSIGNMENT expression"""
    pass
    p[0] = p[1]


def p_expressions_list_1(p):
    """expressions_list : expression"""
    p[0] = [p[1]]


def p_expressions_list_2(p):
    """expressions_list : expressions_list COMMA expression"""
    p[0] = p[1]
    p[0] += [p[3]]

def p_matrix_row(p):
    """matrix_row : LSQBRACKET expressions_list RSQBRACKET"""
    p[0] = p[2]

def p_matrix_column_1(p):
    """matrix_column : matrix_row"""
    p[0] = [p[1]]

def p_matrix_column_2(p):
    """matrix_column : matrix_column SEMICOLON matrix_row"""
    p[0] = p[1]
    p[0] += [p[3]]

def p_matrix(p):
    """matrix : LSQBRACKET matrix_column RSQBRACKET"""
    p[0] = MatrixNode(p[2])

def p_assignment(p):
    """assignment : ID ASSIGNMENT expression"""
    p[0] = TokenNode(p[1], p[3])


def p_expression_binary_expression(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression MULTIPLY expression
                  | expression DIVIDE expression
                  | expression POWER expression
                  | expression MODULO expression
                  | expression FLOORDIV expression
                  | expression GT expression
                  | expression GTE expression
                  | expression LT expression
                  | expression LTE expression
                  | expression EQ expression
                  | expression NEQ expression
                  """
    p[0] = BinaryOperationNode(p[1], p[2], p[3])


def p_expression_uminus(p):
    """expression : MINUS expression %prec UMINUS"""
    p[0] = NumberNode(-p[2].leaf)


def p_expression_number(p):
    """expression : NUMBER"""
    p[0] = NumberNode(p[1])


def p_expression_variable(p):
    """expression : ID"""
    p[0] = TokenNode(p[1])


def p_expression_matrix(p):
    """expression : matrix"""
    p[0] = TokenNode(p[1])


def p_expression_function_call(p):
    """expression : ID LPAREN expressions_list RPAREN"""
    p[0] = FunctionCallNode(p[1], p[3])


def p_expression_group(p):
    """expression : LPAREN expression RPAREN"""
    p[0] = p[2]


def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")


parser = yacc.yacc()
