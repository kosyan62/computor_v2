from __future__ import annotations
from computor_v2.types import Scalar, Complex, Rational, BuiltinFunction
from computor_v2.computor_math import sqrt as _sqrt
from computor_v2.errors import ComputorTypeError


def _builtin_sqrt(val):
    if not isinstance(val, Rational):
        raise ComputorTypeError(f"sqrt expects a real number, got {type(val).__name__}")
    return _sqrt(val)


def _builtin_abs(val):
    if isinstance(val, Rational):
        return abs(val)
    raise ComputorTypeError(f"abs expects a real number, got {type(val).__name__}")


BUILTINS: dict[str, Scalar|BuiltinFunction] = {
    "i":    Complex(Rational(0), Rational(1)),
    "sqrt": BuiltinFunction("sqrt", _builtin_sqrt),
    "abs":  BuiltinFunction("abs",  _builtin_abs),
}