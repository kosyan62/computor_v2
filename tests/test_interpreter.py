import pytest
from computor_v2.parsing.AST import (
    NumberNode, VariableNode, UnaryMinusNode, UnaryPlusNode,
    BinaryOperationNode, FunctionCallNode, MatrixNode,
)
from computor_v2.types import Rational, Complex, Irrational, Matrix, Function
from computor_v2.store import Store
from computor_v2.errors import ComputorNameError, ComputorTypeError, ComputorRecursionError

R = Rational


def make_interpreter(store=None):
    from computor_v2.interpreter import Interpreter
    return Interpreter(store or Store())


def num(v):
    return NumberNode(str(v))


def var(name):
    return VariableNode(name)


def binop(left, op, right):
    return BinaryOperationNode(left, op, right)


# ---------------------------------------------------------------------------
# NumberNode
# ---------------------------------------------------------------------------

class TestNumberNode:

    def test_integer(self):
        interp = make_interpreter()
        assert interp.evaluate(num(3)) == R(3)

    def test_negative_integer(self):
        interp = make_interpreter()
        assert interp.evaluate(num(-5)) == R(-5)

    def test_float(self):
        interp = make_interpreter()
        assert interp.evaluate(num("3.5")) == R(7, 2)

    def test_fraction_string(self):
        interp = make_interpreter()
        assert interp.evaluate(num("0.25")) == R(1, 4)


# ---------------------------------------------------------------------------
# VariableNode
# ---------------------------------------------------------------------------

class TestVariableNode:

    def test_from_bindings(self):
        interp = make_interpreter()
        assert interp.evaluate(var("x"), {"x": R(7)}) == R(7)

    def test_from_store(self):
        store = Store()
        store.set("x", R(42))
        interp = make_interpreter(store)
        assert interp.evaluate(var("x")) == R(42)

    def test_builtin_i(self):
        interp = make_interpreter()
        assert interp.evaluate(var("i")) == Complex(R(0), R(1))

    def test_case_insensitive(self):
        store = Store()
        store.set("myVar", R(1))
        interp = make_interpreter(store)
        assert interp.evaluate(var("MYVAR")) == R(1)

    def test_bindings_shadow_store(self):
        store = Store()
        store.set("x", R(99))
        interp = make_interpreter(store)
        assert interp.evaluate(var("x"), {"x": R(1)}) == R(1)

    def test_undefined_raises(self):
        interp = make_interpreter()
        with pytest.raises(ComputorNameError):
            interp.evaluate(var("undefined"))


# ---------------------------------------------------------------------------
# Unary operators
# ---------------------------------------------------------------------------

class TestUnaryOps:

    def test_unary_minus(self):
        interp = make_interpreter()
        assert interp.evaluate(UnaryMinusNode(num(3))) == R(-3)

    def test_unary_plus(self):
        interp = make_interpreter()
        assert interp.evaluate(UnaryPlusNode(num(3))) == R(3)


# ---------------------------------------------------------------------------
# BinaryOperationNode — арифметика над Rational
# ---------------------------------------------------------------------------

class TestBinaryOps:

    def test_add(self):
        interp = make_interpreter()
        assert interp.evaluate(binop(num(2), "+", num(3))) == R(5)

    def test_sub(self):
        interp = make_interpreter()
        assert interp.evaluate(binop(num(5), "-", num(3))) == R(2)

    def test_mul(self):
        interp = make_interpreter()
        assert interp.evaluate(binop(num(3), "*", num(4))) == R(12)

    def test_div(self):
        interp = make_interpreter()
        assert interp.evaluate(binop(num(7), "/", num(2))) == R(7, 2)

    def test_modulo(self):
        interp = make_interpreter()
        assert interp.evaluate(binop(num(7), "%", num(3))) == R(1)

    def test_floordiv(self):
        interp = make_interpreter()
        assert interp.evaluate(binop(num(7), "//", num(2))) == R(3)

    def test_power(self):
        interp = make_interpreter()
        assert interp.evaluate(binop(num(2), "^", num(10))) == R(1024)

    def test_matmul(self):
        # ** между матрицами — матричное умножение
        m1 = MatrixNode([[num(1), num(2)], [num(3), num(4)]])
        m2 = MatrixNode([[num(1)], [num(1)]])
        interp = make_interpreter()
        result = interp.evaluate(BinaryOperationNode(m1, "**", m2))
        assert result == Matrix([[R(3)], [R(7)]])

    def test_unknown_operator_raises(self):
        interp = make_interpreter()
        with pytest.raises(ComputorTypeError):
            interp.evaluate(binop(num(1), "???", num(2)))


# ---------------------------------------------------------------------------
# FunctionCallNode — builtin
# ---------------------------------------------------------------------------

class TestFunctionCall:

    def test_builtin_sqrt_perfect_square(self):
        interp = make_interpreter()
        node = FunctionCallNode("sqrt", [num(9)])
        assert interp.evaluate(node) == R(3)

    def test_builtin_sqrt_irrational(self):
        interp = make_interpreter()
        node = FunctionCallNode("sqrt", [num(2)])
        result = interp.evaluate(node)
        assert isinstance(result, Irrational)

    def test_builtin_abs(self):
        interp = make_interpreter()
        node = FunctionCallNode("abs", [num(-5)])
        assert interp.evaluate(node) == R(5)

    def test_user_function(self):
        store = Store()
        body = binop(var("x"), "*", num(2))
        store.set("f", Function("x", body))
        interp = make_interpreter(store)
        node = FunctionCallNode("f", [num(3)])
        assert interp.evaluate(node) == R(6)

    def test_undefined_function_raises(self):
        interp = make_interpreter()
        with pytest.raises(ComputorNameError):
            interp.evaluate(FunctionCallNode("unknown", [num(1)]))


# ---------------------------------------------------------------------------
# MatrixNode
# ---------------------------------------------------------------------------

class TestMatrixNode:

    def test_simple_matrix(self):
        interp = make_interpreter()
        node = MatrixNode([[num(1), num(2)], [num(3), num(4)]])
        result = interp.evaluate(node)
        assert result == Matrix([[R(1), R(2)], [R(3), R(4)]])

    def test_matrix_with_expr(self):
        interp = make_interpreter()
        node = MatrixNode([[binop(num(1), "+", num(2))]])
        result = interp.evaluate(node)
        assert result == Matrix([[R(3)]])


# ---------------------------------------------------------------------------
# Recursion detection
# ---------------------------------------------------------------------------

class TestRecursion:

    def test_direct_recursion_raises(self):
        store = Store()
        body = FunctionCallNode("f", [var("x")])
        store.set("f", Function("x", body))
        interp = make_interpreter(store)
        with pytest.raises(ComputorRecursionError):
            interp.evaluate(FunctionCallNode("f", [num(1)]))

    def test_indirect_recursion_raises(self):
        store = Store()
        body_g = FunctionCallNode("f", [var("x")])
        body_f = FunctionCallNode("g", [var("x")])
        store.set("f", Function("x", body_f))
        store.set("g", Function("x", body_g))
        interp = make_interpreter(store)
        with pytest.raises(ComputorRecursionError):
            interp.evaluate(FunctionCallNode("f", [num(1)]))