import pytest

from computor_v2.errors import ComputorNameError, ComputorSolverError
from computor_v2.parsing.parser import parser
from computor_v2.store import Store
from computor_v2.types import Complex, Function, Rational

R = Rational


def make_dispatcher(store=None):
    from computor_v2.dispatcher import Dispatcher
    return Dispatcher(store or Store())


def dispatch(text: str, store=None):
    store = store or Store()
    node = parser.parse(text)
    from computor_v2.dispatcher import Dispatcher
    return Dispatcher(store).dispatch(node)


# ---------------------------------------------------------------------------
# Variable assignment: x = expr
# ---------------------------------------------------------------------------

class TestAssign:

    def test_simple_assign(self):
        store = Store()
        dispatch("x = 5", store)
        assert store.get("x") == R(5)

    def test_assign_returns_value(self):
        result = dispatch("x = 2 + 3")
        assert result == "5"

    def test_assign_expression(self):
        store = Store()
        dispatch("x = 2 * 3 + 1", store)
        assert store.get("x") == R(7)

    def test_assign_uses_store(self):
        store = Store()
        dispatch("x = 4", store)
        result = dispatch("y = x * 2", store)
        assert result == "8"

    def test_assign_complex(self):
        store = Store()
        dispatch("z = 2 * i + 3", store)
        assert store.get("z") == Complex(R(3), R(2))


# ---------------------------------------------------------------------------
# Function definition: f(x) = expr
# ---------------------------------------------------------------------------

class TestFuncDef:

    def test_stores_function(self):
        store = Store()
        dispatch("f(x) = x * 2", store)
        assert isinstance(store.get("f"), Function)

    def test_returns_display_string(self):
        result = dispatch("f(x) = x * 2")
        assert "x" in result
        assert "2" in result

    def test_constant_folding_in_display(self):
        # 4 - 5 + (x + 2)^2 - 4 должно показать упрощённую форму
        result = dispatch("f(x) = 2 + 3 + x")
        assert "5" in result   # 2+3 свёрнуты

    def test_function_callable_after_def(self):
        store = Store()
        dispatch("f(x) = x ^ 2", store)
        result = dispatch("f(3) = ?", store)
        assert result == "9"


# ---------------------------------------------------------------------------
# Query: expr = ?
# ---------------------------------------------------------------------------

class TestQuery:

    def test_query_number(self):
        assert dispatch("2 + 3 = ?") == "5"

    def test_query_variable(self):
        store = Store()
        dispatch("x = 42", store)
        assert dispatch("x = ?", store) == "42"

    def test_query_function_call(self):
        store = Store()
        dispatch("f(x) = x * 3", store)
        assert dispatch("f(4) = ?", store) == "12"

    def test_query_builtin(self):
        result = dispatch("sqrt(9) = ?")
        assert result == "3"

    def test_query_undefined_raises(self):
        with pytest.raises(ComputorNameError):
            dispatch("undefined = ?")


# ---------------------------------------------------------------------------
# Bare expression (no = ?)
# ---------------------------------------------------------------------------

class TestBareExpression:

    def test_bare_number(self):
        assert dispatch("2 + 3") == "5"

    def test_bare_uses_store(self):
        store = Store()
        dispatch("x = 10", store)
        assert dispatch("x * 2", store) == "20"


# ---------------------------------------------------------------------------
# Solve: f(x) = val ?
# ---------------------------------------------------------------------------

class TestSolve:

    def test_linear_solve(self):
        store = Store()
        dispatch("f(x) = 2 * x - 6", store)
        result = dispatch("f(x) = 0 ?", store)
        assert "3" in result

    def test_quadratic_two_roots(self):
        store = Store()
        dispatch("f(x) = x ^ 2 - 3 * x + 2", store)
        result = dispatch("f(x) = 0 ?", store)
        assert "1" in result
        assert "2" in result

    def test_quadratic_one_root(self):
        store = Store()
        dispatch("f(x) = x ^ 2 - 2 * x + 1", store)
        result = dispatch("f(x) = 0 ?", store)
        assert "1" in result

    def test_quadratic_no_real_roots(self):
        store = Store()
        dispatch("f(x) = x ^ 2 + 1", store)
        result = dispatch("f(x) = 0 ?", store)
        assert "i" in result.lower() or "complex" in result.lower()

    def test_degree_3_raises(self):
        store = Store()
        dispatch("f(x) = x ^ 3", store)
        with pytest.raises(ComputorSolverError):
            dispatch("f(x) = 0 ?", store)

    def test_no_solution(self):
        store = Store()
        dispatch("f(x) = 0 * x + 5", store)
        result = dispatch("f(x) = 0 ?", store)
        assert "no solution" in result.lower()

    def test_infinite_solutions(self):
        store = Store()
        dispatch("f(x) = 0 * x", store)
        result = dispatch("f(x) = 0 ?", store)
        assert "infinite" in result.lower()
