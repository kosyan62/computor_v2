"""
Tests covering every example from en.subject.pdf.
Each test runs the exact input from the subject and checks the output.
"""
import subprocess
import sys
import textwrap
from pathlib import Path

PYTHON = sys.executable
MODULE = "computor_v2.main"


def run(content: str, tmp_path: Path) -> list[str]:
    p = tmp_path / "input.cv2"
    p.write_text(textwrap.dedent(content).strip() + "\n")
    result = subprocess.run(
        [PYTHON, "-m", MODULE, "-f", str(p)],
        capture_output=True, text=True, check=False,
    )
    return [l for l in result.stdout.splitlines() if l.strip()]


# ===========================================================================
# V.2 Assignment part — Rational numbers (p.7)
# ===========================================================================

class TestV2Rational:
    def test_integer(self, tmp_path):
        assert run("varA = 2", tmp_path) == ["2"]

    def test_decimal(self, tmp_path):
        assert run("varB = 4.242", tmp_path) == ["4.242"]

    def test_negative_decimal(self, tmp_path):
        assert run("varC = -4.3", tmp_path) == ["-4.3"]


# ===========================================================================
# V.2 Assignment part — Imaginary numbers (p.7)
# ===========================================================================

class TestV2Imaginary:
    def test_complex_pos(self, tmp_path):
        # subject: varA = 2*i + 3  →  3 + 2i
        assert run("varA = 2*i + 3", tmp_path) == ["3 + 2i"]

    def test_complex_neg(self, tmp_path):
        # subject: varB = -4i - 4  →  -4 - 4i
        assert run("varB = -4i - 4", tmp_path) == ["-4 - 4i"]


# ===========================================================================
# V.2 Assignment part — Matrices (p.7)
# ===========================================================================

class TestV2Matrices:
    def test_2x2(self, tmp_path):
        out = run("varA = [[2,3];[4,3]]", tmp_path)
        assert out == ["[ 2 , 3 ]", "[ 4 , 3 ]"]

    def test_1x2(self, tmp_path):
        out = run("varB = [[3,4]]", tmp_path)
        assert out == ["[ 3 , 4 ]"]

    def test_1x2_spaces(self, tmp_path):
        # subject shows varB=  [[1,2]]  (extra spaces around = and [[)
        out = run("matB=  [[1,2]]", tmp_path)
        assert out == ["[ 1 , 2 ]"]

    def test_3x2(self, tmp_path):
        out = run("matA = [[1,2];[3,2];[3,4]]", tmp_path)
        assert out == ["[ 1 , 2 ]", "[ 3 , 2 ]", "[ 3 , 4 ]"]


# ===========================================================================
# V.2 Assignment part — Functions (p.7)
# ===========================================================================

class TestV2Functions:
    def test_poly(self, tmp_path):
        # funA(x) = 2*x^5 + 4*x^2 - 5*x + 4
        out = run("funA(x) = 2*x^5 + 4*x^2 - 5*x + 4", tmp_path)
        assert len(out) == 1
        s = out[0]
        assert "funA(x)" in s
        assert "x^5" in s
        assert "x^2" in s

    def test_simple_linear(self, tmp_path):
        # funC(z) = -2 * z - 5  →  funC(z) = -2 * z - 5
        out = run("funC(z) = -2 * z - 5", tmp_path)
        assert "funC(z)" in out[0]
        assert "-2 * z - 5" in out[0]

    def test_display_with_spaces(self, tmp_path):
        # subject: funD(x) =    2 *x  →  funD(x) = 2 * x
        out = run("funD(x) =    2 *x", tmp_path)
        assert "funD(x)" in out[0]
        assert "2 * x" in out[0]


# ===========================================================================
# V.2 Reassignment (p.8)
# ===========================================================================

class TestV2Reassign:
    def test_type_change(self, tmp_path):
        # x = 2 → 2; y = x → 2; y = 7 → 7; y = 2*i - 4 → -4 + 2i
        out = run("""
            x = 2
            y = x
            y = 7
            y = 2 * i - 4
        """, tmp_path)
        assert out == ["2", "2", "7", "-4 + 2i"]

    def test_computation_chain(self, tmp_path):
        # Full chain from p.8: varA=27, varB=53, funA, varC=1, varD=239.5
        out = run("""
            varA = 2 + 4 *2 - 5 %4 + 2 * (4 + 5)
            varB = 2 * varA - 5 %4
            funA(x) = varA + varB * 4 - 1 / 2 + x
            varC = 2 * varA - varB
            varD = funA(varC)
        """, tmp_path)
        assert out[0] == "27"
        assert out[1] == "53"
        assert "238.5 + x" in out[2]
        assert out[3] == "1"
        assert out[4] == "239.5"


# ===========================================================================
# V.3 Computational part — basic (p.9)
# ===========================================================================

class TestV3Basic:
    def test_assign_and_query(self, tmp_path):
        # a = 2*4+4 → 12; a+2 = ? → 14
        out = run("""
            a = 2 * 4 + 4
            a + 2 = ?
        """, tmp_path)
        assert out == ["12", "14"]

    def test_image_computation(self, tmp_path):
        # funA(x) = 2*4+x → 8+x; funB(x) = 4-5+(x+2)^2-4;
        # funC(x) = 4x+5-2 → 4*x+3; funA(2)+funB(4)=? → 41; funC(3)=? → 15
        out = run("""
            funA(x) = 2 * 4 + x
            funB(x) = 4 - 5 + (x + 2) ^ 2 - 4
            funC(x) = 4*x + 5 - 2
            funA(2) + funB(4) = ?
            funC(3) = ?
        """, tmp_path)
        assert "8" in out[0] and "x" in out[0]   # funA display
        assert "x" in out[1]                       # funB display
        assert "4" in out[2] and "x" in out[2]    # funC display
        assert out[3] == "41"
        assert out[4] == "15"

    def test_solve_quadratic(self, tmp_path):
        # funA(x) = x^2+2x+1; y=0; funA(x) = y ? → one solution -1
        out = run("""
            funA(x) = x ^ 2 + 2 * x + 1
            y = 0
            funA(x) = y ?
        """, tmp_path)
        assert "One solution" in "\n".join(out)
        assert "-1" in out


# ===========================================================================
# V.3 Solve without function definition
# ===========================================================================

class TestV3SolveDirect:
    def test_linear_direct(self, tmp_path):
        out = run("2*x - 4 = 0 ?", tmp_path)
        assert "One solution" in "\n".join(out)
        assert "2" in out

    def test_quadratic_one_root(self, tmp_path):
        out = run("x^2 + 2*x + 1 = 0 ?", tmp_path)
        assert "One solution" in "\n".join(out)
        assert "-1" in out

    def test_quadratic_two_roots(self, tmp_path):
        out = run("x^2 - 5*x + 6 = 0 ?", tmp_path)
        assert "Two solutions" in "\n".join(out)
        assert "2" in out
        assert "3" in out

    def test_quadratic_complex_roots(self, tmp_path):
        out = run("x^2 + 1 = 0 ?", tmp_path)
        assert "Two solutions" in "\n".join(out)
        assert "i" in "\n".join(out)

    def test_quadratic_irrational_roots(self, tmp_path):
        out = run("x^2 - 2 = 0 ?", tmp_path)
        assert "Two solutions" in "\n".join(out)
        assert "√2" in "\n".join(out)


# ===========================================================================
# V.4.1 Rational / Imaginary syntax (p.10)
# ===========================================================================

class TestV41Rational:
    def test_chain_with_vars(self, tmp_path):
        # varA=2, varB=2*(4+varA+3)=18, varC=2*varB=36,
        # varD=2*(2+4*varC-4/3) = 289.333333333
        out = run("""
            varA = 2
            varB= 2 * (4 + varA + 3)
            varC =2 * varB
            varD = 2 *(2 + 4 *varC -4 /3)
        """, tmp_path)
        assert out[0] == "2"
        assert out[1] == "18"
        assert out[2] == "36"
        assert out[3] == "289.333333333"

    def test_case_insensitive(self, tmp_path):
        # varA and varA (same-case) and VARA should resolve to same
        out = run("""
            varA = 2
            VARA = ?
        """, tmp_path)
        assert out == ["2", "2"]


# ===========================================================================
# V.4.2 Matrices syntax (p.10)
# ===========================================================================

class TestV42Matrices:
    def test_3x2_matrix(self, tmp_path):
        out = run("matA = [[1,2];[3,2];[3,4]]", tmp_path)
        assert out == ["[ 1 , 2 ]", "[ 3 , 2 ]", "[ 3 , 4 ]"]

    def test_1x2_matrix(self, tmp_path):
        assert run("matB = [[1,2]]", tmp_path) == ["[ 1 , 2 ]"]


# ===========================================================================
# V.4.3 Functions syntax (p.11)
# ===========================================================================

class TestV43Functions:
    def test_func_2b_plus_b(self, tmp_path):
        # funA(b) = 2*b+b  →  2 * b + b
        out = run("funA(b) = 2*b+b", tmp_path)
        assert "funA(b)" in out[0]
        assert "b" in out[0]

    def test_func_2a(self, tmp_path):
        # funB(a) =2* a  →  2 * a
        out = run("funB(a) =2* a", tmp_path)
        assert "funB(a)" in out[0]
        assert "2 * a" in out[0]

    def test_func_linear(self, tmp_path):
        # funD(x) =    2 *x  →  2 * x
        out = run("funD(x) =    2 *x", tmp_path)
        assert "funD(x)" in out[0]
        assert "2 * x" in out[0]


# ===========================================================================
# Bonus — function composition (p.12)
# ===========================================================================

class TestBonusFunctionComposition:
    def test_compose_via_call(self, tmp_path):
        # funA(x) = 2*x+1; funB(x) = 2*x+1
        # funA(funB(3)) = funA(7) = 15
        out = run("""
            funA(x) = 2*x + 1
            funB(x) = 2*x + 1
            funA(funB(3)) = ?
        """, tmp_path)
        assert out[-1] == "15"