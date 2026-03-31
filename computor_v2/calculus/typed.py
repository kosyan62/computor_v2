from __future__ import annotations
from computor_v2.types import Rational, Complex, Irrational
from computor_v2.calculus.pure import factor_sqrt


def sqrt(val: Rational) -> Rational | Complex | Irrational:
    """Return exact square root of val.

    - Perfect square  → Rational
    - Negative perfect square → Complex (pure imaginary)
    - Non-perfect square  → Irrational
    - Negative non-perfect square → Irrational with complex coeff (i * sqrt(|val|))
    """
    if not isinstance(val, Rational):
        raise TypeError(f"sqrt expects Rational, got {type(val).__name__}")
    if val == Rational(0):
        return Rational(0)

    negative = val < Rational(0)
    pos_val = -val if negative else val

    p, q = pos_val.numerator, pos_val.denominator
    c, r = factor_sqrt(p * q)

    if r == 1:
        # sqrt(pos_val) is exact Rational c/q
        result = Rational(c, q)
        if negative:
            return Complex(Rational(0), result)
        return result
    else:
        # sqrt(pos_val) is irrational: (c/q) * sqrt(r)
        coeff = Rational(c, q)
        if negative:
            # i * (c/q) * sqrt(r)
            coeff = Complex(Rational(0), coeff)
        return Irrational(Rational(0), coeff, Rational(r))