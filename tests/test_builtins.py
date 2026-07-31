
from computor_v2.builtins import BUILTINS
from computor_v2.types import Complex, Rational

# ---------------------------------------------------------------------------
# Builtins
# ---------------------------------------------------------------------------

class TestBuiltins:

    def test_i_is_complex(self):
        assert BUILTINS["i"] == Complex(Rational(0), Rational(1))

    def test_abs_rational(self):
        assert BUILTINS["abs"].call(Rational(-5)) == Rational(5)

    def test_abs_complex(self):
        # |3 + 4i| = 5
        assert BUILTINS["abs"].call(Complex(Rational(3), Rational(4))) == Rational(5)

    def test_abs_pure_imaginary(self):
        # |5i| = 5
        assert BUILTINS["abs"].call(Complex(Rational(0), Rational(5))) == Rational(5)
