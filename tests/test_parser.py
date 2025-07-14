import pytest

from computor_v2.parsing.AST import (
    TokenNode,
    NumberNode,
    BinaryOperationNode,
    FunctionCallNode,
    MatrixNode,
    Equality,
    Unequality,
)
from computor_v2.parsing.parser import parser

test_data = [
    ("1 + 2", BinaryOperationNode(NumberNode(1.0), "+", NumberNode(2.0))),
    ("((((((1 + 2))))))", BinaryOperationNode(NumberNode(1.0), "+", NumberNode(2))),
    # Arithmetic Operators
    ("3 - 1", BinaryOperationNode(NumberNode(3.0), "-", NumberNode(1.0))),
    ("4 * 2", BinaryOperationNode(NumberNode(4.0), "*", NumberNode(2.0))),
    ("8 / 4", BinaryOperationNode(NumberNode(8.0), "/", NumberNode(4.0))),
    ("2 ^ 3", BinaryOperationNode(NumberNode(2.0), "^", NumberNode(3.0))),
    ("5 % 2", BinaryOperationNode(NumberNode(5.0), "%", NumberNode(2.0))),
    ("9 // 4", BinaryOperationNode(NumberNode(9.0), "//", NumberNode(4.0))),
    # Comparison Operators
    ("1 == 2", Unequality(NumberNode(1.0), "==", NumberNode(2.0))),
    ("3 != 4", Unequality(NumberNode(3.0), "!=", NumberNode(4.0))),
    ("2 > 1", Unequality(NumberNode(2.0), ">", NumberNode(1.0))),
    ("2 >= 2", Unequality(NumberNode(2.0), ">=", NumberNode(2.0))),
    ("1 < 2", Unequality(NumberNode(1.0), "<", NumberNode(2.0))),
    ("2 <= 3", Unequality(NumberNode(2.0), "<=", NumberNode(3.0))),
    # Unary minus
    ("-3", BinaryOperationNode(NumberNode(-1.0), "*", NumberNode(3.0))),
    # Implicit multiplication
    ("2x", BinaryOperationNode(NumberNode(2.0), "*", TokenNode("x"))),
    (
        "2f(x)",
        BinaryOperationNode(
            NumberNode(2.0), "*", FunctionCallNode("f", [TokenNode("x")])
        ),
    ),
    # Function calls
    ("f(x)", FunctionCallNode("f", [TokenNode("x")])),
    (
        "max(1, 2, 3)",
        FunctionCallNode("max", [NumberNode(1.0), NumberNode(2.0), NumberNode(3.0)]),
    ),
    # Assignment
    ("a = 4", Equality("a", NumberNode(4))),
    # Matrix
    (
        "[[1, 2]; [3, 4]]",
        MatrixNode(
            [[NumberNode(1.0), NumberNode(2.0)], [NumberNode(3.0), NumberNode(4.0)]]
        ),
    ),
    # Basic expressions
    ("1 + 2", BinaryOperationNode(NumberNode(1.0), "+", NumberNode(2.0))),
    ("((((((1 + 2))))))", BinaryOperationNode(NumberNode(1.0), "+", NumberNode(2.0))),
    ("2 * x", BinaryOperationNode(NumberNode(2), "*", TokenNode("x"))),
    # New test cases for implicit multiply
    ("2x", BinaryOperationNode(NumberNode(2), "*", TokenNode("x"))),
    (
        "2f(x)",
        BinaryOperationNode(
            NumberNode(2), "*", FunctionCallNode("f", [TokenNode("x")])
        ),
    ),
]


@pytest.mark.parametrize("test_input,expected", test_data)
def test_parse(test_input, expected):
    result = parser.parse(test_input)
    assert result == expected
