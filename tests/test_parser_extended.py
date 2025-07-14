import pytest

from computor_v2.parsing.AST import (
    FunctionDefinition,
    FunctionCallNode,
    BinaryOperationNode,
    NumberNode,
    TokenNode,
    MatrixNode,
)
from computor_v2.parsing.parser import parser

valid_test_data = [
    # Nested function calls
    ("f(g(x))", FunctionCallNode("f", [FunctionCallNode("g", [TokenNode("x")])])),
    # Function calls with multiply
    (
        "f(x, y * z)",
        FunctionCallNode(
            "f",
            [TokenNode("x"), BinaryOperationNode(TokenNode("y"), "*", TokenNode("z"))],
        ),
    ),
    # Function call with matrix and number
    (
        "f(2, [[1, 2]])",
        FunctionCallNode(
            "f", [NumberNode(2.0), MatrixNode([[NumberNode(1.0), NumberNode(2.0)]])]
        ),
    ),
    # Matrix with expressions
    (
        "[[1+2, 2*3]; [4^2, 5-3]]",
        MatrixNode(
            [
                [
                    BinaryOperationNode(NumberNode(1.0), "+", NumberNode(2.0)),
                    BinaryOperationNode(NumberNode(2.0), "*", NumberNode(3.0)),
                ],
                [
                    BinaryOperationNode(NumberNode(4.0), "^", NumberNode(2.0)),
                    BinaryOperationNode(NumberNode(5.0), "-", NumberNode(3.0)),
                ],
            ]
        ),
    ),
    # Function definition: simple
    (
        "f(x) = x + 1",
        FunctionDefinition(
            "f", [TokenNode("x")], BinaryOperationNode(TokenNode("x"), "+", NumberNode(1.0))
        ),
    ),
    # Function with multiple arguments
    (
        "max(a, b, c) = a + b + c",
        FunctionDefinition(
            "max",
            [TokenNode("a"), TokenNode("b"), TokenNode("c")],
            BinaryOperationNode(
                BinaryOperationNode(TokenNode("a"), "+", TokenNode("b")),
                "+",
                TokenNode("c"),
            ),
        ),
    ),
    # Function with matrix return
    (
        "m() = [[1, 2]; [3, 4]]",
        FunctionDefinition(
            "m",
            [],
            TokenNode(
                MatrixNode(
                    [
                        [NumberNode(1.0), NumberNode(2.0)],
                        [NumberNode(3.0), NumberNode(4.0)],
                    ]
                )
            ),
        ),
    ),
    # Function with nested function call
    (
        "f(x) = g(x) + 1",
        FunctionDefinition(
            "f",
            1,
            BinaryOperationNode(
                FunctionCallNode("g", [TokenNode("x")]), "+", NumberNode(1.0)
            ),
        ),
    ),
    # Multiple expressions in function args
    (
        "f(1 + 2, 3 * 4)",
        FunctionCallNode(
            "f",
            [
                BinaryOperationNode(NumberNode(1.0), "+", NumberNode(2.0)),
                BinaryOperationNode(NumberNode(3.0), "*", NumberNode(4.0)),
            ],
        ),
    ),
    # Parenthesized matrix
    (
        "([[1, 2]; [3, 4]])",
        MatrixNode(
            [[NumberNode(1.0), NumberNode(2.0)], [NumberNode(3.0), NumberNode(4.0)]]
        ),
    ),
    # Chained comparisons
    (
        "1 < 2 <= 3",
        BinaryOperationNode(
            BinaryOperationNode(NumberNode(1.0), "<", NumberNode(2.0)),
            "<=",
            NumberNode(3.0),
        ),
    ),
]


@pytest.mark.parametrize("test_input,expected", valid_test_data)
def test_valid_parse(test_input, expected):
    result = parser.parse(test_input)
    assert result == expected


invalid_inputs = [
    "1 +",
    "(",
    "f(x",
    "[1, 2]",
    "1 ** 2",
    "f(1, , 2)",
]


@pytest.mark.parametrize("test_input", invalid_inputs)
def test_invalid_parse(test_input):
    with pytest.raises(SyntaxError):
        parser.parse(test_input)
