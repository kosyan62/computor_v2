from __future__ import annotations

from computor_v2.types import Rational

R = Rational


class Polynomial:
    """Immutable polynomial over Rational coefficients."""

    def __init__(self, coeffs: dict[int, Rational]):
        self._coeffs = {k: v for k, v in coeffs.items() if v != R(0)}

    @property
    def degree(self) -> int:
        return max(self._coeffs.keys(), default=0)

    def coefficient(self, n: int) -> Rational:
        return self._coeffs.get(n, R(0))

    def __repr__(self) -> str:
        if not self._coeffs:
            return "0"
        terms = []
        for deg in sorted(self._coeffs.keys(), reverse=True):
            c = self._coeffs[deg]
            if deg == 0:
                terms.append(str(c))
            elif deg == 1:
                terms.append(f"{c}*x")
            else:
                terms.append(f"{c}*x^{deg}")
        return " + ".join(terms)

    def __contains__(self, degree: int) -> bool:
        return degree in self._coeffs

    def __eq__(self, other) -> bool:
        if isinstance(other, Polynomial):
            return self._coeffs == other._coeffs
        if isinstance(other, dict):
            return self._coeffs == {k: v for k, v in other.items() if v != R(0)}
        return NotImplemented