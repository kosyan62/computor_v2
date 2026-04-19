import pytest
from computor_v2.store import Store
from computor_v2.types import Rational, Complex, Function, BuiltinFunction, Scalar
from computor_v2.errors import ComputorNameError, ComputorTypeError
from computor_v2.builtins import BUILTINS

R = Rational


# ---------------------------------------------------------------------------
# Store — basic get/set
# ---------------------------------------------------------------------------

class TestStoreBasic:

    def test_set_and_get(self):
        s = Store()
        s.set("x", R(42))
        assert s.get("x") == R(42)

    def test_overwrite(self):
        s = Store()
        s.set("x", R(1))
        s.set("x", R(2))
        assert s.get("x") == R(2)

    def test_multiple_variables(self):
        s = Store()
        s.set("x", R(1))
        s.set("y", R(2))
        assert s.get("x") == R(1)
        assert s.get("y") == R(2)

    def test_undefined_raises(self):
        s = Store()
        with pytest.raises(ComputorNameError):
            s.get("undefined_var")

    def test_undefined_error_message(self):
        s = Store()
        with pytest.raises(ComputorNameError, match="undefined"):
            s.get("undefined")


# ---------------------------------------------------------------------------
# Store — case insensitivity
# ---------------------------------------------------------------------------

class TestStoreCaseInsensitive:

    def test_set_upper_get_lower(self):
        s = Store()
        s.set("X", R(1))
        assert s.get("x") == R(1)

    def test_set_lower_get_upper(self):
        s = Store()
        s.set("x", R(1))
        assert s.get("X") == R(1)

    def test_mixed_case(self):
        s = Store()
        s.set("MyVar", R(5))
        assert s.get("myvar") == R(5)
        assert s.get("MYVAR") == R(5)
        assert s.get("MyVar") == R(5)

    def test_overwrite_case_insensitive(self):
        s = Store()
        s.set("x", R(1))
        s.set("X", R(2))
        assert s.get("x") == R(2)


# ---------------------------------------------------------------------------
# Store — reserved / built-in names
# ---------------------------------------------------------------------------

class TestStoreReserved:

    def test_set_i_raises(self):
        s = Store()
        with pytest.raises(ComputorNameError):
            s.set("i", R(1))

    def test_set_i_uppercase_raises(self):
        s = Store()
        with pytest.raises(ComputorNameError):
            s.set("I", R(1))

    def test_set_sqrt_raises(self):
        s = Store()
        with pytest.raises(ComputorNameError):
            s.set("sqrt", R(1))

    def test_set_abs_raises(self):
        s = Store()
        with pytest.raises(ComputorNameError):
            s.set("abs", R(1))


# ---------------------------------------------------------------------------
# Store — builtin fallback layer
# ---------------------------------------------------------------------------

class TestStoreBuiltinFallback:

    def test_get_i(self):
        s = Store()
        assert s.get("i") == Complex(R(0), R(1))

    def test_get_i_uppercase(self):
        s = Store()
        assert s.get("I") == Complex(R(0), R(1))

    def test_get_sqrt(self):
        s = Store()
        result = s.get("sqrt")
        assert isinstance(result, BuiltinFunction)

    def test_get_abs(self):
        s = Store()
        result = s.get("abs")
        assert isinstance(result, BuiltinFunction)

    def test_user_var_shadows_not_builtin(self):
        # user cannot shadow builtins (reserved), so user var always coexists separately
        s = Store()
        s.set("x", R(99))
        assert s.get("x") == R(99)
        assert s.get("i") == Complex(R(0), R(1))


# ---------------------------------------------------------------------------
# Store — contains (__contains__ / has)
# ---------------------------------------------------------------------------

class TestStoreContains:

    def test_user_var(self):
        s = Store()
        s.set("x", R(1))
        assert "x" in s

    def test_builtin_in_store(self):
        s = Store()
        assert "i" in s
        assert "sqrt" in s
        assert "abs" in s

    def test_undefined_not_in_store(self):
        s = Store()
        assert "z" not in s

    def test_case_insensitive_contains(self):
        s = Store()
        s.set("myvar", R(1))
        assert "MyVar" in s
        assert "MYVAR" in s


# ---------------------------------------------------------------------------
# Builtins
# ---------------------------------------------------------------------------

class TestBuiltins:

    def test_i_is_complex(self):
        assert BUILTINS["i"] == Complex(R(0), R(1))

    def test_i_is_scalar(self):
        assert isinstance(BUILTINS["i"], Scalar)

    def test_sqrt_is_builtin_function(self):
        assert isinstance(BUILTINS["sqrt"], BuiltinFunction)

    def test_abs_is_builtin_function(self):
        assert isinstance(BUILTINS["abs"], BuiltinFunction)

    def test_sqrt_perfect_square(self):
        result = BUILTINS["sqrt"].call(R(9))
        assert result == R(3)

    def test_sqrt_non_rational_raises(self):
        from computor_v2.errors import ComputorTypeError
        with pytest.raises(ComputorTypeError):
            BUILTINS["sqrt"].call(Complex(R(0), R(1)))

    def test_abs_positive(self):
        assert BUILTINS["abs"].call(R(5)) == R(5)

    def test_abs_negative(self):
        assert BUILTINS["abs"].call(R(-5)) == R(5)

    def test_abs_complex(self):
        assert BUILTINS["abs"].call(Complex(R(3), R(4))) == R(5)