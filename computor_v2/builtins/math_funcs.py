from computor_v2.types import Rational, Complex, BuiltinFunction
from computor_v2.calculus.typed import sqrt as calculus_sqrt
from computor_v2.errors import ComputorTypeError


def builtin_sqrt(val):
    if not isinstance(val, Rational):
        raise ComputorTypeError(f"sqrt expects a real number, got {type(val).__name__}")
    return calculus_sqrt(val)


def builtin_abs(val):
    if isinstance(val, Rational):
        return abs(val)
    if isinstance(val, Complex):
        # |a + bi| = sqrt(a^2 + b^2)
        return calculus_sqrt(val.re * val.re + val.im * val.im)
    raise ComputorTypeError(f"abs expects a real or complex number, got {type(val).__name__}")


BUILTINS = {
    "sqrt": BuiltinFunction("sqrt", builtin_sqrt),
    "abs":  BuiltinFunction("abs",  builtin_abs),
}