import pytest

from computor_v2.calculus.pure import factor_sqrt
from computor_v2.calculus.typed import sqrt
from computor_v2.types import Complex, Irrational, Rational

R = Rational


# ---------------------------------------------------------------------------
# calculus.pure.factor_sqrt
# ---------------------------------------------------------------------------

class TestFactorSqrt:

    def test_perfect_square(self):
        assert factor_sqrt(4) == (2, 1)
        assert factor_sqrt(9) == (3, 1)
        assert factor_sqrt(25) == (5, 1)

    def test_square_free(self):
        assert factor_sqrt(2) == (1, 2)
        assert factor_sqrt(3) == (1, 3)
        assert factor_sqrt(5) == (1, 5)

    def test_composite(self):
        assert factor_sqrt(8) == (2, 2)    # square root of 8 = 2 * square root of 2
        assert factor_sqrt(12) == (2, 3)   # square root of 12 = 2 * square root of 3
        assert factor_sqrt(18) == (3, 2)   # square root of 18 = 3 * square root of 2
        assert factor_sqrt(50) == (5, 2)   # square root of 50 = 5 * square root of 2

    def test_one(self):
        assert factor_sqrt(1) == (1, 1)


# ---------------------------------------------------------------------------
# calculus.typed.sqrt
# ---------------------------------------------------------------------------

class TestSqrt:

    def test_perfect_squares_return_rational(self):
        assert sqrt(R(4)) == R(2)
        assert sqrt(R(9)) == R(3)
        assert sqrt(R(25)) == R(5)
        assert sqrt(R(0)) == R(0)
        assert sqrt(R(1)) == R(1)

    def test_rational_perfect_square(self):
        # square root of (1/4) = 1/2
        assert sqrt(R(1, 4)) == R(1, 2)
        # square root of (9/16) = 3/4
        assert sqrt(R(9, 16)) == R(3, 4)

    def test_non_perfect_returns_irrational(self):
        result = sqrt(R(2))
        assert isinstance(result, Irrational)
        assert result.radicand == R(2)
        assert result.coeff == R(1)
        assert result.number == R(0)

    def test_sqrt_normalizes(self):
        # square root of 8 = 2 * square root of 2
        result = sqrt(R(8))
        assert isinstance(result, Irrational)
        assert result.radicand == R(2)
        assert result.coeff == R(2)

    def test_sqrt_non_rational_raises(self):
        with pytest.raises(TypeError):
            sqrt(2)  # plain int, not Rational

    def test_sqrt_negative_perfect_square_returns_complex(self):
        # square root of -4 = 2i
        result = sqrt(R(-4))
        assert isinstance(result, Complex)
        assert result == Complex(R(0), R(2))

    def test_sqrt_negative_non_perfect_returns_irrational(self):
        # square root of -2 = i * square root of 2
        result = sqrt(R(-2))
        assert isinstance(result, Irrational)
        assert result.radicand == R(2)
        assert result.coeff == Complex(R(0), R(1))
        assert result.number == R(0)

    def test_sqrt_negative_composite(self):
        # square root of -8 = 2i * square root of 2
        result = sqrt(R(-8))
        assert isinstance(result, Irrational)
        assert result.radicand == R(2)
        assert result.coeff == Complex(R(0), R(2))


# ---------------------------------------------------------------------------
# Irrational construction & normalization
# ---------------------------------------------------------------------------

class TestIrrationalConstruction:

    def test_basic(self):
        ir = Irrational(R(0), R(1), R(2))
        assert ir.number == R(0)
        assert ir.coeff == R(1)
        assert ir.radicand == R(2)

    def test_normalizes_radicand(self):
        # square root of 8 = 2 * square root of 2
        ir = Irrational(R(0), R(1), R(8))
        assert ir.radicand == R(2)
        assert ir.coeff == R(2)

    def test_normalizes_rational_radicand(self):
        # 1 * square root of (1/2) = (1/2) * square root of 2
        ir = Irrational(R(0), R(1), R(1, 2))
        assert ir.radicand == R(2)
        assert ir.coeff == R(1, 2)

    def test_zero_radicand_raises(self):
        with pytest.raises(ValueError):
            Irrational(R(0), R(1), R(0))

    def test_negative_radicand_converts_to_complex_coeff(self):
        # √(-2) = i * √2
        ir = Irrational(R(0), R(1), R(-2))
        assert ir.radicand == R(2)
        assert ir.coeff == Complex(R(0), R(1))

    def test_negative_radicand_perfect_square_coeff(self):
        # √(-4) = i * 2 * √1... but radicand=1 means coeff*√1 = coeff, still Irrational
        # Actually √(-4) is better handled via calculus.typed.sqrt → Complex
        # Here we just verify normalization: coeff absorbs i and factor
        ir = Irrational(R(0), R(1), R(-4))
        assert ir.radicand == R(1)
        assert ir.coeff == Complex(R(0), R(2))

    def test_zero_coeff_raises(self):
        with pytest.raises(ValueError):
            Irrational(R(0), R(0), R(2))


# ---------------------------------------------------------------------------
# Irrational arithmetic
# ---------------------------------------------------------------------------

class TestIrrationalArithmetic:

    def _ir(self, rational=0, coeff=1, radicand=2):
        return Irrational(R(rational), R(coeff), R(radicand))

    # --- add ---

    def test_add_rational(self):
        ir = self._ir(0, 1, 2)
        result = ir + R(3)
        assert isinstance(result, Irrational)
        assert result.number == R(3)
        assert result.coeff == R(1)

    def test_add_int(self):
        ir = self._ir(0, 1, 2)
        result = ir + 3
        assert result.number == R(3)

    def test_radd_rational(self):
        ir = self._ir(0, 1, 2)
        result = R(3) + ir
        assert result.number == R(3)

    def test_add_same_radicand(self):
        # square root of 2 + square root of 2 = 2 * square root of 2
        ir = self._ir(0, 1, 2)
        result = ir + ir
        assert isinstance(result, Irrational)
        assert result.coeff == R(2)

    def test_add_same_radicand_cancels(self):
        # square root of 2 + (-square root of 2) = 0
        ir1 = self._ir(0, 1, 2)
        ir2 = self._ir(0, -1, 2)
        result = ir1 + ir2
        assert result == R(0)

    def test_add_different_radicand_raises(self):
        ir1 = self._ir(0, 1, 2)
        ir2 = self._ir(0, 1, 3)
        with pytest.raises(TypeError):
            ir1 + ir2

    # --- sub ---

    def test_sub_rational(self):
        ir = self._ir(3, 1, 2)
        result = ir - R(1)
        assert result.number == R(2)

    def test_sub_same_radicand(self):
        # 2 * square root of 2 - square root of 2 = square root of 2
        ir1 = self._ir(0, 2, 2)
        ir2 = self._ir(0, 1, 2)
        result = ir1 - ir2
        assert isinstance(result, Irrational)
        assert result.coeff == R(1)

    def test_rsub_rational(self):
        # 5 - square root of 2
        ir = self._ir(0, 1, 2)
        result = 5 - ir
        assert isinstance(result, Irrational)
        assert result.number == R(5)
        assert result.coeff == R(-1)

    # --- mul ---

    def test_mul_rational(self):
        # 3 * square root of 2
        ir = self._ir(0, 1, 2)
        result = ir * R(3)
        assert isinstance(result, Irrational)
        assert result.coeff == R(3)

    def test_rmul_rational(self):
        ir = self._ir(0, 1, 2)
        result = R(3) * ir
        assert result.coeff == R(3)

    def test_mul_zero_returns_rational(self):
        ir = self._ir(0, 1, 2)
        result = ir * R(0)
        assert result == R(0)

    def test_mul_same_radicand(self):
        # square root of 2 * square root of 2 = 2
        ir = self._ir(0, 1, 2)
        result = ir * ir
        assert result == R(2)

    def test_mul_with_rational_part(self):
        # (1 + square root of 2) * (1 + square root of 2) = (1 + 2) + 2 * square root of 2 = 3 + 2 * square root of 2
        ir = Irrational(R(1), R(1), R(2))
        result = ir * ir
        assert isinstance(result, Irrational)
        assert result.number == R(3)
        assert result.coeff == R(2)

    def test_mul_different_radicand_raises(self):
        ir1 = self._ir(0, 1, 2)
        ir2 = self._ir(0, 1, 3)
        with pytest.raises(TypeError):
            ir1 * ir2

    # --- truediv ---

    def test_div_rational(self):
        # 2 * square root of 2 / 2 = square root of 2
        ir = self._ir(0, 2, 2)
        result = ir / R(2)
        assert isinstance(result, Irrational)
        assert result.coeff == R(1)

    def test_div_by_zero_raises(self):
        ir = self._ir(0, 1, 2)
        with pytest.raises(ZeroDivisionError):
            ir / R(0)

    def test_div_same_radicand(self):
        # square root of 2 / square root of 2 = 1
        ir = self._ir(0, 1, 2)
        result = ir / ir
        assert result == R(1)

    def test_rtruediv(self):
        # 2 / square root of 2 = 2 * square root of 2 / 2 = square root of 2
        ir = self._ir(0, 1, 2)
        result = R(2) / ir
        assert isinstance(result, Irrational)
        assert result.coeff == R(1)
        assert result.number == R(0)

    # --- neg ---

    def test_neg(self):
        ir = Irrational(R(3), R(2), R(5))
        neg = -ir
        assert neg.number == R(-3)
        assert neg.coeff == R(-2)
        assert neg.radicand == R(5)


# ---------------------------------------------------------------------------
# Irrational repr
# ---------------------------------------------------------------------------

class TestIrrationalRepr:

    def test_pure_sqrt(self):
        assert repr(Irrational(R(0), R(1), R(2))) == "√2"

    def test_negative_sqrt(self):
        assert repr(Irrational(R(0), R(-1), R(2))) == "-√2"

    def test_coeff_sqrt(self):
        assert repr(Irrational(R(0), R(2), R(3))) == "2 * √3"

    def test_rational_plus_sqrt(self):
        assert repr(Irrational(R(1), R(1), R(2))) == "1 + √2"

    def test_rational_minus_sqrt(self):
        assert repr(Irrational(R(1), R(-1), R(2))) == "1 - √2"