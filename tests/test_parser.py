import pytest

from computor_v2.parsing.AST import (
    VariableNode,
    NumberNode,
    BinaryOperationNode,
    FunctionCallNode,
    MatrixNode,
    Equality,
    ComparisonNode,
    FunctionDefinitionNode,
)
from computor_v2.parsing.parser import parser

basic_types_test_data = [
    ("1", NumberNode(1.0)),
    ("x", VariableNode("x")),
    (
        "[[1, 2];[3,4]]",
        MatrixNode(
            [[NumberNode(1.0), NumberNode(2.0)], [NumberNode(3.0), NumberNode(4.0)]]
        ),
    ),
    ("x + 1", BinaryOperationNode(VariableNode("x"), "+", NumberNode(1.0))),
    ("f(x)", FunctionCallNode("f", [VariableNode("x")])),
    ("f(x) = 42", FunctionDefinitionNode("f", [VariableNode("x")], NumberNode(42.0))),
    ("x = 42", Equality(VariableNode("x"), NumberNode(42.0))),
    ("x != 42", ComparisonNode(VariableNode("x"), "!=", NumberNode(42.0))),
]

operations_test_data = [
    # Arithmetic Operators
    ("1 + 2", BinaryOperationNode(NumberNode(1.0), "+", NumberNode(2.0))),
    ("3 - 1", BinaryOperationNode(NumberNode(3.0), "-", NumberNode(1.0))),
    ("4 * 2", BinaryOperationNode(NumberNode(4.0), "*", NumberNode(2.0))),
    ("8 / 4", BinaryOperationNode(NumberNode(8.0), "/", NumberNode(4.0))),
    ("2 ^ 3", BinaryOperationNode(NumberNode(2.0), "^", NumberNode(3.0))),
    (
        "[[1,2];[3,4]] ** [[5,6];[7,8]]",
        BinaryOperationNode(
            MatrixNode([[NumberNode(1.0), NumberNode(2.0)], [NumberNode(3.0), NumberNode(4.0)]]),
            "**",
            MatrixNode([[NumberNode(5.0), NumberNode(6.0)], [NumberNode(7.0), NumberNode(8.0)]]),
        ),
    ),
    ("5 % 2", BinaryOperationNode(NumberNode(5.0), "%", NumberNode(2.0))),
    ("9 // 4", BinaryOperationNode(NumberNode(9.0), "//", NumberNode(4.0))),
    # For token
    ("2 * x", BinaryOperationNode(NumberNode(2), "*", VariableNode("x"))),
    ("x * 2", BinaryOperationNode(VariableNode("x"), "*", NumberNode(2))),
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
    ("1 == 2", ComparisonNode(NumberNode(1.0), "==", NumberNode(2.0))),
    ("3 != 4", ComparisonNode(NumberNode(3.0), "!=", NumberNode(4.0))),
    ("2 > 1", ComparisonNode(NumberNode(2.0), ">", NumberNode(1.0))),
    ("2 >= 2", ComparisonNode(NumberNode(2.0), ">=", NumberNode(2.0))),
    ("1 < 2", ComparisonNode(NumberNode(1.0), "<", NumberNode(2.0))),
    ("2 <= 3", ComparisonNode(NumberNode(2.0), "<=", NumberNode(3.0))),
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
    ("f(x)", FunctionCallNode("f", [VariableNode("x")])),
    ("f((x))", FunctionCallNode("f", [VariableNode("x")])),
    ("g(x, 42)", FunctionCallNode("g", [VariableNode("x"), NumberNode(42.0)])),
    ("f(x, y)", FunctionCallNode("f", [VariableNode("x"), VariableNode("y")])),
    (
        "f(x + y)",
        FunctionCallNode(
            "f", [BinaryOperationNode(VariableNode("x"), "+", VariableNode("y"))]
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
    ("f(x) = 42", FunctionDefinitionNode("f", [VariableNode("x")], NumberNode(42.0))),
    ("f() = 42", FunctionDefinitionNode("f", [], NumberNode(42.0))),
    (
        "f(x, y) = 42",
        FunctionDefinitionNode("f", [VariableNode("x"), VariableNode("y")], NumberNode(42.0)),
    ),
    (
        "f(x) = 2 * x",
        FunctionDefinitionNode(
            "f",
            [VariableNode("x")],
            BinaryOperationNode(NumberNode(2.0), "*", VariableNode("x")),
        ),
    ),
    # Unary minus
    ("-3", BinaryOperationNode(NumberNode(-1.0), "*", NumberNode(3.0))),
    (
        "-f(x)",
        BinaryOperationNode(
            NumberNode(-1.0), "*", FunctionCallNode("f", [VariableNode("x")])
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
    ("a = 4", Equality(VariableNode("a"), NumberNode(4))),  # Matrix
    (
        "a = 1 + x",
        Equality(
            VariableNode("a"), BinaryOperationNode(NumberNode(1.0), "+", VariableNode("x"))
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
            VariableNode("m"),
            MatrixNode([[NumberNode(1.0), NumberNode(2.0)], [NumberNode(3.0), NumberNode(4.0)]]),
        ),
    ),
    # Assignment to function call result
    ("x = f(2)", Equality(VariableNode("x"), FunctionCallNode("f", [NumberNode(2.0)]))),
    # Equation form: expr = expr (both sides non-trivial)
    (
        "x + 1 = 2 * x",
        Equality(
            BinaryOperationNode(VariableNode("x"), "+", NumberNode(1.0)),
            BinaryOperationNode(NumberNode(2.0), "*", VariableNode("x")),
        ),
    ),
    # Modulo with token operands
    ("x % 2", BinaryOperationNode(VariableNode("x"), "%", NumberNode(2.0))),
    ("a % b", BinaryOperationNode(VariableNode("a"), "%", VariableNode("b"))),
    # Column vector (single-column matrix)
    (
        "[[1];[2];[3]]",
        MatrixNode([[NumberNode(1.0)], [NumberNode(2.0)], [NumberNode(3.0)]]),
    ),
    # Single-element matrix
    ("[[5]]", MatrixNode([[NumberNode(5.0)]])),
    # Унарный минус в присваивании
    (
        "x = -3",
        Equality(VariableNode("x"), BinaryOperationNode(NumberNode(-1.0), "*", NumberNode(3.0))),
    ),
    # Степень в присваивании
    (
        "x = 2 ^ 3",
        Equality(VariableNode("x"), BinaryOperationNode(NumberNode(2.0), "^", NumberNode(3.0))),
    ),
    # Вложенный вызов функции
    ("f(g(x))", FunctionCallNode("f", [FunctionCallNode("g", [VariableNode("x")])])),
    # Рекурсивный вызов той же функции
    ("f(f(x))", FunctionCallNode("f", [FunctionCallNode("f", [VariableNode("x")])])),
    # Тело функции — вызов другой функции
    (
        "f(x) = g(x)",
        FunctionDefinitionNode("f", [VariableNode("x")], FunctionCallNode("g", [VariableNode("x")])),
    ),
    # Сгруппированные выражения с переменными
    (
        "(x + 1) * (x - 1)",
        BinaryOperationNode(
            BinaryOperationNode(VariableNode("x"), "+", NumberNode(1.0)),
            "*",
            BinaryOperationNode(VariableNode("x"), "-", NumberNode(1.0)),
        ),
    ),
    # Матрица с выражениями внутри элементов
    (
        "[[1+2, 2*3]; [4^2, 5-3]]",
        MatrixNode([
            [
                BinaryOperationNode(NumberNode(1.0), "+", NumberNode(2.0)),
                BinaryOperationNode(NumberNode(2.0), "*", NumberNode(3.0)),
            ],
            [
                BinaryOperationNode(NumberNode(4.0), "^", NumberNode(2.0)),
                BinaryOperationNode(NumberNode(5.0), "-", NumberNode(3.0)),
            ],
        ]),
    ),
    # Матрица в скобках
    (
        "([[1, 2]; [3, 4]])",
        MatrixNode([[NumberNode(1.0), NumberNode(2.0)], [NumberNode(3.0), NumberNode(4.0)]]),
    ),
    # Тройная вложенность вызовов
    (
        "f(g(h(x)))",
        FunctionCallNode("f", [FunctionCallNode("g", [FunctionCallNode("h", [VariableNode("x")])])]),
    ),
    # Uppercase идентификаторы
    ("X = 1", Equality(VariableNode("X"), NumberNode(1.0))),
    ("VarA", VariableNode("VarA")),
    # Функция с несколькими аргументами в определении
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
    # Функция возвращает матрицу
    (
        "m() = [[1, 2]; [3, 4]]",
        FunctionDefinitionNode(
            "m",
            [],
            MatrixNode([[NumberNode(1.0), NumberNode(2.0)], [NumberNode(3.0), NumberNode(4.0)]]),
        ),
    ),
    # Тело функции — вызов с вычислением
    (
        "f(x) = g(x) + 1",
        FunctionDefinitionNode(
            "f",
            [VariableNode("x")],
            BinaryOperationNode(FunctionCallNode("g", [VariableNode("x")]), "+", NumberNode(1.0)),
        ),
    ),
    # Функция с определением через степень
    (
        "f(x) = x^2",
        FunctionDefinitionNode(
            "f", [VariableNode("x")], BinaryOperationNode(VariableNode("x"), "^", NumberNode(2.0))
        ),
    ),
    # Унарный минус внутри аргумента функции
    (
        "f(-x)",
        FunctionCallNode("f", [BinaryOperationNode(NumberNode(-1.0), "*", VariableNode("x"))]),
    ),
    # Несколько выражений как аргументы
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
    # Сложное выражение как аргумент
    (
        "f(x * 2 + 1)",
        FunctionCallNode(
            "f",
            [BinaryOperationNode(
                BinaryOperationNode(VariableNode("x"), "*", NumberNode(2.0)),
                "+",
                NumberNode(1.0),
            )],
        ),
    ),
    # Функция с умножением в аргументе
    (
        "f(x, y * z)",
        FunctionCallNode(
            "f",
            [VariableNode("x"), BinaryOperationNode(VariableNode("y"), "*", VariableNode("z"))],
        ),
    ),
    # Функция с матричным аргументом и числом
    (
        "f(2, [[1, 2]])",
        FunctionCallNode(
            "f", [NumberNode(2.0), MatrixNode([[NumberNode(1.0), NumberNode(2.0)]])]
        ),
    ),
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
    # Унарный минус имеет меньший приоритет, чем степень: -x^2 = -(x^2)
    (
        "-x^2",
        BinaryOperationNode(
            NumberNode(-1.0),
            "*",
            BinaryOperationNode(VariableNode("x"), "^", NumberNode(2.0)),
        ),
    ),
    # Отрицательный показатель: x^-2 = x^(-1*2)
    (
        "x^-2",
        BinaryOperationNode(
            VariableNode("x"),
            "^",
            BinaryOperationNode(NumberNode(-1.0), "*", NumberNode(2.0)),
        ),
    ),
    # Умножение приоритетнее сложения: x * y + z = (x*y) + z
    (
        "x * y + z",
        BinaryOperationNode(
            BinaryOperationNode(VariableNode("x"), "*", VariableNode("y")),
            "+",
            VariableNode("z"),
        ),
    ),
    # Умножение приоритетнее сложения: x + y * z = x + (y*z)
    (
        "x + y * z",
        BinaryOperationNode(
            VariableNode("x"),
            "+",
            BinaryOperationNode(VariableNode("y"), "*", VariableNode("z")),
        ),
    ),
    # Левая ассоциативность сложения: 1 + 2 + 3 = (1+2)+3
    (
        "1 + 2 + 3",
        BinaryOperationNode(
            BinaryOperationNode(NumberNode(1.0), "+", NumberNode(2.0)),
            "+",
            NumberNode(3.0),
        ),
    ),
    # Левая ассоциативность деления: 1 / 2 / 4 = (1/2)/4
    (
        "1 / 2 / 4",
        BinaryOperationNode(
            BinaryOperationNode(NumberNode(1.0), "/", NumberNode(2.0)),
            "/",
            NumberNode(4.0),
        ),
    ),
]

implicit_multiply_test_data = [
    # Базовое неявное умножение: число сразу за идентификатором
    ("2x", BinaryOperationNode(NumberNode(2.0), "*", VariableNode("x"))),
    # С пробелом (тот же поток токенов после лексинга)
    ("2 x", BinaryOperationNode(NumberNode(2.0), "*", VariableNode("x"))),
    # Вещественный коэффициент
    ("3.14x", BinaryOperationNode(NumberNode(3.14), "*", VariableNode("x"))),
    # Неявное умножение перед скобкой
    (
        "2(x + 1)",
        BinaryOperationNode(
            NumberNode(2.0), "*", BinaryOperationNode(VariableNode("x"), "+", NumberNode(1.0))
        ),
    ),
    # Ключевой случай: 2x^2 должно быть 2*(x^2), а НЕ (2*x)^2
    (
        "2x^2",
        BinaryOperationNode(
            NumberNode(2.0),
            "*",
            BinaryOperationNode(VariableNode("x"), "^", NumberNode(2.0)),
        ),
    ),
    # Неявное умножение в более длинном выражении
    (
        "2x + 3",
        BinaryOperationNode(
            BinaryOperationNode(NumberNode(2.0), "*", VariableNode("x")),
            "+",
            NumberNode(3.0),
        ),
    ),
    # Два неявных умножения
    (
        "2x + 3y",
        BinaryOperationNode(
            BinaryOperationNode(NumberNode(2.0), "*", VariableNode("x")),
            "+",
            BinaryOperationNode(NumberNode(3.0), "*", VariableNode("y")),
        ),
    ),
    # Полином с неявным умножением
    (
        "2x^2 + 3x",
        BinaryOperationNode(
            BinaryOperationNode(
                NumberNode(2.0),
                "*",
                BinaryOperationNode(VariableNode("x"), "^", NumberNode(2.0)),
            ),
            "+",
            BinaryOperationNode(NumberNode(3.0), "*", VariableNode("x")),
        ),
    ),
    # В определении функции
    (
        "f(x) = 2x^2 - 5",
        FunctionDefinitionNode(
            "f",
            [VariableNode("x")],
            BinaryOperationNode(
                BinaryOperationNode(
                    NumberNode(2.0),
                    "*",
                    BinaryOperationNode(VariableNode("x"), "^", NumberNode(2.0)),
                ),
                "-",
                NumberNode(5.0),
            ),
        ),
    ),
    # Уравнение с неявным умножением
    (
        "2x^2 = 0",
        Equality(
            BinaryOperationNode(
                NumberNode(2.0), "*", BinaryOperationNode(VariableNode("x"), "^", NumberNode(2.0))
            ),
            NumberNode(0.0),
        ),
    ),
    # Унарный минус + неявное: -2x = (-1*2)*x
    (
        "-2x",
        BinaryOperationNode(
            BinaryOperationNode(NumberNode(-1.0), "*", NumberNode(2.0)),
            "*",
            VariableNode("x"),
        ),
    ),
    # Неявное умножение с отрицательным содержимым скобок
    (
        "2(-2)",
        BinaryOperationNode(
            NumberNode(2.0),
            "*",
            BinaryOperationNode(NumberNode(-1.0), "*", NumberNode(2.0)),
        ),
    ),
    (
        "2(-x)",
        BinaryOperationNode(
            NumberNode(2.0),
            "*",
            BinaryOperationNode(NumberNode(-1.0), "*", VariableNode("x")),
        ),
    ),
    # Коэффициент перед вызовом функции: 2func(x) = 2 * func(x)
    (
        "2func(x)",
        BinaryOperationNode(
            NumberNode(2.0), "*", FunctionCallNode("func", [VariableNode("x")])
        ),
    ),
    # 2x(y): x(y) — вызов функции, итого 2 * x(y)
    (
        "2x(y)",
        BinaryOperationNode(
            NumberNode(2.0), "*", FunctionCallNode("x", [VariableNode("y")])
        ),
    ),
    # Неявное умножение внутри аргумента функции
    (
        "f(2x)",
        FunctionCallNode(
            "f", [BinaryOperationNode(NumberNode(2.0), "*", VariableNode("x"))]
        ),
    ),
    # Неявное умножение внутри матрицы
    (
        "[[2x, 3y]]",
        MatrixNode([[
            BinaryOperationNode(NumberNode(2.0), "*", VariableNode("x")),
            BinaryOperationNode(NumberNode(3.0), "*", VariableNode("y")),
        ]]),
    ),
]

unary_plus_test_data = [
    ("+1", NumberNode(1.0)),
    ("+x", VariableNode("x")),
    ("2 + +1", BinaryOperationNode(NumberNode(2.0), "+", NumberNode(1.0))),
    (
        "+-1",
        BinaryOperationNode(NumberNode(-1.0), "*", NumberNode(1.0)),
    ),
    (
        "+-+-1",
        BinaryOperationNode(
            NumberNode(-1.0),
            "*",
            BinaryOperationNode(NumberNode(-1.0), "*", NumberNode(1.0)),
        ),
    ),
]

# --- Тесты на явные ошибки синтаксиса --- #
invalid_input_test_data = [
    "1 +",        # незаконченное выражение
    "f(x",        # незакрытая скобка
    "[[1,2]",     # незакрытая матрица
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
            NumberNode(2.0), "*", BinaryOperationNode(VariableNode("x"), "^", NumberNode(2.0))
    )
    bx = parser.parse("3*x")
    assert bx == BinaryOperationNode(
        NumberNode(3.0), "*", VariableNode("x")
    )
    c = parser.parse("4")
    assert c == NumberNode(4.0)
    ax_squared_plus_bx_minus_c = parser.parse("2*x^2 + 3*x - 4")
    assert ax_squared_plus_bx_minus_c == BinaryOperationNode(
        BinaryOperationNode(ax_squared, "+", bx), "-", c)
    polynomial_expression = parser.parse("2*x^2 + 3*x - 4 = 0")
    assert polynomial_expression == Equality(ax_squared_plus_bx_minus_c, NumberNode(0.0))


@pytest.mark.parametrize("test_input", [
    # Незаконченные выражения
    "1 +",
    "x *",
    "x ^",
    "f(x) =",
    "2 **",
    # Операторы в начале (не унарный минус/плюс)
    "* 2",
    "-*",
    "1 + * 2",
    # Одиночные операторы
    "+",
    "/",
    "%",
    "^",
    "*",
    "=",
    # Незакрытые скобки / скобки
    "f(x",
    "f(",
    "[[1,2]",
    "[[1,2],[3,4]",
    "(",
    # Невалидные матрицы
    "[1, 2]",           # одинарные скобки
    "[1, 2; 3, 4]",     # одинарные скобки с разделителем
    "[[1,2];]",         # пустая строка после ;
    "[[1,,2]]",         # двойная запятая
    "([[1 2]])",        # элементы без запятой
    "[[1,2][3,4]]",     # строки без ;
    # Пустой / пробельный ввод
    "",
    "  ",
    # Невалидные вызовы функций
    "f(1, , 2)",        # пустой аргумент
    "f(x,)",            # trailing запятая
    "f(())",            # пустые скобки как аргумент
    "max((1, 2, 3))",   # кортеж в аргументе
    "f(x=1)",           # keyword argument
    "()",               # пустые скобки
    # Невалидные присваивания
    "= 5",
    "x = = 1",
    "x == = 1= 42",
    "a = b = 1",
    "x = y = 1",
    # Цепочка сравнений
    "1 <= 2 < 3",
    # Функция с выражением как параметром в определении
    "f(x + y) = 2",
    # Нельзя вызвать expression как функцию
    "2(x)(y)",
    # Прочее
    ")f(x",
    "f,f(,)f(1 2)",
    "[[1,2] [3,4]]x = ",
    "1 2 31 +",
])
def test_invalid_inputs(test_input):
    with pytest.raises((SyntaxError, ValueError)):
        parser.parse(test_input)


@pytest.mark.parametrize("test_input,expected", implicit_multiply_test_data)
def test_implicit_multiply(test_input, expected):
    result = parser.parse(test_input)
    assert result == expected


@pytest.mark.parametrize("test_input,expected", unary_plus_test_data)
def test_unary_plus(test_input, expected):
    result = parser.parse(test_input)
    assert result == expected
