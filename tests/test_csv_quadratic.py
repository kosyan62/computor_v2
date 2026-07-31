"""
Integration tests using quadratic_test_data.json (converted from computor v1 CSV dataset).
10000 equations total: real roots, complex roots, repeated roots.
All comparisons are exact (no float approximation).
"""
import json
import os
import re

import pytest

from computor_v2.normalizer import Normalizer
from computor_v2.parsing.parser import parser
from computor_v2.solver import PolynomialSolver, _sort_key
from computor_v2.store import Store
from computor_v2.types import Complex, Irrational, Rational

JSON_PATH = os.path.join(os.path.dirname(__file__), "quadratic_test_data.json")


def load_dataset():
    with open(JSON_PATH) as f:
        return json.load(f)


def solve_lhs(lhs: str):
    node = parser.parse(lhs)
    poly = Normalizer(Store()).to_polynomial(node, "x")
    return PolynomialSolver.solve(poly)


# ---------------------------------------------------------------------------
# Exact root parser  (parses sympy-style strings like '-5/16 - sqrt(39)*I/16')
# ---------------------------------------------------------------------------

def _make_rational(s: str) -> Rational:
    s = s.strip().replace(" ", "")
    if "/" in s:
        n, d = s.split("/")
        return Rational(int(n), int(d))
    return Rational(int(s))


def _split_terms(expr: str) -> list[str]:
    """Split 'a - b + c' into ['+a', '-b', '+c'], respecting parentheses."""
    expr = expr.strip()
    if not expr.startswith("-"):
        expr = "+" + expr
    terms, current, depth = [], "", 0
    for ch in expr:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch in "+-" and depth == 0 and current:
            terms.append(current)
            current = ch
        else:
            current += ch
    if current:
        terms.append(current)
    return terms


_SQRT_RE = re.compile(
    r"^([+-]?)\s*"            # optional sign
    r"(?:(\d+)\*)?\s*"        # optional integer multiplier
    r"sqrt\((\d+)\)"          # sqrt(radicand)
    r"(\*I)?"                 # optional *I
    r"(?:/(\d+))?$"           # optional /denom
)

_IMAG_RE = re.compile(
    r"^([+-]?)\s*"            # optional sign
    r"(?:(\d+)\*)?\s*"        # optional integer multiplier (e.g. 4*)
    r"I"                      # imaginary unit
    r"(?:/(\d+))?$"           # optional /denom
)


def parse_single_root(expr: str):
    """Parse one root expression (the part after 'x = ') into Rational, Complex, or Irrational."""
    terms = _split_terms(expr)
    rational_total = Rational(0)
    imag_total = Rational(0)
    sqrt_coeff_r = None
    radicand_r = None
    is_imag = False

    for term in terms:
        term_clean = term.replace(" ", "")
        m_sqrt = _SQRT_RE.match(term_clean)
        m_imag = _IMAG_RE.match(term_clean)
        if m_sqrt:
            sign = -1 if m_sqrt.group(1) == "-" else 1
            numer = int(m_sqrt.group(2)) if m_sqrt.group(2) else 1
            rad = int(m_sqrt.group(3))
            is_imag = bool(m_sqrt.group(4))
            denom = int(m_sqrt.group(5)) if m_sqrt.group(5) else 1
            sqrt_coeff_r = Rational(sign * numer, denom)
            radicand_r = Rational(rad)
        elif m_imag:
            sign = -1 if m_imag.group(1) == "-" else 1
            numer = int(m_imag.group(2)) if m_imag.group(2) else 1
            denom = int(m_imag.group(3)) if m_imag.group(3) else 1
            imag_total = imag_total + Rational(sign * numer, denom)
        else:
            rational_total = rational_total + _make_rational(term)

    if sqrt_coeff_r is not None:
        coeff = Complex(Rational(0), sqrt_coeff_r) if is_imag else sqrt_coeff_r
        return Irrational(rational_total, coeff, radicand_r)

    if imag_total != Rational(0):
        return Complex(rational_total, imag_total)

    return rational_total


def parse_csv_roots(roots_raw: str) -> list:
    """Parse 'x = a, x = b' into a sorted list of our types."""
    parts = re.split(r",\s*x\s*=\s*", roots_raw)
    parts[0] = re.sub(r"^x\s*=\s*", "", parts[0])
    parsed = [parse_single_root(p) for p in parts]
    return sorted(parsed, key=_sort_key)


# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------

dataset = load_dataset()

real_cases     = [(e["lhs"], e["roots_raw"]) for e in dataset if e["type"] == "real"]
repeated_cases = [(e["lhs"], e["roots_raw"]) for e in dataset if e["type"] == "repeated"]
complex_cases  = [(e["lhs"], e["roots_raw"]) for e in dataset if e["type"] == "complex"]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("lhs,roots_raw", real_cases)
def test_real_distinct_roots(lhs, roots_raw):
    result = solve_lhs(lhs)
    assert result.count == 2
    expected = parse_csv_roots(roots_raw)
    actual = sorted(result.solutions, key=_sort_key)
    assert actual == expected, (
        f"lhs={lhs!r}:\n  expected {expected}\n  got      {actual}"
    )


@pytest.mark.parametrize("lhs,roots_raw", repeated_cases)
def test_repeated_root(lhs, roots_raw):
    result = solve_lhs(lhs)
    assert result.count == 1
    expected = parse_csv_roots(roots_raw)
    assert result.solutions == expected, (
        f"lhs={lhs!r}:\n  expected {expected}\n  got      {result.solutions}"
    )


@pytest.mark.parametrize("lhs,roots_raw", complex_cases)
def test_complex_roots(lhs, roots_raw):
    result = solve_lhs(lhs)
    assert result.count == 2
    expected = parse_csv_roots(roots_raw)
    actual = sorted(result.solutions, key=_sort_key)
    assert actual == expected, (
        f"lhs={lhs!r}:\n  expected {expected}\n  got      {actual}"
    )
