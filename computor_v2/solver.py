from __future__ import annotations
from computor_v2.polynomial import Polynomial
from computor_v2.types import Rational
from computor_v2.calculus.typed import sqrt as calc_sqrt
from computor_v2.errors import ComputorSolverError

R = Rational


def _sort_key(val) -> tuple:
    """Numeric sort key for solutions: (re, im) approximation."""
    from computor_v2.types import Rational, Complex, Irrational
    if isinstance(val, Rational):
        return (val.numerator / val.denominator, 0)
    if isinstance(val, Complex):
        return (val.re.numerator / val.re.denominator, val.im.numerator / val.im.denominator)
    if isinstance(val, Irrational):
        import math
        r = val.radicand.numerator / val.radicand.denominator
        n = val.number.numerator / val.number.denominator if isinstance(val.number, Rational) else 0
        if isinstance(val.coeff, Complex):
            # Complex irrational: sort by (re_approx, im_approx)
            im_c = val.coeff.im.numerator / val.coeff.im.denominator
            return (n, im_c * math.sqrt(r))
        c = val.coeff.numerator / val.coeff.denominator
        return (n + c * math.sqrt(r), 0)
    return (0, 0)


class SolveResult:
    def __init__(self, solutions: list, count: int | float):
        self.solutions = solutions
        self.count = count

    def __repr__(self) -> str:
        return f"SolveResult(count={self.count}, solutions={self.solutions})"

    def __eq__(self, other) -> bool:
        if isinstance(other, SolveResult):
            return self.count == other.count and self.solutions == other.solutions
        return NotImplemented


NO_SOLUTION        = SolveResult([], 0)
INFINITE_SOLUTIONS = SolveResult([], float("inf"))


class PolynomialSolver:

    @staticmethod
    def solve(poly: Polynomial) -> SolveResult:
        match poly.degree:
            case 0: return ZeroSolver(poly).solve()
            case 1: return LinearSolver(poly).solve()
            case 2: return QuadraticSolver(poly).solve()
            case _:
                raise ComputorSolverError(
                    f"Polynomial degree {poly.degree} is not supported (max: 2)"
                )


class ZeroSolver:
    def __init__(self, poly: Polynomial):
        self.poly = poly

    def solve(self) -> SolveResult:
        if self.poly.coefficient(0) == R(0):
            return INFINITE_SOLUTIONS
        return NO_SOLUTION


class LinearSolver:
    def __init__(self, poly: Polynomial):
        self.a = poly.coefficient(1)
        self.b = poly.coefficient(0)

    def solve(self) -> SolveResult:
        if self.a == R(0):
            return INFINITE_SOLUTIONS if self.b == R(0) else NO_SOLUTION
        return SolveResult([-self.b / self.a], 1)


class QuadraticSolver:
    def __init__(self, poly: Polynomial):
        self.a = poly.coefficient(2)
        self.b = poly.coefficient(1)
        self.c = poly.coefficient(0)

    @property
    def discriminant(self) -> Rational:
        return self.b * self.b - R(4) * self.a * self.c

    def solve(self) -> SolveResult:
        a, b = self.a, self.b
        d = self.discriminant

        if d == R(0):
            return SolveResult([-b / (R(2) * a)], 1)

        sqrt_d = calc_sqrt(d)
        x1 = (-b + sqrt_d) / (R(2) * a)
        x2 = (-b - sqrt_d) / (R(2) * a)
        return SolveResult(sorted([x1, x2], key=_sort_key), 2)