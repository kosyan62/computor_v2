import pytest

from computor_v2.parsing.AST import (
    TokenNode,
    NumberNode,
    BinaryOperationNode,
    FunctionCallNode,
    MatrixNode,
    Equality,
    Unequality,
    FunctionDefinition,
)
from computor_v2.parsing.parser import parser

basic_types_test_data = [
    ("1", NumberNode(1.0)),
    ("x", TokenNode("x")),
    (
        "[[1, 2];[3,4]]",
        MatrixNode(
            [[NumberNode(1.0), NumberNode(2.0)], [NumberNode(3.0), NumberNode(4.0)]]
        ),
    ),
    ("x + 1", BinaryOperationNode(TokenNode("x"), "+", NumberNode(1.0))),
    ("f(x)", FunctionCallNode("f", [TokenNode("x")])),
    ("f(x) = 42", FunctionDefinition("f", [TokenNode("x")], NumberNode(42.0))),
    ("x = 42", Equality(TokenNode("x"), NumberNode(42.0))),
    ("x != 42", Unequality(TokenNode("x"), "!=", NumberNode(42.0))),
]

operations_test_data = [
    # Arithmetic Operators
    ("1 + 2", BinaryOperationNode(NumberNode(1.0), "+", NumberNode(2.0))),
    ("3 - 1", BinaryOperationNode(NumberNode(3.0), "-", NumberNode(1.0))),
    ("4 * 2", BinaryOperationNode(NumberNode(4.0), "*", NumberNode(2.0))),
    ("8 / 4", BinaryOperationNode(NumberNode(8.0), "/", NumberNode(4.0))),
    ("2 ^ 3", BinaryOperationNode(NumberNode(2.0), "^", NumberNode(3.0))),
    ("2 ** 3", BinaryOperationNode(NumberNode(2.0), "^", NumberNode(3.0))),
    ("5 % 2", BinaryOperationNode(NumberNode(5.0), "%", NumberNode(2.0))),
    ("9 // 4", BinaryOperationNode(NumberNode(9.0), "//", NumberNode(4.0))),
    # For token
    ("2 * x", BinaryOperationNode(NumberNode(2), "*", TokenNode("x"))),
    ("x * 2", BinaryOperationNode(TokenNode("x"), "*", NumberNode(2))),
    # Matrix
    (
        "[[1,2];[3,4]]",
        MatrixNode(
            [[NumberNode(1.0), NumberNode(2.0)], [NumberNode(3.0), NumberNode(4.0)]]
        ),
    ),
    (
        "[[1]; [2, 3, 4]]",
        MatrixNode([[NumberNode(1)], [NumberNode(2), NumberNode(3), NumberNode(4)]]),
    ),
    ("[[]]", MatrixNode([[]])),
    # Matrix operations
    (
        "[[1, 2]; [3,4]] + [[5,6]; [7,8]]",
        BinaryOperationNode(
            MatrixNode(
                [
                    [NumberNode(1.0), NumberNode(2.0)],
                    [NumberNode(3.0), NumberNode(4.0)],
                ]
            ),
            "+",
            MatrixNode(
                [
                    [NumberNode(5.0), NumberNode(6.0)],
                    [NumberNode(7.0), NumberNode(8.0)],
                ]
            ),
        ),
    ),
    (
        "[[1, 2]; [3,4]] * 2",
        BinaryOperationNode(
            MatrixNode(
                [
                    [NumberNode(1.0), NumberNode(2.0)],
                    [NumberNode(3.0), NumberNode(4.0)],
                ]
            ),
            "*",
            NumberNode(2.0),
        ),
    ),
    # Comparison Operators
    ("1 == 2", Unequality(NumberNode(1.0), "==", NumberNode(2.0))),
    ("3 != 4", Unequality(NumberNode(3.0), "!=", NumberNode(4.0))),
    ("2 > 1", Unequality(NumberNode(2.0), ">", NumberNode(1.0))),
    ("2 >= 2", Unequality(NumberNode(2.0), ">=", NumberNode(2.0))),
    ("1 < 2", Unequality(NumberNode(1.0), "<", NumberNode(2.0))),
    ("2 <= 3", Unequality(NumberNode(2.0), "<=", NumberNode(3.0))),
    # Function calls
    ("f()", FunctionCallNode("f", [])),
    ("f(1)", FunctionCallNode("f", [NumberNode(1.0)])),
    ("f((1))", FunctionCallNode("f", [NumberNode(1.0)])),
    (
        "f(-(1))",
        FunctionCallNode(
            "f", [BinaryOperationNode(NumberNode(-1.0), "*", NumberNode(1.0))]
        ),
    ),
    (
        "max(1, 2, 3)",
        FunctionCallNode("max", [NumberNode(1.0), NumberNode(2.0), NumberNode(3.0)]),
    ),
    # Function calls for tokens
    ("f(x)", FunctionCallNode("f", [TokenNode("x")])),
    ("f((x))", FunctionCallNode("f", [TokenNode("x")])),
    ("g(x, 42)", FunctionCallNode("g", [TokenNode("x"), NumberNode(42.0)])),
    ("f(x, y)", FunctionCallNode("f", [TokenNode("x"), TokenNode("y")])),
    (
        "f(x + y)",
        FunctionCallNode(
            "f", [BinaryOperationNode(TokenNode("x"), "+", TokenNode("y"))]
        ),
    ),
    (
        "f([[1,2];[3,4]])",
        FunctionCallNode(
            "f",
            [
                MatrixNode(
                    [
                        [NumberNode(1.0), NumberNode(2.0)],
                        [NumberNode(3.0), NumberNode(4.0)],
                    ]
                )
            ],
        ),
    ),
    (
        "f([[1,2];[3,4]],[[6,7];[8,9]])",
        FunctionCallNode(
            "f",
            [
                MatrixNode(
                    [
                        [NumberNode(1.0), NumberNode(2.0)],
                        [NumberNode(3.0), NumberNode(4.0)],
                    ]
                ),
                MatrixNode(
                    [
                        [NumberNode(6.0), NumberNode(7.0)],
                        [NumberNode(8.0), NumberNode(9.0)],
                    ]
                ),
            ],
        ),
    ),
    # Function definition
    ("f(x) = 42", FunctionDefinition("f", [TokenNode("x")], NumberNode(42.0))),
    ("f() = 42", FunctionDefinition("f", [], NumberNode(42.0))),
    (
        "f(x, y) = 42",
        FunctionDefinition("f", [TokenNode("x"), TokenNode("y")], NumberNode(42.0)),
    ),
    (
        "f(x) = 2 * x",
        FunctionDefinition(
            "f",
            [TokenNode("x")],
            BinaryOperationNode(NumberNode(2.0), "*", TokenNode("x")),
        ),
    ),
    # Unary minus
    ("-3", BinaryOperationNode(NumberNode(-1.0), "*", NumberNode(3.0))),
    (
        "-f(x)",
        BinaryOperationNode(
            NumberNode(-1.0), "*", FunctionCallNode("f", [TokenNode("x")])
        ),
    ),
    (
        "- (1 + 2)",
        BinaryOperationNode(
            NumberNode(-1.0),
            "*",
            BinaryOperationNode(NumberNode(1.0), "+", NumberNode(2.0)),
        ),
    ),
    (
        "--3",
        BinaryOperationNode(
            NumberNode(-1),
            "*",
            BinaryOperationNode(NumberNode(-1.0), "*", NumberNode(3.0)),
        ),
    ),
    (
        "---3",
        BinaryOperationNode(
            NumberNode(-1.0),
            "*",
            BinaryOperationNode(
                NumberNode(-1.0),
                "*",
                BinaryOperationNode(NumberNode(-1.0), "*", NumberNode(3.0)),
            ),
        ),
    ),
    # Simple assignment
    ("a = 4", Equality(TokenNode("a"), NumberNode(4))),  # Matrix
    (
        "a = 1 + x",
        Equality(
            TokenNode("a"), BinaryOperationNode(NumberNode(1.0), "+", TokenNode("x"))
        ),
    ),
    # Some edge case tests
    ("((((((1 + 2))))))", BinaryOperationNode(NumberNode(1.0), "+", NumberNode(2))),
    # Float literals
    ("4.242", NumberNode(4.242)),
    ("0.5", NumberNode(0.5)),
    # Matrix assignment
    (
        "m = [[1,2];[3,4]]",
        Equality(
            TokenNode("m"),
            MatrixNode([[NumberNode(1.0), NumberNode(2.0)], [NumberNode(3.0), NumberNode(4.0)]]),
        ),
    ),
    # Assignment to function call result
    ("x = f(2)", Equality(TokenNode("x"), FunctionCallNode("f", [NumberNode(2.0)]))),
    # Equation form: expr = expr (both sides non-trivial)
    (
        "x + 1 = 2 * x",
        Equality(
            BinaryOperationNode(TokenNode("x"), "+", NumberNode(1.0)),
            BinaryOperationNode(NumberNode(2.0), "*", TokenNode("x")),
        ),
    ),
    # Modulo with token operands
    ("x % 2", BinaryOperationNode(TokenNode("x"), "%", NumberNode(2.0))),
    ("a % b", BinaryOperationNode(TokenNode("a"), "%", TokenNode("b"))),
    # Column vector (single-column matrix)
    (
        "[[1];[2];[3]]",
        MatrixNode([[NumberNode(1.0)], [NumberNode(2.0)], [NumberNode(3.0)]]),
    ),
    # Single-element matrix
    ("[[5]]", MatrixNode([[NumberNode(5.0)]])),
]

operation_order_test_data = [
    # Basic precedence
    (
        "1 + 2 * 3",
        BinaryOperationNode(
            NumberNode(1), "+", BinaryOperationNode(NumberNode(2), "*", NumberNode(3))
        ),
    ),
    (
        "(1 + 2) * 3",
        BinaryOperationNode(
            BinaryOperationNode(NumberNode(1), "+", NumberNode(2)), "*", NumberNode(3)
        ),
    ),
    (
        "2 ^ 3 * 4",
        BinaryOperationNode(
            BinaryOperationNode(NumberNode(2), "^", NumberNode(3)), "*", NumberNode(4)
        ),
    ),
    (
        "-2 ^ 3",
        BinaryOperationNode(
            NumberNode(-1.0),
            "*",
            BinaryOperationNode(NumberNode(2), "^", NumberNode(3)),
        ),
    ),
    (
        "4 + 2 ^ 2 * 3",
        BinaryOperationNode(
            NumberNode(4),
            "+",
            BinaryOperationNode(
                BinaryOperationNode(NumberNode(2), "^", NumberNode(2)),
                "*",
                NumberNode(3),
            ),
        ),
    ),
    (
        "3 * 2 + 1",
        BinaryOperationNode(
            BinaryOperationNode(NumberNode(3), "*", NumberNode(2)), "+", NumberNode(1)
        ),
    ),
    (
        "2 + 3 - 1",
        BinaryOperationNode(
            BinaryOperationNode(NumberNode(2), "+", NumberNode(3)), "-", NumberNode(1)
        ),
    ),
    (
        "8 / 4 / 2",
        BinaryOperationNode(
            BinaryOperationNode(NumberNode(8), "/", NumberNode(4)), "/", NumberNode(2)
        ),
    ),
    (
        "2 ^ 3 ^ 2",
        BinaryOperationNode(
            NumberNode(2), "^", BinaryOperationNode(NumberNode(3), "^", NumberNode(2))
        ),
    ),
    # Modulo binds tighter than + (same level as * and /)
    (
        "1 + 5 % 3",
        BinaryOperationNode(
            NumberNode(1.0), "+", BinaryOperationNode(NumberNode(5.0), "%", NumberNode(3.0))
        ),
    ),
    (
        "5 % 3 + 1",
        BinaryOperationNode(
            BinaryOperationNode(NumberNode(5.0), "%", NumberNode(3.0)), "+", NumberNode(1.0)
        ),
    ),
    # FLOORDIV binds tighter than +
    (
        "1 + 8 // 4",
        BinaryOperationNode(
            NumberNode(1.0), "+", BinaryOperationNode(NumberNode(8.0), "//", NumberNode(4.0))
        ),
    ),
    (
        "8 // 4 - 1",
        BinaryOperationNode(
            BinaryOperationNode(NumberNode(8.0), "//", NumberNode(4.0)), "-", NumberNode(1.0)
        ),
    ),
]

@pytest.mark.parametrize("test_input,expected", basic_types_test_data)
def test_basic_types(test_input, expected):
    result = parser.parse(test_input)
    assert result == expected


@pytest.mark.parametrize("test_input,expected", operations_test_data)
def test_operations(test_input, expected):
    result = parser.parse(test_input)
    assert result == expected


@pytest.mark.parametrize("test_input,expected", operation_order_test_data)
def test_operations_order(test_input, expected):
    result = parser.parse(test_input)
    assert result == expected


def test_polynomial():
    ax_squared = parser.parse("2*x^2")
    assert ax_squared == BinaryOperationNode(
            NumberNode(2.0), "*", BinaryOperationNode(TokenNode("x"), "^", NumberNode(2.0))
    )
    bx = parser.parse("3*x")
    assert bx == BinaryOperationNode(
        NumberNode(3.0), "*", TokenNode("x")
    )
    c = parser.parse("4")
    assert c == NumberNode(4.0)
    ax_squared_plus_bx_minus_c = parser.parse("2*x^2 + 3*x - 4")
    assert ax_squared_plus_bx_minus_c == BinaryOperationNode(
        BinaryOperationNode(ax_squared, "+", bx), "-", c)
    polynomial_expression = parser.parse("2*x^2 + 3*x - 4 = 0")
    assert polynomial_expression == Equality(ax_squared_plus_bx_minus_c, NumberNode(0.0))
