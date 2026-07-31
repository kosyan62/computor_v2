from computor_v2.formatter import fmt_complex, fmt_rational
from computor_v2.types import Complex
from computor_v2.types import Rational as R


def test_integer():
    assert fmt_rational(R(5)) == "5"
    assert fmt_rational(R(-3)) == "-3"
    assert fmt_rational(R(0)) == "0"


def test_terminating_decimal():
    assert fmt_rational(R(2121, 500)) == "4.242"   # 500 = 2²×5³
    assert fmt_rational(R(1, 2)) == "0.5"
    assert fmt_rational(R(3, 4)) == "0.75"
    assert fmt_rational(R(1, 25)) == "0.04"
    assert fmt_rational(R(1, 8)) == "0.125"
    assert fmt_rational(R(-1, 2)) == "-0.5"


def test_non_terminating_fraction():
    assert fmt_rational(R(1, 3)) == "0.333333333"
    assert fmt_rational(R(7, 12)) == "0.583333333"
    assert fmt_rational(R(-2, 3)) == "-0.666666667"
    assert fmt_rational(R(1, 6)) == "0.166666667"


def test_complex_full():
    assert fmt_complex(Complex(R(3), R(2))) == "3 + 2i"
    assert fmt_complex(Complex(R(-4), R(-4))) == "-4 - 4i"
    assert fmt_complex(Complex(R(-4), R(2))) == "-4 + 2i"
    assert fmt_complex(Complex(R(-3), R(1))) == "-3 + i"
    assert fmt_complex(Complex(R(3), R(-1))) == "3 - i"
    assert fmt_complex(Complex(R(-3), R(-1))) == "-3 - i"


def test_complex_real_only():
    assert fmt_complex(Complex(R(3), R(0))) == "3"
    assert fmt_complex(Complex(R(0), R(0))) == "0"


def test_complex_imag_only():
    assert fmt_complex(Complex(R(0), R(2))) == "2i"
    assert fmt_complex(Complex(R(0), R(-1))) == "-i"
    assert fmt_complex(Complex(R(0), R(1))) == "i"
    assert fmt_complex(Complex(R(0), R(-3))) == "-3i"


def test_complex_rational_parts():
    assert fmt_complex(Complex(R(1, 2), R(1, 3))) == "0.5 + 0.333333333i"
    assert fmt_complex(Complex(R(3), R(-1, 2))) == "3 - 0.5i"


# Task 3: fmt_irrational — real coefficient
from computor_v2.formatter import fmt_irrational
from computor_v2.types import Irrational


def test_irrational_number_zero_d1():
    assert fmt_irrational(Irrational(R(0), R(1), R(5))) == "√5"
    assert fmt_irrational(Irrational(R(0), R(2), R(5))) == "2√5"


def test_irrational_number_zero_d_gt1():
    assert fmt_irrational(Irrational(R(0), R(1, 2), R(10))) == "√10 / 2"
    assert fmt_irrational(Irrational(R(0), R(-1, 2), R(10))) == "-√10 / 2"
    assert fmt_irrational(Irrational(R(0), R(2, 3), R(7))) == "2√7 / 3"


def test_irrational_with_number_d1():
    assert fmt_irrational(Irrational(R(1), R(2), R(5))) == "1 + 2√5"
    assert fmt_irrational(Irrational(R(-1), R(-1), R(3))) == "-1 - √3"


def test_irrational_with_number_d_gt1():
    assert fmt_irrational(Irrational(R(-5, 16), R(1, 16), R(39))) == "(-5 + √39) / 16"
    assert fmt_irrational(Irrational(R(-5, 16), R(-1, 16), R(39))) == "(-5 - √39) / 16"
    assert fmt_irrational(Irrational(R(1, 3), R(2, 3), R(7))) == "(1 + 2√7) / 3"


# Task 4: fmt_irrational — complex coefficient
def test_irrational_complex_coeff_zero_number():
    assert fmt_irrational(Irrational(R(0), Complex(R(0), R(2, 5)), R(5))) == "2√5 * i / 5"
    assert fmt_irrational(Irrational(R(0), Complex(R(0), R(-1)), R(2))) == "-√2 * i"
    assert fmt_irrational(Irrational(R(0), Complex(R(0), R(1)), R(3))) == "√3 * i"


def test_irrational_complex_coeff_with_number():
    assert fmt_irrational(
        Irrational(R(-5, 16), Complex(R(0), R(1, 16)), R(39))
    ) == "(-5 + √39 * i) / 16"
    assert fmt_irrational(
        Irrational(R(-5, 16), Complex(R(0), R(-1, 16)), R(39))
    ) == "(-5 - √39 * i) / 16"


# Task 5: fmt_matrix
from computor_v2.formatter import fmt_matrix
from computor_v2.types import Matrix


def test_matrix_single_row():
    m = Matrix([[R(1), R(2)]])
    assert fmt_matrix(m) == "[ 1 , 2 ]"


def test_matrix_multi_row():
    m = Matrix([[R(1), R(2)], [R(3), R(4)]])
    assert fmt_matrix(m) == "[ 1 , 2 ]\n[ 3 , 4 ]"


def test_matrix_single_element():
    m = Matrix([[R(7)]])
    assert fmt_matrix(m) == "[ 7 ]"


def test_matrix_with_fractions():
    m = Matrix([[R(1, 2), R(1, 3)]])
    assert fmt_matrix(m) == "[ 0.5 , 0.333333333 ]"


# Task 6: fmt_ast with precedence
from computor_v2.formatter import fmt_ast
from computor_v2.parsing.AST import (
    BinaryOperationNode,
    FunctionCallNode,
    NumberNode,
    UnaryMinusNode,
    VariableNode,
)


def test_ast_number():
    assert fmt_ast(NumberNode("3")) == "3"
    assert fmt_ast(NumberNode("4.242")) == "4.242"


def test_ast_variable():
    assert fmt_ast(VariableNode("x")) == "x"


def test_ast_unary_minus():
    assert fmt_ast(UnaryMinusNode(VariableNode("x"))) == "-x"
    assert fmt_ast(UnaryMinusNode(NumberNode("3"))) == "-3"
    assert fmt_ast(UnaryMinusNode(BinaryOperationNode(VariableNode("x"), "+", NumberNode("2")))) == "-(x + 2)"


def test_ast_binop_simple():
    node = BinaryOperationNode(VariableNode("x"), "+", NumberNode("2"))
    assert fmt_ast(node) == "x + 2"
    node = BinaryOperationNode(VariableNode("x"), "*", NumberNode("3"))
    assert fmt_ast(node) == "x * 3"


def test_ast_binop_power_no_spaces():
    node = BinaryOperationNode(VariableNode("x"), "^", NumberNode("2"))
    assert fmt_ast(node) == "x^2"


def test_ast_parentheses_low_prec_inside_high():
    # (x + 2) ^ 3  →  (x + 2)^3
    inner = BinaryOperationNode(VariableNode("x"), "+", NumberNode("2"))
    node = BinaryOperationNode(inner, "^", NumberNode("3"))
    assert fmt_ast(node) == "(x + 2)^3"


def test_ast_no_parens_high_prec_inside_low():
    # x^2 + 3  →  x^2 + 3
    inner = BinaryOperationNode(VariableNode("x"), "^", NumberNode("2"))
    node = BinaryOperationNode(inner, "+", NumberNode("3"))
    assert fmt_ast(node) == "x^2 + 3"


def test_ast_function_call():
    node = FunctionCallNode("f", [VariableNode("x")])
    assert fmt_ast(node) == "f(x)"
    node2 = FunctionCallNode("g", [VariableNode("x"), NumberNode("2")])
    assert fmt_ast(node2) == "g(x, 2)"


# Task 7: fmt_polynomial
from computor_v2.formatter import fmt_polynomial
from computor_v2.polynomial import Polynomial


def test_polynomial_constant():
    assert fmt_polynomial(Polynomial({0: R(3)}), "x") == "3"


def test_polynomial_linear():
    assert fmt_polynomial(Polynomial({1: R(2), 0: R(1)}), "x") == "2x + 1"
    assert fmt_polynomial(Polynomial({1: R(1), 0: R(-4)}), "x") == "x - 4"
    assert fmt_polynomial(Polynomial({1: R(-1), 0: R(2)}), "x") == "-x + 2"


def test_polynomial_quadratic():
    assert fmt_polynomial(Polynomial({2: R(1), 1: R(2), 0: R(1)}), "x") == "x^2 + 2x + 1"
    assert fmt_polynomial(Polynomial({2: R(5), 1: R(-3), 0: R(2)}), "x") == "5x^2 - 3x + 2"
    assert fmt_polynomial(Polynomial({2: R(-1), 0: R(4)}), "x") == "-x^2 + 4"
    assert fmt_polynomial(Polynomial({2: R(1)}), "x") == "x^2"


def test_polynomial_var_name():
    assert fmt_polynomial(Polynomial({1: R(2), 0: R(1)}), "y") == "2y + 1"


# Task 8: fmt_solve + fmt dispatcher
from computor_v2.formatter import fmt, fmt_solve
from computor_v2.solver import INFINITE_SOLUTIONS, NO_SOLUTION, SolveResult


def test_fmt_dispatch_rational():
    assert fmt(R(3)) == "3"
    assert fmt(R(1, 3)) == "0.333333333"


def test_fmt_dispatch_complex():
    assert fmt(Complex(R(3), R(2))) == "3 + 2i"


def test_fmt_dispatch_irrational():
    assert fmt(Irrational(R(0), R(1, 2), R(10))) == "√10 / 2"


def test_fmt_dispatch_matrix():
    assert fmt(Matrix([[R(1), R(2)]])) == "[ 1 , 2 ]"


def test_solve_no_solution():
    poly = Polynomial({0: R(3)})
    assert fmt_solve(NO_SOLUTION, poly, "x") == "3 = 0\nNo solution."


def test_solve_infinite():
    poly = Polynomial({0: R(0)})
    out = fmt_solve(INFINITE_SOLUTIONS, poly, "x")
    assert "Infinite solutions." in out


def test_solve_one_real():
    poly = Polynomial({2: R(1), 1: R(2), 0: R(1)})
    result = SolveResult([R(-1)], 1)
    out = fmt_solve(result, poly, "x")
    assert out == "x^2 + 2x + 1 = 0\nOne solution in ℝ:\n-1"


def test_solve_two_real():
    poly = Polynomial({2: R(1), 1: R(-5), 0: R(6)})
    result = SolveResult([R(2), R(3)], 2)
    out = fmt_solve(result, poly, "x")
    assert out == "x^2 - 5x + 6 = 0\nTwo solutions in ℝ:\n2\n3"


def test_solve_two_complex():
    # 5x^2 - 3x + 2 = 0 → x = (3 ± √31*i) / 10
    poly = Polynomial({2: R(5), 1: R(-3), 0: R(2)})
    sol1 = Irrational(R(3, 10), Complex(R(0), R(-1, 10)), R(31))
    sol2 = Irrational(R(3, 10), Complex(R(0), R(1, 10)), R(31))
    result = SolveResult([sol1, sol2], 2)
    out = fmt_solve(result, poly, "x")
    assert "Two solutions in ℂ:" in out
    assert "5x^2 - 3x + 2 = 0" in out
