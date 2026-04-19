from __future__ import annotations
from computor_v2.types import Rational, Complex, Irrational, Matrix, Function, BuiltinFunction
from computor_v2.polynomial import Polynomial
from computor_v2.parsing.AST import (
    NumberNode, VariableNode, UnaryMinusNode, UnaryPlusNode,
    BinaryOperationNode, FunctionCallNode,
)


def fmt_rational(r: Rational) -> str:
    """Format Rational: integer if whole, terminating decimal if possible, else fraction."""
    if r.denominator == 1:
        return str(r.numerator)
    d = r.denominator
    tmp = d
    while tmp % 2 == 0:
        tmp //= 2
    while tmp % 5 == 0:
        tmp //= 5
    if tmp == 1:
        # Terminating decimal — find number of decimal places
        a, b = 0, 0
        t = d
        while t % 2 == 0:
            t //= 2
            a += 1
        t = d
        while t % 5 == 0:
            t //= 5
            b += 1
        places = max(a, b)
        sign = "-" if r.numerator < 0 else ""
        total = abs(r.numerator) * (10 ** places) // d
        int_part = total // (10 ** places)
        frac_part = total % (10 ** places)
        frac_str = str(frac_part).zfill(places)
        return f"{sign}{int_part}.{frac_str}"
    # Non-terminating: show as 9-decimal-place approximation
    from decimal import Decimal, getcontext
    getcontext().prec = 20
    val = Decimal(r.numerator) / Decimal(r.denominator)
    s = f"{val:.9f}"
    return s.rstrip("0").rstrip(".")


def fmt_complex(c: Complex) -> str:
    """Format Complex as 'a + bi' with sign handling."""
    im = c.im
    if im == Rational(0):
        return fmt_rational(c.re) if c.re != Rational(0) else "0"

    # Format imaginary part magnitude
    if im == Rational(1):
        im_abs_str = "i"
    elif im == Rational(-1):
        im_abs_str = "i"
    else:
        im_abs_str = f"{fmt_rational(abs(im))}i"

    im_positive = im > Rational(0)

    if c.re == Rational(0):
        return im_abs_str if im_positive else f"-{im_abs_str}"

    re_str = fmt_rational(c.re)
    if im_positive:
        return f"{re_str} + {im_abs_str}"
    return f"{re_str} - {im_abs_str}"


def fmt_irrational(irr: Irrational) -> str:
    """Format Irrational as '(n ± c√r) / d' using same-denominator convention."""
    r = irr.radicand.numerator  # radicand is always a positive integer after normalization
    sqrt_str = f"√{r}"

    is_complex_coeff = isinstance(irr.coeff, Complex)

    if is_complex_coeff:
        c_im: Rational = irr.coeff.im
        c_numer = c_im.numerator
        d = c_im.denominator
        abs_c = abs(c_numer)
        positive = c_numer > 0
        sqrt_part = f"{sqrt_str} * i" if abs_c == 1 else f"{abs_c}{sqrt_str} * i"
    else:
        c: Rational = irr.coeff
        c_numer = c.numerator
        d = c.denominator
        abs_c = abs(c_numer)
        positive = c_numer > 0
        sqrt_part = sqrt_str if abs_c == 1 else f"{abs_c}{sqrt_str}"

    number_zero = irr.number == Rational(0)

    if number_zero:
        signed_sqrt = sqrt_part if positive else f"-{sqrt_part}"
        return signed_sqrt if d == 1 else f"{signed_sqrt} / {d}"

    if isinstance(irr.number, Complex):
        n_str = fmt_complex(irr.number)
        inner = f"{n_str} + {sqrt_part}" if positive else f"{n_str} - {sqrt_part}"
    else:
        n_numer = irr.number.numerator  # denominator == d in practice
        inner = f"{n_numer} + {sqrt_part}" if positive else f"{n_numer} - {sqrt_part}"
    return inner if d == 1 else f"({inner}) / {d}"


_PREC = {"+": 1, "-": 1, "*": 2, "/": 2, "//": 2, "%": 2, "^": 3, "**": 3}
_SPACED = {"+", "-", "*", "/", "//", "%"}  # ^ gets no surrounding spaces


def _op_prec(op: str) -> int:
    return _PREC.get(op, 0)


def fmt_ast(node) -> str:
    """Walk a simplified AST and produce infix string."""
    if isinstance(node, NumberNode):
        v = str(node.value)
        if "/" in v:
            n, d = v.split("/")
            return fmt_rational(Rational(int(n), int(d)))
        return fmt_rational(Rational.from_str(v))

    if isinstance(node, VariableNode):
        return node.value

    if isinstance(node, UnaryMinusNode):
        inner = fmt_ast(node.operand)
        if isinstance(node.operand, BinaryOperationNode):
            return f"-({inner})"
        return f"-{inner}"

    if isinstance(node, UnaryPlusNode):
        return fmt_ast(node.operand)

    if isinstance(node, BinaryOperationNode):
        left_s = fmt_ast(node.left)
        right_s = fmt_ast(node.right)
        p = _op_prec(node.op)

        if isinstance(node.left, BinaryOperationNode) and _op_prec(node.left.op) < p:
            left_s = f"({left_s})"
        if isinstance(node.right, BinaryOperationNode):
            rp = _op_prec(node.right.op)
            if rp < p or (rp == p and node.op in ("-", "/", "//", "%", "^")):
                right_s = f"({right_s})"

        sep = " " if node.op in _SPACED else ""
        return f"{left_s}{sep}{node.op}{sep}{right_s}"

    if isinstance(node, FunctionCallNode):
        args = ", ".join(fmt_ast(a) for a in node.args)
        return f"{node.func_name}({args})"

    return repr(node)


def fmt_function(f: Function) -> str:
    """Format a Function as '(param) = body'."""
    return f"({f.param}) = {fmt_ast(f.body)}"


def fmt_matrix(m: Matrix) -> str:
    """Format Matrix as '[ v1 , v2 ]' per row, rows separated by newlines."""
    rows = []
    for row in m.rows:
        cells = " , ".join(fmt(cell) for cell in row)
        rows.append(f"[ {cells} ]")
    return "\n".join(rows)


def fmt_polynomial(poly: Polynomial, var: str) -> str:
    """Format Polynomial as descending-degree string: '5x^2 - 3x + 2'."""
    if not poly._coeffs:
        return "0"

    terms = []
    for degree in sorted(poly._coeffs.keys(), reverse=True):
        coeff: Rational = poly._coeffs[degree]
        abs_coeff = Rational(abs(coeff.numerator), coeff.denominator)
        abs_c_str = fmt_rational(abs_coeff)
        positive = coeff > Rational(0)

        if degree == 0:
            term = fmt_rational(coeff)
        elif degree == 1:
            if abs_coeff == Rational(1):
                term = var if positive else f"-{var}"
            else:
                term = f"{abs_c_str}{var}" if positive else f"-{abs_c_str}{var}"
        else:
            if abs_coeff == Rational(1):
                term = f"{var}^{degree}" if positive else f"-{var}^{degree}"
            else:
                term = f"{abs_c_str}{var}^{degree}" if positive else f"-{abs_c_str}{var}^{degree}"

        terms.append(term)

    result = terms[0]
    for term in terms[1:]:
        if term.startswith("-"):
            result += f" - {term[1:]}"
        else:
            result += f" + {term}"
    return result


def _is_complex_valued(val) -> bool:
    """True if val has a non-zero imaginary component."""
    if isinstance(val, Complex):
        return val.im != Rational(0)
    if isinstance(val, Irrational) and isinstance(val.coeff, Complex):
        return True
    return False


def fmt_solve(result, poly: Polynomial, var: str) -> str:
    """Format full solve output: reduced form + header + solutions."""
    lines = [f"{fmt_polynomial(poly, var)} = 0"]

    if result.count == 0:
        lines.append("No solution.")
    elif result.count == float("inf"):
        lines.append("Infinite solutions.")
    else:
        any_complex = any(_is_complex_valued(s) for s in result.solutions)
        field = "ℂ" if any_complex else "ℝ"
        count_word = "One" if result.count == 1 else "Two"
        plural = "s" if result.count > 1 else ""
        lines.append(f"{count_word} solution{plural} in {field}:")
        for sol in result.solutions:
            lines.append(fmt(sol))

    return "\n".join(lines)


def fmt(val) -> str:
    """Main dispatcher — format any computor_v2 value for display."""
    if isinstance(val, Irrational):
        return fmt_irrational(val)
    if isinstance(val, Complex):
        return fmt_complex(val)
    if isinstance(val, Rational):
        return fmt_rational(val)
    if isinstance(val, Matrix):
        return fmt_matrix(val)
    if isinstance(val, (Function, BuiltinFunction)):
        return fmt_function(val)
    return str(val)
