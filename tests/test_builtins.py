import pytest

from computor_v2.types import Complex, Rational
from computor_v2.builtins import BUILTINS
from computor_v2.errors import ComputorTypeError
# ---------------------------------------------------------------------------
# Builtins
# ---------------------------------------------------------------------------

class TestBuiltins:

    def test_i_is_complex(self):
        assert BUILTINS["i"] == Complex(Rational(0), Rational(1))

    def test_abs_rational(self):
        assert BUILTINS["abs"].call(Rational(-5)) == Rational(5)

    def test_abs_complex_raises(self):
        with pytest.raises(ComputorTypeError):
            BUILTINS["abs"].call(Complex(Rational(3), Rational(4)))
