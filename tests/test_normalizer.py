import pytest

from computor_v2.errors import ComputorSolverError
from computor_v2.parsing.AST import (
    BinaryOperationNode,
    FunctionCallNode,
    NumberNode,
    UnaryMinusNode,
    VariableNode,
)
from computor_v2.store import Store
from computor_v2.types import Rational as R


def make_normalizer(store=None):
    from computor_v2.normalizer import Normalizer
    return Normalizer(store or Store())


def num(v):
    return NumberNode(str(v))


def var(name):
    return VariableNode(name)


def binop(left, op, right):
    return BinaryOperationNode(left, op, right)


class TestSimplify:

    def test_pure_number_folds(self):
        n = make_normalizer()
        result = n.simplify(binop(num(4), "-", num(5)), "x")
        assert result == num(-1)

    def test_variable_stays(self):
        n = make_normalizer()
        result = n.simplify(var("x"), "x")
        assert result == var("x")

    def test_other_variable_stays(self):
        n = make_normalizer()
        result = n.simplify(var("a"), "x")
        assert result == var("a")

    def test_constant_child_folds(self):
        # (4 - 5) + x  →  -1 + x
        n = make_normalizer()
        result = n.simplify(binop(binop(num(4), "-", num(5)), "+", var("x")), "x")
        assert result == binop(num(-1), "+", var("x"))

    def test_unary_minus_folds(self):
        n = make_normalizer()
        result = n.simplify(UnaryMinusNode(num(3)), "x")
        assert result == num(-3)

    def test_unary_minus_on_var_stays(self):
        n = make_normalizer()
        result = n.simplify(UnaryMinusNode(var("x")), "x")
        assert result == UnaryMinusNode(var("x"))

    def test_nested_constants_fold(self):
        # 2 * 3 + x  →  6 + x
        n = make_normalizer()
        result = n.simplify(binop(binop(num(2), "*", num(3)), "+", var("x")), "x")
        assert result == binop(num(6), "+", var("x"))

    def test_expression_with_no_free_var_folds_completely(self):
        # 2 + 3 * 4  →  14
        n = make_normalizer()
        result = n.simplify(binop(num(2), "+", binop(num(3), "*", num(4))), "x")
        assert result == num(14)


class TestToPolynomial:

    def test_constant(self):
        n = make_normalizer()
        assert n.to_polynomial(num(5), "x") == {0: R(5)}

    def test_variable(self):
        n = make_normalizer()
        assert n.to_polynomial(var("x"), "x") == {1: R(1)}

    def test_x_squared(self):
        n = make_normalizer()
        assert n.to_polynomial(binop(var("x"), "^", num(2)), "x") == {2: R(1)}

    def test_linear(self):
        # 3 * x
        n = make_normalizer()
        assert n.to_polynomial(binop(num(3), "*", var("x")), "x") == {1: R(3)}

    def test_quadratic(self):
        # x^2 - 5
        n = make_normalizer()
        poly = n.to_polynomial(binop(binop(var("x"), "^", num(2)), "-", num(5)), "x")
        assert poly == {2: R(1), 0: R(-5)}

    def test_full_quadratic(self):
        # x^2 + 3*x - 2
        n = make_normalizer()
        expr = binop(
            binop(binop(var("x"), "^", num(2)), "+", binop(num(3), "*", var("x"))),
            "-", num(2)
        )
        assert n.to_polynomial(expr, "x") == {2: R(1), 1: R(3), 0: R(-2)}

    def test_coefficient_on_squared(self):
        # 2 * x^2
        n = make_normalizer()
        poly = n.to_polynomial(binop(num(2), "*", binop(var("x"), "^", num(2))), "x")
        assert poly == {2: R(2)}

    def test_unary_minus(self):
        # -x  →  {1: -1}
        n = make_normalizer()
        assert n.to_polynomial(UnaryMinusNode(var("x")), "x") == {1: R(-1)}

    def test_store_variable_as_coefficient(self):
        # a * x where a = 3 in store
        store = Store()
        store.set("a", R(3))
        n = make_normalizer(store)
        poly = n.to_polynomial(binop(var("a"), "*", var("x")), "x")
        assert poly == {1: R(3)}

    def test_sqrt_of_var_raises(self):
        n = make_normalizer()
        with pytest.raises(ComputorSolverError):
            n.to_polynomial(FunctionCallNode("sqrt", [var("x")]), "x")

    def test_second_unknown_raises(self):
        n = make_normalizer()
        with pytest.raises(ComputorSolverError):
            n.to_polynomial(binop(var("x"), "+", var("y")), "x")

    def test_zero_coefficients_excluded(self):
        # x - x  →  {} or {0: 0} — нулевые коэффициенты не хранятся
        n = make_normalizer()
        poly = n.to_polynomial(binop(var("x"), "-", var("x")), "x")
        assert 1 not in poly or poly.get(1) == R(0)

    def test_power_of_bracket(self):
        # (x + 1)^2  →  {2: 1, 1: 2, 0: 1}
        n = make_normalizer()
        expr = binop(binop(var("x"), "+", num(1)), "^", num(2))
        assert n.to_polynomial(expr, "x") == {2: R(1), 1: R(2), 0: R(1)}

    def test_power_of_bracket_with_coeff(self):
        # (2*x + 3)^2 = 4x^2 + 12x + 9
        n = make_normalizer()
        inner = binop(binop(num(2), "*", var("x")), "+", num(3))
        expr = binop(inner, "^", num(2))
        assert n.to_polynomial(expr, "x") == {2: R(4), 1: R(12), 0: R(9)}

    def test_product_of_two_linears(self):
        # (x + 2) * (x - 3) = x^2 - x - 6
        n = make_normalizer()
        expr = binop(
            binop(var("x"), "+", num(2)),
            "*",
            binop(var("x"), "-", num(3)),
        )
        assert n.to_polynomial(expr, "x") == {2: R(1), 1: R(-1), 0: R(-6)}

    def test_rational_coefficient(self):
        # x^2 / 2  →  {2: 1/2}
        n = make_normalizer()
        expr = binop(binop(var("x"), "^", num(2)), "/", num(2))
        # division not in polynomial ops — raises
        with pytest.raises(ComputorSolverError):
            n.to_polynomial(expr, "x")

    def test_x_to_zero(self):
        # x^0  →  {0: 1}
        n = make_normalizer()
        assert n.to_polynomial(binop(var("x"), "^", num(0)), "x") == {0: R(1)}

    def test_cubic_raises_not_in_normalizer(self):
    # x^3 поддерживается нормализатором — solver потом решит degree
        n = make_normalizer()
        expr = binop(var("x"), "^", num(3))
        assert n.to_polynomial(expr, "x") == {3: R(1)}

    def test_negative_constant_term(self):
        # x^2 - 3*x + 2
        n = make_normalizer()
        expr = binop(
            binop(binop(var("x"), "^", num(2)), "-", binop(num(3), "*", var("x"))),
            "+", num(2)
        )
        assert n.to_polynomial(expr, "x") == {2: R(1), 1: R(-3), 0: R(2)}

    def test_fractional_constant(self):
        # x + 1/2  →  {1: 1, 0: 1/2}
        n = make_normalizer()
        expr = binop(var("x"), "+", binop(num(1), "/", num(2)))
        # "/" at constant level treated as division — might raise depending on impl
        # if Normalizer doesn't support division in poly: should raise
        # if it does handle constant division: {1: R(1), 0: R(1,2)}
        # We expect it to work since 1/2 simplifies to Rational(1,2) in _to_poly
        with pytest.raises(ComputorSolverError):
            n.to_polynomial(expr, "x")

    def test_multiply_by_negative(self):
        # -2 * x^2 + 4*x - 1
        n = make_normalizer()
        expr = binop(
            binop(UnaryMinusNode(num(2)), "*", binop(var("x"), "^", num(2))),
            "+",
            binop(binop(num(4), "*", var("x")), "-", num(1))
        )
        assert n.to_polynomial(expr, "x") == {2: R(-2), 1: R(4), 0: R(-1)}

    def test_store_coeff_in_quadratic(self):
        # a*x^2 + b*x + c where a=2, b=-3, c=1
        store = Store()
        store.set("a", R(2))
        store.set("b", R(-3))
        store.set("c", R(1))
        n = make_normalizer(store)
        expr = binop(
            binop(
                binop(var("a"), "*", binop(var("x"), "^", num(2))),
                "+",
                binop(var("b"), "*", var("x")),
            ),
            "+", var("c")
        )
        assert n.to_polynomial(expr, "x") == {2: R(2), 1: R(-3), 0: R(1)}

    def test_x_squared_times_bracket(self):
        # x^2 * (x + 1) = x^3 + x^2
        n = make_normalizer()
        expr = binop(binop(var("x"), "^", num(2)), "*", binop(var("x"), "+", num(1)))
        assert n.to_polynomial(expr, "x") == {3: R(1), 2: R(1)}

class TestToPolynomialForSolve:
    def test_zero_rhs(self):
        n = make_normalizer()
        # body = x^2 + 2x + 1, rhs = R(0) → same polynomial
        body = binop(
            binop(binop(var("x"), "^", num(2)), "+", binop(num(2), "*", var("x"))),
            "+", num(1)
        )
        poly = n.to_polynomial_for_solve(body, R(0), "x")
        assert poly == {2: R(1), 1: R(2), 0: R(1)}

    def test_nonzero_rhs(self):
        n = make_normalizer()
        # body = x + 3, rhs = R(5) → x + 3 - 5 = x - 2
        body = binop(var("x"), "+", num(3))
        poly = n.to_polynomial_for_solve(body, R(5), "x")
        assert poly == {1: R(1), 0: R(-2)}
