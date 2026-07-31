import pytest

from computor_v2.parsing.AST import VariableNode
from computor_v2.types import BuiltinFunction, Complex, Function, Matrix, Rational

# ---------------------------------------------------------------------------
# Rational
# ---------------------------------------------------------------------------

class TestRational:

    def test_creation_reduces(self):
        assert Rational(4, 2) == Rational(2, 1)
        assert Rational(6, 4) == Rational(3, 2)
        assert Rational(-6, 4) == Rational(-3, 2)
        assert Rational(6, -4) == Rational(-3, 2)
        assert Rational(-6, -4) == Rational(3, 2)

    def test_zero(self):
        assert Rational(0) == Rational(0, 1)
        assert Rational(0).numerator == 0
        assert Rational(0).denominator == 1

    def test_denominator_zero(self):
        with pytest.raises(ZeroDivisionError):
            Rational(1, 0)

    def test_from_str_integer(self):
        assert Rational.from_str("42") == Rational(42)
        assert Rational.from_str("0") == Rational(0)

    def test_from_str_decimal(self):
        assert Rational.from_str("4.242") == Rational(2121, 500)
        assert Rational.from_str("0.5") == Rational(1, 2)
        assert Rational.from_str("1.0") == Rational(1)
        assert Rational.from_str("3.14") == Rational(157, 50)

    def test_from_str_negative(self):
        assert Rational.from_str("-42") == Rational(-42)
        assert Rational.from_str("-0.75") == Rational(-3, 4)
        assert Rational.from_str("-1.88") == Rational(-47, 25)
        assert Rational.from_str("-0.000000001") == Rational(-1, 10**9)
        assert Rational.from_str("+0.5") == Rational(1, 2)

    def test_add(self):
        assert Rational(1, 2) + Rational(1, 3) == Rational(5, 6)
        assert Rational(1) + Rational(2) == Rational(3)
        assert Rational(-1, 2) + Rational(1, 2) == Rational(0)

    def test_sub(self):
        assert Rational(3, 4) - Rational(1, 4) == Rational(1, 2)
        assert Rational(1) - Rational(2) == Rational(-1)

    def test_mul(self):
        assert Rational(2, 3) * Rational(3, 4) == Rational(1, 2)
        assert Rational(0) * Rational(100) == Rational(0)
        assert Rational(-2) * Rational(3) == Rational(-6)

    def test_div(self):
        assert Rational(1, 2) / Rational(1, 4) == Rational(2)
        assert Rational(3) / Rational(2) == Rational(3, 2)
        with pytest.raises(ZeroDivisionError):
            Rational(1) / Rational(0)

    def test_mod(self):
        assert Rational(5) % Rational(2) == Rational(1)
        assert Rational(7) % Rational(3) == Rational(1)
        assert Rational(6) % Rational(2) == Rational(0)
        with pytest.raises(ZeroDivisionError):
            Rational(1) % Rational(0)

    def test_floordiv(self):
        assert Rational(7) // Rational(2) == Rational(3)
        assert Rational(9) // Rational(4) == Rational(2)
        assert Rational(-7) // Rational(2) == Rational(-4)  # floor
        with pytest.raises(ZeroDivisionError):
            Rational(1) // Rational(0)

    def test_pow_positive(self):
        assert Rational(2) ** Rational(3) == Rational(8)
        assert Rational(1, 2) ** Rational(2) == Rational(1, 4)
        assert Rational(3) ** Rational(0) == Rational(1)

    def test_pow_negative(self):
        assert Rational(2) ** Rational(-1) == Rational(1, 2)
        assert Rational(2) ** Rational(-2) == Rational(1, 4)
        with pytest.raises(ZeroDivisionError):
            Rational(0) ** Rational(-1)

    def test_pow_non_integer_exp(self):
        with pytest.raises(TypeError):
            Rational(4) ** Rational(1, 2)

    def test_neg(self):
        assert -Rational(3) == Rational(-3)
        assert -Rational(-3) == Rational(3)
        assert -Rational(0) == Rational(0)

    def test_comparison(self):
        assert Rational(1, 2) < Rational(3, 4)
        assert Rational(3, 4) > Rational(1, 2)
        assert Rational(1, 2) <= Rational(1, 2)
        assert Rational(1, 2) >= Rational(1, 2)
        assert Rational(1, 3) != Rational(1, 2)

    def test_int_coerce_add(self):
        assert Rational(3) + 2 == Rational(5)
        assert 2 + Rational(3) == Rational(5)

    def test_int_coerce_sub(self):
        assert Rational(5) - 2 == Rational(3)
        assert 5 - Rational(2) == Rational(3)

    def test_int_coerce_mul(self):
        assert Rational(3) * 2 == Rational(6)
        assert 2 * Rational(3) == Rational(6)

    def test_int_coerce_div(self):
        assert Rational(6) / 2 == Rational(3)
        assert 6 / Rational(2) == Rational(3)

    def test_int_coerce_pow(self):
        assert Rational(2) ** 3 == Rational(8)

    def test_promotes_to_complex_on_add(self):
        result = Rational(3) + Complex(Rational(1), Rational(2))
        assert isinstance(result, Complex)
        assert result == Complex(Rational(4), Rational(2))

    def test_promotes_to_complex_on_mul(self):
        result = Rational(2) * Complex(Rational(3), Rational(1))
        assert isinstance(result, Complex)
        assert result == Complex(Rational(6), Rational(2))


# ---------------------------------------------------------------------------
# Complex
# ---------------------------------------------------------------------------

class TestComplex:

    def test_creation(self):
        c = Complex(Rational(3), Rational(2))
        assert c.re == Rational(3)
        assert c.im == Rational(2)

    def test_add_complex(self):
        a = Complex(Rational(1), Rational(2))
        b = Complex(Rational(3), Rational(4))
        assert a + b == Complex(Rational(4), Rational(6))

    def test_add_rational(self):
        c = Complex(Rational(1), Rational(2))
        assert c + Rational(3) == Complex(Rational(4), Rational(2))
        assert Rational(3) + c == Complex(Rational(4), Rational(2))

    def test_sub(self):
        a = Complex(Rational(4), Rational(3))
        b = Complex(Rational(1), Rational(2))
        assert a - b == Complex(Rational(3), Rational(1))

    def test_mul_complex(self):
        # (1+2i)(3+4i) = (3-8) + (4+6)i = -5 + 10i
        a = Complex(Rational(1), Rational(2))
        b = Complex(Rational(3), Rational(4))
        assert a * b == Complex(Rational(-5), Rational(10))

    def test_mul_rational(self):
        c = Complex(Rational(2), Rational(3))
        assert c * Rational(2) == Complex(Rational(4), Rational(6))
        assert Rational(2) * c == Complex(Rational(4), Rational(6))

    def test_div_complex(self):
        # (4+2i)/(3+1i) = ((12+2)+(6-4)i)/(9+1) = (14+2i)/10 = 7/5 + i/5
        a = Complex(Rational(4), Rational(2))
        b = Complex(Rational(3), Rational(1))
        assert a / b == Complex(Rational(7, 5), Rational(1, 5))

    def test_div_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            Complex(Rational(1), Rational(1)) / Complex(Rational(0), Rational(0))

    def test_neg(self):
        assert -Complex(Rational(3), Rational(2)) == Complex(Rational(-3), Rational(-2))

    def test_eq_rational(self):
        assert Complex(Rational(5), Rational(0)) == Rational(5)

    def test_no_matrix_ops(self):
        c = Complex(Rational(1), Rational(1))
        m = Matrix([[Rational(1), Rational(2)], [Rational(3), Rational(4)]])
        with pytest.raises(TypeError):
            c + m
        with pytest.raises(TypeError):
            c * m


# ---------------------------------------------------------------------------
# Matrix
# ---------------------------------------------------------------------------

class TestMatrix:

    def _m(self, rows):
        return Matrix([[Rational(v) for v in row] for row in rows])

    def test_creation(self):
        m = self._m([[1, 2], [3, 4]])
        assert m.n_rows == 2
        assert m.n_cols == 2

    def test_creation_invalid(self):
        with pytest.raises(ValueError):
            Matrix([[Rational(1), Rational(2)], [Rational(3)]])

    def test_add(self):
        a = self._m([[1, 2], [3, 4]])
        b = self._m([[5, 6], [7, 8]])
        assert a + b == self._m([[6, 8], [10, 12]])

    def test_add_size_mismatch(self):
        with pytest.raises(TypeError):
            self._m([[1, 2]]) + self._m([[1, 2], [3, 4]])

    def test_sub(self):
        a = self._m([[5, 6], [7, 8]])
        b = self._m([[1, 2], [3, 4]])
        assert a - b == self._m([[4, 4], [4, 4]])

    def test_mul_scalar(self):
        m = self._m([[1, 2], [3, 4]])
        assert m * Rational(2) == self._m([[2, 4], [6, 8]])
        assert Rational(2) * m == self._m([[2, 4], [6, 8]])

    def test_mul_elementwise(self):
        a = self._m([[1, 2], [3, 4]])
        b = self._m([[2, 0], [1, 3]])
        assert a * b == self._m([[2, 0], [3, 12]])

    def test_matmul(self):
        # [[1,2],[3,4]] @ [[5,6],[7,8]] = [[19,22],[43,50]]
        a = self._m([[1, 2], [3, 4]])
        b = self._m([[5, 6], [7, 8]])
        assert a @ b == self._m([[19, 22], [43, 50]])

    def test_matmul_size_mismatch(self):
        with pytest.raises(TypeError):
            self._m([[1, 2, 3]]) @ self._m([[1, 2], [3, 4]])

    def test_matmul_non_square(self):
        # 2×3 @ 3×2 = 2×2
        a = Matrix([[Rational(1), Rational(2), Rational(3)],
                    [Rational(4), Rational(5), Rational(6)]])
        b = Matrix([[Rational(7), Rational(8)],
                    [Rational(9), Rational(10)],
                    [Rational(11), Rational(12)]])
        result = a @ b
        assert result == Matrix([[Rational(58), Rational(64)],
                                  [Rational(139), Rational(154)]])

    def test_eq(self):
        assert self._m([[1, 2]]) == self._m([[1, 2]])
        assert self._m([[1, 2]]) != self._m([[1, 3]])


# ---------------------------------------------------------------------------
# Function
# ---------------------------------------------------------------------------

class TestFunction:

    def test_creation(self):
        body = VariableNode("x")
        f = Function("x", body)
        assert f.param == "x"
        assert f.body is body


# ---------------------------------------------------------------------------
# BuiltinFunction
# ---------------------------------------------------------------------------

class TestBuiltinFunction:

    def test_isinstance_function(self):
        b = BuiltinFunction("double", lambda x: x + x)
        assert isinstance(b, Function)

    def test_call(self):
        double = BuiltinFunction("double", lambda x: x * Rational(2))
        result = double.call(Rational(3))
        assert result == Rational(6)

    def test_call_evaluator_ignored(self):
        b = BuiltinFunction("id", lambda x: x)
        assert b.call(Rational(5), evaluator="anything") == Rational(5)

    def test_eq(self):
        a = BuiltinFunction("f", lambda x: x)
        b = BuiltinFunction("f", lambda x: x)
        assert a == b

    def test_repr(self):
        b = BuiltinFunction("sqrt", lambda x: x)
        assert "sqrt" in repr(b)


# ---------------------------------------------------------------------------
# Store
