from __future__ import annotations

import math

from computor_v2.errors import ComputorTypeError
from computor_v2.parsing.AST import (
    BinaryOperationNode,
    FunctionCallNode,
    NumberNode,
    UnaryMinusNode,
    UnaryPlusNode,
    VariableNode,
)
from computor_v2.store import Store
from computor_v2.types import BuiltinFunction, Function, Irrational, Rational


def _val_to_float(val) -> float:
    if isinstance(val, Rational):
        return val.numerator / val.denominator
    if isinstance(val, Irrational):
        n = val.number.numerator / val.number.denominator if isinstance(val.number, Rational) else 0.0
        r = val.radicand.numerator / val.radicand.denominator
        if isinstance(val.coeff, Rational):
            return n + (val.coeff.numerator / val.coeff.denominator) * math.sqrt(r)
    raise ComputorTypeError(f"Cannot plot: function returns {type(val).__name__}, expected a real number")


def _float_eval(node, param: str, x: float, store: Store) -> float:
    """Evaluate AST node as Python float — used only for plotting."""
    if isinstance(node, NumberNode):
        return float(node.value)
    if isinstance(node, VariableNode):
        if node.value.lower() == param.lower():
            return x
        return _val_to_float(store.get(node.value))
    if isinstance(node, UnaryMinusNode):
        return -_float_eval(node.operand, param, x, store)
    if isinstance(node, UnaryPlusNode):
        return _float_eval(node.operand, param, x, store)
    if isinstance(node, BinaryOperationNode):
        left = _float_eval(node.left, param, x, store)
        right = _float_eval(node.right, param, x, store)
        match node.op:
            case "+":  return left + right
            case "-":  return left - right
            case "*":  return left * right
            case "/":  return left / right if right != 0 else float("nan")
            case "^":
                res = left ** right
                return res if isinstance(res, float) else float("nan")
            case "%":  return math.fmod(left, right) if right != 0 else float("nan")
            case "//": return math.floor(left / right) if right != 0 else float("nan")
            case "**": return float("nan")
    if isinstance(node, FunctionCallNode):
        try:
            inner = store.get(node.func_name)
        except Exception:
            return float("nan")
        arg = _float_eval(node.args[0], param, x, store)
        if isinstance(inner, BuiltinFunction):
            try:
                return _val_to_float(inner.call(Rational.from_str(f"{arg:.9f}")))
            except Exception:
                return float("nan")
        if isinstance(inner, Function):
            return _float_eval(inner.body, inner.param, arg, store)
    return float("nan")


def plot_function(func: Function, func_name: str, store: Store,
                  x_min: float = -10.0, x_max: float = 10.0, n_points: int = 500):
    try:
        import matplotlib
        _CANDIDATES = [
            ("PyQt6",  "Qt6Agg"),
            ("PyQt5",  "Qt5Agg"),
            ("PySide6","Qt6Agg"),
            ("PySide2","Qt5Agg"),
            ("gi",     "GTK4Agg"),
            ("wx",     "WXAgg"),
        ]
        for _mod, _backend in _CANDIDATES:
            try:
                __import__(_mod)
                matplotlib.use(_backend)
                break
            except ImportError:
                continue
        import matplotlib.pyplot as plt
    except ImportError:
        raise ComputorTypeError("matplotlib is not installed; run: uv add matplotlib")

    xs = [x_min + (x_max - x_min) * i / n_points for i in range(n_points + 1)]
    ys = []
    for x in xs:
        try:
            y = _float_eval(func.body, func.param, x, store)
            ys.append(y)
        except Exception:
            ys.append(float("nan"))

    # Break the curve at poles: a sign flip between two huge neighbours is an
    # asymptote crossing, not a real segment — matplotlib must not connect it.
    finite = sorted(abs(y) for y in ys if math.isfinite(y))
    cutoff = 10 * finite[len(finite) // 2] if finite else 0.0
    if cutoff > 0:
        for i in range(1, len(ys)):
            a, b = ys[i - 1], ys[i]
            if (math.isfinite(a) and math.isfinite(b) and a * b < 0
                    and abs(a) > cutoff and abs(b) > cutoff):
                ys[i] = float("nan")

    _fig, ax = plt.subplots()
    ax.plot(xs, ys, linewidth=1.5)
    ax.axhline(0, color="black", linewidth=0.5)
    ax.axvline(0, color="black", linewidth=0.5)
    ax.set_xlabel("x")
    ax.set_ylabel(f"{func_name}(x)")
    ax.set_title(f"{func_name}(x)")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show(block=False)