import pytest
from computor_v2.polynomial import Polynomial
from computor_v2.types import Rational, Complex, Irrational
from computor_v2.errors import ComputorSolverError
from computor_v2.solver import PolynomialSolver, SolveResult

R = Rational


def solve(coeffs: dict) -> SolveResult:
    return PolynomialSolver.solve(Polynomial(coeffs))


# ---------------------------------------------------------------------------
# Degree 0
# ---------------------------------------------------------------------------

class TestZeroSolver:

    def test_identity(self):
        result = solve({})
        assert result.count == float("inf")
        assert result.solutions == []

    def test_contradiction(self):
        result = solve({0: R(5)})
        assert result.count == 0
        assert result.solutions == []


# ---------------------------------------------------------------------------
# Degree 1
# ---------------------------------------------------------------------------

class TestLinearSolver:

    def test_simple(self):
        # 2x - 6 = 0  →  x = 3
        result = solve({1: R(2), 0: R(-6)})
        assert result.count == 1
        assert result.solutions == [R(3)]

    def test_unit_coeff(self):
        # x - 2 = 0  →  x = 2
        assert solve({1: R(1), 0: R(-2)}).solutions == [R(2)]

    def test_negative_result(self):
        # x + 4 = 0  →  x = -4
        assert solve({1: R(1), 0: R(4)}).solutions == [R(-4)]

    def test_negative_coeff(self):
        # -x - 4 = 0  →  x = -4
        assert solve({1: R(-1), 0: R(-4)}).solutions == [R(-4)]

    def test_fractional_result(self):
        # 3x - 1 = 0  →  x = 1/3
        assert solve({1: R(3), 0: R(-1)}).solutions == [R(1, 3)]

    def test_zero_result(self):
        assert solve({1: R(1)}).solutions == [R(0)]

    def test_large_coeff(self):
        # 2x - 96 = 0  →  x = 48
        assert solve({1: R(2), 0: R(-96)}).solutions == [R(48)]

    def test_negative_result_2(self):
        # 3x + 6 = 0  →  x = -2
        assert solve({1: R(3), 0: R(6)}).solutions == [R(-2)]

    def test_identity(self):
        result = solve({1: R(0), 0: R(0)})
        assert result.count == float("inf")

    def test_contradiction(self):
        result = solve({1: R(0), 0: R(5)})
        assert result.count == 0


# ---------------------------------------------------------------------------
# Degree 2
# ---------------------------------------------------------------------------

class TestQuadraticSolver:

    # --- D > 0, rational roots ---

    def test_two_rational_roots(self):
        # x^2 - 3x + 2 = 0  →  x=1, x=2
        result = solve({2: R(1), 1: R(-3), 0: R(2)})
        assert result.count == 2
        assert set(result.solutions) == {R(1), R(2)}

    def test_two_rational_roots_with_coeff(self):
        # 2x^2 - 6x + 4 = 0  →  x=1, x=2
        result = solve({2: R(2), 1: R(-6), 0: R(4)})
        assert set(result.solutions) == {R(1), R(2)}

    def test_negative_roots(self):
        # x^2 + 5x + 6 = 0  →  x=-2, x=-3
        result = solve({2: R(1), 1: R(5), 0: R(6)})
        assert set(result.solutions) == {R(-2), R(-3)}

    def test_one_positive_one_negative(self):
        # x^2 - x - 6 = 0  →  x=3, x=-2
        result = solve({2: R(1), 1: R(-1), 0: R(-6)})
        assert set(result.solutions) == {R(3), R(-2)}

    def test_fractional_roots(self):
        # 2x^2 - 3x + 1 = 0  →  x=1/2, x=1
        result = solve({2: R(2), 1: R(-3), 0: R(1)})
        assert set(result.solutions) == {R(1, 2), R(1)}

    # --- D = 0, one root ---

    def test_one_root_zero(self):
        # x^2 = 0  →  x = 0
        result = solve({2: R(1)})
        assert result.count == 1
        assert result.solutions == [R(0)]

    def test_one_root_nonzero(self):
        # x^2 - 2x + 1 = 0  →  (x-1)^2  →  x = 1
        result = solve({2: R(1), 1: R(-2), 0: R(1)})
        assert result.count == 1
        assert result.solutions == [R(1)]

    def test_one_root_negative(self):
        # x^2 + 4x + 4 = 0  →  (x+2)^2  →  x = -2
        result = solve({2: R(1), 1: R(4), 0: R(4)})
        assert result.count == 1
        assert result.solutions == [R(-2)]

    # --- D < 0, complex roots ---

    def test_complex_roots(self):
        # 6x^2 + 6x + 3 = 0  →  D = -36
        result = solve({2: R(6), 1: R(6), 0: R(3)})
        assert result.count == 2
        assert all(isinstance(r, Complex) for r in result.solutions)
        r1, r2 = result.solutions
        assert r1.re == r2.re
        assert r1.im == -r2.im

    def test_complex_roots_unit(self):
        # x^2 + 1 = 0  →  x = ±i
        result = solve({2: R(1), 0: R(1)})
        assert set(result.solutions) == {Complex(R(0), R(1)), Complex(R(0), R(-1))}

    def test_complex_roots_with_real_part(self):
        # x^2 + x + 1 = 0  →  D = -3
        result = solve({2: R(1), 1: R(1), 0: R(1)})
        assert result.count == 2
        assert all(isinstance(r, (Complex, Irrational)) for r in result.solutions)

    # --- D > 0, irrational roots ---

    def test_irrational_roots(self):
        # x^2 - 2 = 0  →  x = ±√2
        result = solve({2: R(1), 0: R(-2)})
        assert result.count == 2
        assert all(isinstance(r, Irrational) for r in result.solutions)

    def test_irrational_roots_with_b(self):
        # x^2 - 2x - 1 = 0  →  D = 8  →  x = 1 ± √2
        result = solve({2: R(1), 1: R(-2), 0: R(-1)})
        assert result.count == 2
        assert all(isinstance(r, Irrational) for r in result.solutions)

    # --- degree > 2 ---

    def test_degree_3_raises(self):
        with pytest.raises(ComputorSolverError, match="degree"):
            solve({3: R(1), 0: R(-1)})

    def test_degree_4_raises(self):
        with pytest.raises(ComputorSolverError, match="degree"):
            solve({4: R(1)})
