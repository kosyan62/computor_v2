import pytest

from computor_v2.parsing.AST import (
    VariableNode,
    NumberNode,
    UnaryMinusNode,
    UnaryPlusNode,
    BinaryOperationNode,
    FunctionCallNode,
    MatrixNode,
    Equality,
    ComparisonNode,
    FunctionDefinitionNode,
    QueryNode,
    SolveNode,
)
from computor_v2.parsing.parser import parser

N = NumberNode  # shorthand

basic_types_test_data = [
    ("1", N("1")),
    ("x", VariableNode("x")),
    (
        "[[1, 2];[3,4]]",
        MatrixNode([[N("1"), N("2")], [N("3"), N("4")]]),
    ),
    ("x + 1", BinaryOperationNode(VariableNode("x"), "+", N("1"))),
    ("f(x)", FunctionCallNode("f", [VariableNode("x")])),
    ("f(x) = 42", FunctionDefinitionNode("f", [VariableNode("x")], N("42"))),
    ("x = 42", Equality(VariableNode("x"), N("42"))),
    ("x != 42", ComparisonNode(VariableNode("x"), "!=", N("42"))),
]

operations_test_data = [
    # Arithmetic
    ("1 + 2", BinaryOperationNode(N("1"), "+", N("2"))),
    ("3 - 1", BinaryOperationNode(N("3"), "-", N("1"))),
    ("4 * 2", BinaryOperationNode(N("4"), "*", N("2"))),
    ("8 / 4", BinaryOperationNode(N("8"), "/", N("4"))),
    ("2 ^ 3", BinaryOperationNode(N("2"), "^", N("3"))),
    (
        "[[1,2];[3,4]] ** [[5,6];[7,8]]",
        BinaryOperationNode(
            MatrixNode([[N("1"), N("2")], [N("3"), N("4")]]),
            "**",
            MatrixNode([[N("5"), N("6")], [N("7"), N("8")]]),
        ),
    ),
    ("5 % 2", BinaryOperationNode(N("5"), "%", N("2"))),
    ("9 // 4", BinaryOperationNode(N("9"), "//", N("4"))),
    # Variables
    ("2 * x", BinaryOperationNode(N("2"), "*", VariableNode("x"))),
    ("x * 2", BinaryOperationNode(VariableNode("x"), "*", N("2"))),
    # Matrix
    ("[[1,2];[3,4]]", MatrixNode([[N("1"), N("2")], [N("3"), N("4")]])),
    (
        "[[1]; [2, 3, 4]]",
        MatrixNode([[N("1")], [N("2"), N("3"), N("4")]]),
    ),
    ("[[]]", MatrixNode([[]])),
    # Matrix operations
    (
        "[[1, 2]; [3,4]] + [[5,6]; [7,8]]",
        BinaryOperationNode(
            MatrixNode([[N("1"), N("2")], [N("3"), N("4")]]),
            "+",
            MatrixNode([[N("5"), N("6")], [N("7"), N("8")]]),
        ),
    ),
    (
        "[[1, 2]; [3,4]] * 2",
        BinaryOperationNode(
            MatrixNode([[N("1"), N("2")], [N("3"), N("4")]]),
            "*",
            N("2"),
        ),
    ),
    # Comparison
    ("1 == 2", ComparisonNode(N("1"), "==", N("2"))),
    ("3 != 4", ComparisonNode(N("3"), "!=", N("4"))),
    ("2 > 1", ComparisonNode(N("2"), ">", N("1"))),
    ("2 >= 2", ComparisonNode(N("2"), ">=", N("2"))),
    ("1 < 2", ComparisonNode(N("1"), "<", N("2"))),
    ("2 <= 3", ComparisonNode(N("2"), "<=", N("3"))),
    # Function calls
    ("f()", FunctionCallNode("f", [])),
    ("f(1)", FunctionCallNode("f", [N("1")])),
    ("f((1))", FunctionCallNode("f", [N("1")])),
    (
        "f(-(1))",
        FunctionCallNode("f", [UnaryMinusNode(N("1"))]),
    ),
    (
        "max(1, 2, 3)",
        FunctionCallNode("max", [N("1"), N("2"), N("3")]),
    ),
    ("f(x)", FunctionCallNode("f", [VariableNode("x")])),
    ("f((x))", FunctionCallNode("f", [VariableNode("x")])),
    ("g(x, 42)", FunctionCallNode("g", [VariableNode("x"), N("42")])),
    ("f(x, y)", FunctionCallNode("f", [VariableNode("x"), VariableNode("y")])),
    (
        "f(x + y)",
        FunctionCallNode("f", [BinaryOperationNode(VariableNode("x"), "+", VariableNode("y"))]),
    ),
    (
        "f([[1,2];[3,4]])",
        FunctionCallNode("f", [MatrixNode([[N("1"), N("2")], [N("3"), N("4")]])]),
    ),
    (
        "f([[1,2];[3,4]],[[6,7];[8,9]])",
        FunctionCallNode(
            "f",
            [
                MatrixNode([[N("1"), N("2")], [N("3"), N("4")]]),
                MatrixNode([[N("6"), N("7")], [N("8"), N("9")]]),
            ],
        ),
    ),
    # Function definition
    ("f(x) = 42", FunctionDefinitionNode("f", [VariableNode("x")], N("42"))),
    ("f() = 42", FunctionDefinitionNode("f", [], N("42"))),
    (
        "f(x, y) = 42",
        FunctionDefinitionNode("f", [VariableNode("x"), VariableNode("y")], N("42")),
    ),
    (
        "f(x) = 2 * x",
        FunctionDefinitionNode(
            "f",
            [VariableNode("x")],
            BinaryOperationNode(N("2"), "*", VariableNode("x")),
        ),
    ),
    # Unary minus
    ("-3", UnaryMinusNode(N("3"))),
    ("-f(x)", UnaryMinusNode(FunctionCallNode("f", [VariableNode("x")]))),
    ("- (1 + 2)", UnaryMinusNode(BinaryOperationNode(N("1"), "+", N("2")))),
    ("-(-3)", UnaryMinusNode(UnaryMinusNode(N("3")))),
    ("-(-(x))", UnaryMinusNode(UnaryMinusNode(VariableNode("x")))),
    # Assignment
    ("a = 4", Equality(VariableNode("a"), N("4"))),
    (
        "a = 1 + x",
        Equality(VariableNode("a"), BinaryOperationNode(N("1"), "+", VariableNode("x"))),
    ),
    # Edge cases
    ("((((((1 + 2))))))", BinaryOperationNode(N("1"), "+", N("2"))),
    # Float literals
    ("4.242", N("4.242")),
    ("0.5", N("0.5")),
    # Matrix assignment
    (
        "m = [[1,2];[3,4]]",
        Equality(VariableNode("m"), MatrixNode([[N("1"), N("2")], [N("3"), N("4")]])),
    ),
    ("x = f(2)", Equality(VariableNode("x"), FunctionCallNode("f", [N("2")]))),
    # Equation form
    (
        "x + 1 = 2 * x",
        Equality(
            BinaryOperationNode(VariableNode("x"), "+", N("1")),
            BinaryOperationNode(N("2"), "*", VariableNode("x")),
        ),
    ),
    # Modulo
    ("x % 2", BinaryOperationNode(VariableNode("x"), "%", N("2"))),
    ("a % b", BinaryOperationNode(VariableNode("a"), "%", VariableNode("b"))),
    # Column vector
    ("[[1];[2];[3]]", MatrixNode([[N("1")], [N("2")], [N("3")]])),
    # Single-element matrix
    ("[[5]]", MatrixNode([[N("5")]])),
    # Unary minus in assignment
    ("x = -3", Equality(VariableNode("x"), UnaryMinusNode(N("3")))),
    # Power in assignment
    ("x = 2 ^ 3", Equality(VariableNode("x"), BinaryOperationNode(N("2"), "^", N("3")))),
    # Nested function calls
    ("f(g(x))", FunctionCallNode("f", [FunctionCallNode("g", [VariableNode("x")])])),
    ("f(f(x))", FunctionCallNode("f", [FunctionCallNode("f", [VariableNode("x")])])),
    (
        "f(x) = g(x)",
        FunctionDefinitionNode("f", [VariableNode("x")], FunctionCallNode("g", [VariableNode("x")])),
    ),
    # Grouped expressions
    (
        "(x + 1) * (x - 1)",
        BinaryOperationNode(
            BinaryOperationNode(VariableNode("x"), "+", N("1")),
            "*",
            BinaryOperationNode(VariableNode("x"), "-", N("1")),
        ),
    ),
    # Matrix with expressions
    (
        "[[1+2, 2*3]; [4^2, 5-3]]",
        MatrixNode([
            [BinaryOperationNode(N("1"), "+", N("2")), BinaryOperationNode(N("2"), "*", N("3"))],
            [BinaryOperationNode(N("4"), "^", N("2")), BinaryOperationNode(N("5"), "-", N("3"))],
        ]),
    ),
    # Matrix in parens
    (
        "([[1, 2]; [3, 4]])",
        MatrixNode([[N("1"), N("2")], [N("3"), N("4")]]),
    ),
    # Triple nesting
    (
        "f(g(h(x)))",
        FunctionCallNode("f", [FunctionCallNode("g", [FunctionCallNode("h", [VariableNode("x")])])]),
    ),
    # Uppercase
    ("X = 1", Equality(VariableNode("X"), N("1"))),
    ("VarA", VariableNode("VarA")),
    # Multi-arg function definition
    (
        "sum(a, b, c) = a + b + c",
        FunctionDefinitionNode(
            "sum",
            [VariableNode("a"), VariableNode("b"), VariableNode("c")],
            BinaryOperationNode(
                BinaryOperationNode(VariableNode("a"), "+", VariableNode("b")),
                "+",
                VariableNode("c"),
            ),
        ),
    ),
    # Function returning matrix
    (
        "m() = [[1, 2]; [3, 4]]",
        FunctionDefinitionNode("m", [], MatrixNode([[N("1"), N("2")], [N("3"), N("4")]])),
    ),
    (
        "f(x) = g(x) + 1",
        FunctionDefinitionNode(
            "f",
            [VariableNode("x")],
            BinaryOperationNode(FunctionCallNode("g", [VariableNode("x")]), "+", N("1")),
        ),
    ),
    (
        "f(x) = x^2",
        FunctionDefinitionNode(
            "f", [VariableNode("x")], BinaryOperationNode(VariableNode("x"), "^", N("2"))
        ),
    ),
    (
        "f(-x)",
        FunctionCallNode("f", [UnaryMinusNode(VariableNode("x"))]),
    ),
    (
        "f(1 + 2, 3 * 4)",
        FunctionCallNode(
            "f",
            [BinaryOperationNode(N("1"), "+", N("2")), BinaryOperationNode(N("3"), "*", N("4"))],
        ),
    ),
    (
        "f(x * 2 + 1)",
        FunctionCallNode(
            "f",
            [BinaryOperationNode(BinaryOperationNode(VariableNode("x"), "*", N("2")), "+", N("1"))],
        ),
    ),
    (
        "f(x, y * z)",
        FunctionCallNode(
            "f",
            [VariableNode("x"), BinaryOperationNode(VariableNode("y"), "*", VariableNode("z"))],
        ),
    ),
    (
        "f(2, [[1, 2]])",
        FunctionCallNode("f", [N("2"), MatrixNode([[N("1"), N("2")]])]),
    ),
]

operation_order_test_data = [
    ("1 + 2 * 3", BinaryOperationNode(N("1"), "+", BinaryOperationNode(N("2"), "*", N("3")))),
    ("(1 + 2) * 3", BinaryOperationNode(BinaryOperationNode(N("1"), "+", N("2")), "*", N("3"))),
    (
        "2 ^ 3 * 4",
        BinaryOperationNode(BinaryOperationNode(N("2"), "^", N("3")), "*", N("4")),
    ),
    (
        "-2 ^ 3",
        UnaryMinusNode(BinaryOperationNode(N("2"), "^", N("3"))),
    ),
    (
        "4 + 2 ^ 2 * 3",
        BinaryOperationNode(
            N("4"),
            "+",
            BinaryOperationNode(BinaryOperationNode(N("2"), "^", N("2")), "*", N("3")),
        ),
    ),
    ("3 * 2 + 1", BinaryOperationNode(BinaryOperationNode(N("3"), "*", N("2")), "+", N("1"))),
    ("2 + 3 - 1", BinaryOperationNode(BinaryOperationNode(N("2"), "+", N("3")), "-", N("1"))),
    ("8 / 4 / 2", BinaryOperationNode(BinaryOperationNode(N("8"), "/", N("4")), "/", N("2"))),
    (
        "2 ^ 3 ^ 2",
        BinaryOperationNode(N("2"), "^", BinaryOperationNode(N("3"), "^", N("2"))),
    ),
    # Modulo
    ("1 + 5 % 3", BinaryOperationNode(N("1"), "+", BinaryOperationNode(N("5"), "%", N("3")))),
    ("5 % 3 + 1", BinaryOperationNode(BinaryOperationNode(N("5"), "%", N("3")), "+", N("1"))),
    # FloorDiv
    ("1 + 8 // 4", BinaryOperationNode(N("1"), "+", BinaryOperationNode(N("8"), "//", N("4")))),
    ("8 // 4 - 1", BinaryOperationNode(BinaryOperationNode(N("8"), "//", N("4")), "-", N("1"))),
    # -x^2 = -(x^2)
    ("-x^2", UnaryMinusNode(BinaryOperationNode(VariableNode("x"), "^", N("2")))),
    # x^-2 = x^(-(2))
    ("x^-2", BinaryOperationNode(VariableNode("x"), "^", UnaryMinusNode(N("2")))),
    (
        "x * y + z",
        BinaryOperationNode(BinaryOperationNode(VariableNode("x"), "*", VariableNode("y")), "+", VariableNode("z")),
    ),
    (
        "x + y * z",
        BinaryOperationNode(VariableNode("x"), "+", BinaryOperationNode(VariableNode("y"), "*", VariableNode("z"))),
    ),
    (
        "1 + 2 + 3",
        BinaryOperationNode(BinaryOperationNode(N("1"), "+", N("2")), "+", N("3")),
    ),
    (
        "1 / 2 / 4",
        BinaryOperationNode(BinaryOperationNode(N("1"), "/", N("2")), "/", N("4")),
    ),
]

implicit_multiply_test_data = [
    ("2x", BinaryOperationNode(N("2"), "*", VariableNode("x"))),
    ("2 x", BinaryOperationNode(N("2"), "*", VariableNode("x"))),
    ("3.14x", BinaryOperationNode(N("3.14"), "*", VariableNode("x"))),
    (
        "2(x + 1)",
        BinaryOperationNode(N("2"), "*", BinaryOperationNode(VariableNode("x"), "+", N("1"))),
    ),
    # 2x^2 = 2*(x^2)
    (
        "2x^2",
        BinaryOperationNode(N("2"), "*", BinaryOperationNode(VariableNode("x"), "^", N("2"))),
    ),
    (
        "2x + 3",
        BinaryOperationNode(BinaryOperationNode(N("2"), "*", VariableNode("x")), "+", N("3")),
    ),
    (
        "2x + 3y",
        BinaryOperationNode(
            BinaryOperationNode(N("2"), "*", VariableNode("x")),
            "+",
            BinaryOperationNode(N("3"), "*", VariableNode("y")),
        ),
    ),
    (
        "2x^2 + 3x",
        BinaryOperationNode(
            BinaryOperationNode(N("2"), "*", BinaryOperationNode(VariableNode("x"), "^", N("2"))),
            "+",
            BinaryOperationNode(N("3"), "*", VariableNode("x")),
        ),
    ),
    (
        "f(x) = 2x^2 - 5",
        FunctionDefinitionNode(
            "f",
            [VariableNode("x")],
            BinaryOperationNode(
                BinaryOperationNode(N("2"), "*", BinaryOperationNode(VariableNode("x"), "^", N("2"))),
                "-",
                N("5"),
            ),
        ),
    ),
    (
        "2x^2 = 0",
        Equality(
            BinaryOperationNode(N("2"), "*", BinaryOperationNode(VariableNode("x"), "^", N("2"))),
            N("0"),
        ),
    ),
    # -2x = (-2) * x  (UMINUS binds tighter than MULTIPLY)
    (
        "-2x",
        BinaryOperationNode(UnaryMinusNode(N("2")), "*", VariableNode("x")),
    ),
    (
        "2(-2)",
        BinaryOperationNode(N("2"), "*", UnaryMinusNode(N("2"))),
    ),
    (
        "2(-x)",
        BinaryOperationNode(N("2"), "*", UnaryMinusNode(VariableNode("x"))),
    ),
    (
        "2func(x)",
        BinaryOperationNode(N("2"), "*", FunctionCallNode("func", [VariableNode("x")])),
    ),
    (
        "2x(y)",
        BinaryOperationNode(N("2"), "*", FunctionCallNode("x", [VariableNode("y")])),
    ),
    (
        "f(2x)",
        FunctionCallNode("f", [BinaryOperationNode(N("2"), "*", VariableNode("x"))]),
    ),
    (
        "[[2x, 3y]]",
        MatrixNode([[
            BinaryOperationNode(N("2"), "*", VariableNode("x")),
            BinaryOperationNode(N("3"), "*", VariableNode("y")),
        ]]),
    ),
]

query_solve_test_data = [
    # QueryNode: expr = ?
    ("x = ?", QueryNode(VariableNode("x"))),
    ("a + 2 = ?", QueryNode(BinaryOperationNode(VariableNode("a"), "+", N("2")))),
    ("42 = ?", QueryNode(N("42"))),
    ("sqrt(9) = ?", QueryNode(FunctionCallNode("sqrt", [N("9")]))),
    ("f(x) = ?", QueryNode(FunctionCallNode("f", [VariableNode("x")]))),
    ("f() = ?", QueryNode(FunctionCallNode("f", []))),
    # SolveNode: f(x) = val ?
    ("f(x) = 0 ?", SolveNode(FunctionCallNode("f", [VariableNode("x")]), N("0"))),
    (
        "f(x) = x + 1 ?",
        SolveNode(
            FunctionCallNode("f", [VariableNode("x")]),
            BinaryOperationNode(VariableNode("x"), "+", N("1")),
        ),
    ),
    # SolveNode: polynomial equation expr = expr ?
    ("x = 0 ?", SolveNode(VariableNode("x"), N("0"))),
    (
        "x^2 + x = 0 ?",
        SolveNode(
            BinaryOperationNode(
                BinaryOperationNode(VariableNode("x"), "^", N("2")),
                "+",
                VariableNode("x"),
            ),
            N("0"),
        ),
    ),
    (
        "2x^2 + 3x = 1 ?",
        SolveNode(
            BinaryOperationNode(
                BinaryOperationNode(N("2"), "*", BinaryOperationNode(VariableNode("x"), "^", N("2"))),
                "+",
                BinaryOperationNode(N("3"), "*", VariableNode("x")),
            ),
            N("1"),
        ),
    ),
]

unary_plus_test_data = [
    ("+1", UnaryPlusNode(N("1"))),
    ("+x", UnaryPlusNode(VariableNode("x"))),
    ("2 + +1", BinaryOperationNode(N("2"), "+", UnaryPlusNode(N("1")))),
    ("2 + -1", BinaryOperationNode(N("2"), "+", UnaryMinusNode(N("1")))),
    ("+(x)", UnaryPlusNode(VariableNode("x"))),
    # скобки делают внутреннее выражение атомом — два знака через скобки допустимы
    ("+(-1)", UnaryPlusNode(UnaryMinusNode(N("1")))),
    ("-(+x)", UnaryMinusNode(UnaryPlusNode(VariableNode("x")))),
]

invalid_input_test_data = [
    "1 +",
    "f(x",
    "[[1,2]",
    # Consecutive unary operators without parens
    "--3",
    "---3",
    "+-1",
    "+-+-1",
    "-+1",
    "++1",
    "x *",
    "x ^",
    "f(x) =",
    "2 **",
    "* 2",
    "-*",
    "1 + * 2",
    "+",
    "/",
    "%",
    "^",
    "*",
    "=",
    "f(",
    "[[1,2],[3,4]",
    "(",
    "[1, 2]",
    "[1, 2; 3, 4]",
    "[[1,2];]",
    "[[1,,2]]",
    "([[1 2]])",
    "[[1,2][3,4]]",
    "",
    "  ",
    "f(1, , 2)",
    "f(x,)",
    "f(())",
    "max((1, 2, 3))",
    "f(x=1)",
    "()",
    "= 5",
    "x = = 1",
    "x == = 1= 42",
    "a = b = 1",
    "x = y = 1",
    "1 <= 2 < 3",
    "f(x + y) = 2",
    "2(x)(y)",
    ")f(x",
    "f,f(,)f(1 2)",
    "[[1,2] [3,4]]x = ",
    "1 2 31 +",
]


@pytest.mark.parametrize("test_input,expected", basic_types_test_data)
def test_basic_types(test_input, expected):
    assert parser.parse(test_input) == expected


@pytest.mark.parametrize("test_input,expected", operations_test_data)
def test_operations(test_input, expected):
    assert parser.parse(test_input) == expected


@pytest.mark.parametrize("test_input,expected", operation_order_test_data)
def test_operations_order(test_input, expected):
    assert parser.parse(test_input) == expected


def test_polynomial():
    ax_squared = parser.parse("2*x^2")
    assert ax_squared == BinaryOperationNode(N("2"), "*", BinaryOperationNode(VariableNode("x"), "^", N("2")))
    bx = parser.parse("3*x")
    assert bx == BinaryOperationNode(N("3"), "*", VariableNode("x"))
    c = parser.parse("4")
    assert c == N("4")
    full = parser.parse("2*x^2 + 3*x - 4")
    assert full == BinaryOperationNode(BinaryOperationNode(ax_squared, "+", bx), "-", c)
    eq = parser.parse("2*x^2 + 3*x - 4 = 0")
    assert eq == Equality(full, N("0"))


@pytest.mark.parametrize("test_input", invalid_input_test_data)
def test_invalid_inputs(test_input):
    with pytest.raises((SyntaxError, ValueError)):
        parser.parse(test_input)


@pytest.mark.parametrize("test_input,expected", implicit_multiply_test_data)
def test_implicit_multiply(test_input, expected):
    assert parser.parse(test_input) == expected


@pytest.mark.parametrize("test_input,expected", query_solve_test_data)
def test_query_solve(test_input, expected):
    assert parser.parse(test_input) == expected


@pytest.mark.parametrize("test_input,expected", unary_plus_test_data)
def test_unary_plus(test_input, expected):
    assert parser.parse(test_input) == expected