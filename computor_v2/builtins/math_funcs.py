import math
from computor_v2.types import Rational, Complex, Irrational, BuiltinFunction
from computor_v2.calculus.typed import sqrt as calculus_sqrt
from computor_v2.errors import ComputorTypeError


def _to_float(val) -> float:
    if isinstance(val, Rational):
        return val.numerator / val.denominator
    raise ComputorTypeError(f"Expected a real number, got {type(val).__name__}")


def _from_float(f: float) -> Rational:
    return Rational.from_str(f"{f:.9f}")


def builtin_sqrt(val):
    if not isinstance(val, Rational):
        raise ComputorTypeError(f"sqrt expects a real number, got {type(val).__name__}")
    return calculus_sqrt(val)


def builtin_abs(val):
    if isinstance(val, Rational):
        return abs(val)
    if isinstance(val, Complex):
        return calculus_sqrt(val.re * val.re + val.im * val.im)
    if isinstance(val, Irrational) and isinstance(val.coeff, Rational):
        n = val.number.numerator / val.number.denominator if isinstance(val.number, Rational) else 0.0
        r = val.radicand.numerator / val.radicand.denominator
        c = val.coeff.numerator / val.coeff.denominator
        return val if n + c * math.sqrt(r) >= 0 else -val
    raise ComputorTypeError(f"abs expects a real or complex number, got {type(val).__name__}")


def builtin_sin(val):
    return _from_float(math.sin(_to_float(val)))


def builtin_cos(val):
    return _from_float(math.cos(_to_float(val)))


def builtin_tan(val):
    return _from_float(math.tan(_to_float(val)))


def builtin_exp(val):
    return _from_float(math.exp(_to_float(val)))


BUILTINS = {
    "sqrt": BuiltinFunction("sqrt", builtin_sqrt),
    "abs":  BuiltinFunction("abs",  builtin_abs),
    "sin":  BuiltinFunction("sin",  builtin_sin),
    "cos":  BuiltinFunction("cos",  builtin_cos),
    "tan":  BuiltinFunction("tan",  builtin_tan),
    "exp":  BuiltinFunction("exp",  builtin_exp),
}