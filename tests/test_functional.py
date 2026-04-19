"""Functional tests: run the interpreter as a subprocess via -f and stdin."""
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

PYTHON = sys.executable
MODULE = "computor_v2.main"


def run_file(content: str, extra_args: list[str] | None = None, tmp_path=None) -> str:
    """Write content to a temp file and run with -f. Returns stdout."""
    p = tmp_path / "input.cv2"
    p.write_text(textwrap.dedent(content))
    args = [PYTHON, "-m", MODULE, "-f", str(p)] + (extra_args or [])
    result = subprocess.run(args, capture_output=True, text=True)
    return result.stdout.strip()


def run_stdin(content: str) -> str:
    """Feed content line-by-line via stdin REPL. Returns stdout (minus prompts)."""
    lines = textwrap.dedent(content).strip() + "\nexit\n"
    result = subprocess.run(
        [PYTHON, "-m", MODULE],
        input=lines,
        capture_output=True,
        text=True,
    )
    # Strip the '> ' prompts and trailing "See you later!" from REPL output
    output_lines = []
    for line in result.stdout.splitlines():
        stripped = line.lstrip("> ").strip()
        if stripped and stripped not in ("See you later!", "Bye!"):
            output_lines.append(stripped)
    return "\n".join(output_lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def lines(out: str) -> list[str]:
    return [l for l in out.splitlines() if l.strip()]


# ===========================================================================
# 1. Variable assignment
# ===========================================================================

class TestAssignFile:
    def test_integer(self, tmp_path):
        out = run_file("x = 42\nx = ?", tmp_path=tmp_path)
        assert lines(out) == ["42", "42"]

    def test_decimal(self, tmp_path):
        out = run_file("x = 4.242\nx = ?", tmp_path=tmp_path)
        assert lines(out) == ["4.242", "4.242"]

    def test_fraction_result(self, tmp_path):
        out = run_file("x = 1 / 3\nx = ?", tmp_path=tmp_path)
        assert lines(out) == ["1/3", "1/3"]

    def test_expression(self, tmp_path):
        out = run_file("x = 2 + 3\ny = x * 4\ny = ?", tmp_path=tmp_path)
        assert "20" in out

    def test_chained_assign(self, tmp_path):
        out = run_file("a = 2\nb = a * 3\nc = b + 1\nc = ?", tmp_path=tmp_path)
        assert "7" in out

    def test_reassign(self, tmp_path):
        out = run_file("x = 5\nx = 10\nx = ?", tmp_path=tmp_path)
        assert lines(out)[-1] == "10"


class TestAssignStdin:
    def test_basic(self):
        out = run_stdin("x = 7\nx = ?")
        assert "7" in out

    def test_uses_previous(self):
        out = run_stdin("a = 3\nb = a + a\nb = ?")
        assert "6" in out


# ===========================================================================
# 2. Arithmetic expressions
# ===========================================================================

class TestArithFile:
    def test_add(self, tmp_path):
        assert "5" in run_file("2 + 3 = ?", tmp_path=tmp_path)

    def test_sub(self, tmp_path):
        assert "1" in run_file("4 - 3 = ?", tmp_path=tmp_path)

    def test_mul(self, tmp_path):
        assert "12" in run_file("3 * 4 = ?", tmp_path=tmp_path)

    def test_div_exact(self, tmp_path):
        assert "2" in run_file("6 / 3 = ?", tmp_path=tmp_path)

    def test_div_fraction(self, tmp_path):
        assert "1/3" in run_file("1 / 3 = ?", tmp_path=tmp_path)

    def test_modulo(self, tmp_path):
        assert "1" in run_file("7 % 3 = ?", tmp_path=tmp_path)

    def test_floor_div(self, tmp_path):
        assert "2" in run_file("7 // 3 = ?", tmp_path=tmp_path)

    def test_power(self, tmp_path):
        assert "8" in run_file("2 ^ 3 = ?", tmp_path=tmp_path)

    def test_precedence(self, tmp_path):
        assert "14" in run_file("2 + 3 * 4 = ?", tmp_path=tmp_path)

    def test_unary_minus(self, tmp_path):
        assert "-5" in run_file("-5 = ?", tmp_path=tmp_path)

    def test_implicit_multiply(self, tmp_path):
        out = run_file("x = 3\n2x = ?", tmp_path=tmp_path)
        assert "6" in out

    def test_fraction_cancel(self, tmp_path):
        assert "1" in run_file("1/3 + 2/3 = ?", tmp_path=tmp_path)


# ===========================================================================
# 3. Complex numbers
# ===========================================================================

class TestComplexFile:
    def test_assign_complex(self, tmp_path):
        out = run_file("z = 3 + 2 * i\nz = ?", tmp_path=tmp_path)
        assert "3 + 2i" in out

    def test_complex_add(self, tmp_path):
        out = run_file("(2 + 3 * i) + (1 - i) = ?", tmp_path=tmp_path)
        assert "3 + 2i" in out

    def test_complex_mul(self, tmp_path):
        out = run_file("(2 + 3 * i) * (1 - i) = ?", tmp_path=tmp_path)
        assert "5 + i" in out

    def test_i_squared(self, tmp_path):
        assert "-1" in run_file("i ^ 2 = ?", tmp_path=tmp_path)

    def test_i_cubed(self, tmp_path):
        assert "-i" in run_file("i ^ 3 = ?", tmp_path=tmp_path)

    def test_i_fourth(self, tmp_path):
        assert "1" in run_file("i ^ 4 = ?", tmp_path=tmp_path)

    def test_complex_power(self, tmp_path):
        # (2 + 3i)^2 = 4 + 12i - 9 = -5 + 12i
        out = run_file("(2 + 3 * i) ^ 2 = ?", tmp_path=tmp_path)
        assert "-5 + 12i" in out

    def test_pure_imaginary(self, tmp_path):
        assert "i" in run_file("sqrt(-1) = ?", tmp_path=tmp_path)


# ===========================================================================
# 4. Matrix operations
# ===========================================================================

class TestMatrixFile:
    def test_assign_display(self, tmp_path):
        out = run_file("m = [[1,2];[3,4]]\nm = ?", tmp_path=tmp_path)
        assert "[ 1 , 2 ]" in out
        assert "[ 3 , 4 ]" in out

    def test_add(self, tmp_path):
        out = run_file(
            "a = [[1,2];[3,4]]\nb = [[5,6];[7,8]]\na + b = ?",
            tmp_path=tmp_path,
        )
        assert "[ 6 , 8 ]" in out
        assert "[ 10 , 12 ]" in out

    def test_element_wise_mul(self, tmp_path):
        out = run_file(
            "a = [[1,2];[3,4]]\nb = [[5,6];[7,8]]\na * b = ?",
            tmp_path=tmp_path,
        )
        assert "[ 5 , 12 ]" in out
        assert "[ 21 , 32 ]" in out

    def test_matmul(self, tmp_path):
        out = run_file(
            "a = [[1,2];[3,4]]\nb = [[5,6];[7,8]]\na ** b = ?",
            tmp_path=tmp_path,
        )
        assert "[ 19 , 22 ]" in out
        assert "[ 43 , 50 ]" in out

    def test_scalar_mul(self, tmp_path):
        out = run_file("a = [[1,2];[3,4]]\na * 2 = ?", tmp_path=tmp_path)
        assert "[ 2 , 4 ]" in out
        assert "[ 6 , 8 ]" in out

    def test_sub(self, tmp_path):
        out = run_file(
            "a = [[5,6];[7,8]]\nb = [[1,2];[3,4]]\na - b = ?",
            tmp_path=tmp_path,
        )
        assert "[ 4 , 4 ]" in out
        assert "[ 4 , 4 ]" in out


# ===========================================================================
# 5. Functions
# ===========================================================================

class TestFunctionFile:
    def test_def_and_call(self, tmp_path):
        out = run_file("f(x) = x ^ 2\nf(3) = ?", tmp_path=tmp_path)
        assert "9" in out

    def test_def_display(self, tmp_path):
        out = run_file("f(x) = 2 * x + 1", tmp_path=tmp_path)
        assert "f(x)" in out
        assert "x" in out

    def test_constant_folding_in_def(self, tmp_path):
        out = run_file("f(x) = 2 + 3 + x", tmp_path=tmp_path)
        assert "5" in out

    def test_call_at_zero(self, tmp_path):
        out = run_file("f(x) = x ^ 2 + 2 * x + 1\nf(0) = ?", tmp_path=tmp_path)
        assert "1" in out

    def test_call_negative(self, tmp_path):
        out = run_file("f(x) = x ^ 2 + 2 * x + 1\nf(-1) = ?", tmp_path=tmp_path)
        assert "0" in out

    def test_nested_call(self, tmp_path):
        out = run_file(
            "f(x) = x * 2\ng(x) = f(x) + 1\ng(5) = ?",
            tmp_path=tmp_path,
        )
        assert "11" in out

    def test_function_uses_variable(self, tmp_path):
        out = run_file("a = 3\nf(x) = x + a\nf(2) = ?", tmp_path=tmp_path)
        assert "5" in out

    def test_builtin_sqrt(self, tmp_path):
        assert "2" in run_file("sqrt(4) = ?", tmp_path=tmp_path)

    def test_builtin_sqrt_irrational(self, tmp_path):
        assert "√2" in run_file("sqrt(2) = ?", tmp_path=tmp_path)

    def test_builtin_abs(self, tmp_path):
        assert "5" in run_file("abs(-5) = ?", tmp_path=tmp_path)


# ===========================================================================
# 6. Solve
# ===========================================================================

class TestSolveFile:
    def test_linear(self, tmp_path):
        out = run_file("f(x) = 2 * x - 6\nf(x) = 0 ?", tmp_path=tmp_path)
        assert "3" in out

    def test_quadratic_two_real(self, tmp_path):
        out = run_file("f(x) = x ^ 2 - 3 * x + 2\nf(x) = 0 ?", tmp_path=tmp_path)
        assert "1" in out
        assert "2" in out

    def test_quadratic_one_real(self, tmp_path):
        out = run_file("f(x) = x ^ 2 - 2 * x + 1\nf(x) = 0 ?", tmp_path=tmp_path)
        assert "1" in out
        assert "One solution" in out

    def test_quadratic_irrational(self, tmp_path):
        out = run_file("f(x) = x ^ 2 - 2\nf(x) = 0 ?", tmp_path=tmp_path)
        assert "√2" in out

    def test_quadratic_complex(self, tmp_path):
        out = run_file("f(x) = x ^ 2 + 1\nf(x) = 0 ?", tmp_path=tmp_path)
        assert "i" in out

    def test_quadratic_complex_rhs(self, tmp_path):
        # f(x) = x^2 - 2, solve for f(x) = 2  →  x^2 = 4  →  x = ±2
        out = run_file("f(x) = x ^ 2 - 2\nf(x) = 2 ?", tmp_path=tmp_path)
        assert "2" in out

    def test_no_solution(self, tmp_path):
        out = run_file("f(x) = 5\nf(x) = 0 ?", tmp_path=tmp_path)
        assert "No solution" in out

    def test_infinite_solutions(self, tmp_path):
        out = run_file("f(x) = 0 * x\nf(x) = 0 ?", tmp_path=tmp_path)
        assert "Infinite" in out

    def test_degree_3_error(self, tmp_path):
        out = run_file("f(x) = x ^ 3\nf(x) = 0 ?", tmp_path=tmp_path)
        assert "Error" in out or "error" in out.lower()


# ===========================================================================
# 7. Error handling — no crash, just "Error: ..." line
# ===========================================================================

class TestErrorHandlingFile:
    def test_division_by_zero(self, tmp_path):
        out = run_file("1 / 0 = ?", tmp_path=tmp_path)
        assert out.startswith("Error:")

    def test_undefined_variable(self, tmp_path):
        out = run_file("undefined_var = ?", tmp_path=tmp_path)
        assert "Error" in out

    def test_matrix_dimension_mismatch(self, tmp_path):
        out = run_file("[[1,2]] ** [[1,2]] = ?", tmp_path=tmp_path)
        assert "Error" in out

    def test_recursion(self, tmp_path):
        out = run_file("f(x) = f(x) + 1\nf(3) = ?", tmp_path=tmp_path)
        assert "Error" in out

    def test_execution_continues_after_error(self, tmp_path):
        # After an error, next line must still execute
        out = run_file("1 / 0 = ?\n2 + 2 = ?", tmp_path=tmp_path)
        assert "Error" in out
        assert "4" in out

    def test_matrix_type_mismatch(self, tmp_path):
        out = run_file("[[1,2];[3,4]] + 5 = ?", tmp_path=tmp_path)
        assert "Error" in out


class TestErrorHandlingStdin:
    def test_division_by_zero_no_crash(self):
        out = run_stdin("1 / 0 = ?")
        assert "Error" in out

    def test_continues_after_error(self):
        out = run_stdin("1 / 0 = ?\n3 + 3 = ?")
        assert "Error" in out
        assert "6" in out


# ===========================================================================
# 8. Comments and blank lines in file mode
# ===========================================================================

class TestFileFormat:
    def test_comments_ignored(self, tmp_path):
        out = run_file("# this is a comment\n2 + 2 = ?", tmp_path=tmp_path)
        assert out == "4"

    def test_blank_lines_ignored(self, tmp_path):
        out = run_file("\n\n2 + 2 = ?\n\n", tmp_path=tmp_path)
        assert out == "4"

    def test_mixed(self, tmp_path):
        out = run_file(
            """
            # assign
            x = 10

            # query
            x = ?
            """,
            tmp_path=tmp_path,
        )
        assert "10" in out


# ===========================================================================
# 9. Stdin REPL: multiple commands
# ===========================================================================

class TestReplSession:
    def test_full_session(self):
        out = run_stdin(
            """
            x = 5
            y = x * 2
            y = ?
            f(x) = x ^ 2
            f(3) = ?
            """
        )
        assert "10" in out
        assert "9" in out

    def test_reassign_in_session(self):
        out = run_stdin("x = 1\nx = 2\nx = ?")
        assert out.splitlines()[-1] == "2"