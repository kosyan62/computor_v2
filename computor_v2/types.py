from __future__ import annotations
from abc import ABC
from computor_v2.pure_math import gcd, factor_sqrt


class Scalar(ABC):
    """Common base for all scalar numeric types: Rational, Irrational, Complex."""


class Rational(Scalar):
    def __init__(self, numerator: int, denominator: int = 1):
        if denominator == 0:
            raise ZeroDivisionError("Rational denominator cannot be zero")
        if denominator < 0:
            numerator, denominator = -numerator, -denominator
        g = gcd(abs(numerator), denominator)
        self.numerator = numerator // g
        self.denominator = denominator // g

    @classmethod
    def from_str(cls, s: str) -> Rational:
        if "." in s:
            integer_part, decimal_part = s.split(".")
            denominator = 10 ** len(decimal_part)
            numerator = int(integer_part) * denominator + int(decimal_part)
            return cls(numerator, denominator)
        return cls(int(s))

    def _coerce(self, other):
        if isinstance(other, int):
            return Rational(other)
        if isinstance(other, Rational):
            return other
        return None

    # --- Arithmetic ---

    def __add__(self, other):
        if isinstance(other, Complex):
            return Complex(self, Rational(0)) + other
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return Rational(
            self.numerator * other.denominator + other.numerator * self.denominator,
            self.denominator * other.denominator,
        )

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Complex):
            return Complex(self, Rational(0)) - other
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return Rational(
            self.numerator * other.denominator - other.numerator * self.denominator,
            self.denominator * other.denominator,
        )

    def __rsub__(self, other):
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return Rational(
            other.numerator * self.denominator - self.numerator * other.denominator,
            self.denominator * other.denominator,
        )

    def __mul__(self, other):
        if isinstance(other, Complex):
            return Complex(self, Rational(0)) * other
        if isinstance(other, Matrix):
            return other * self
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return Rational(self.numerator * other.numerator,
                        self.denominator * other.denominator)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, Complex):
            return Complex(self, Rational(0)) / other
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        if other.numerator == 0:
            raise ZeroDivisionError("Division by zero")
        return Rational(self.numerator * other.denominator,
                        self.denominator * other.numerator)

    def __rtruediv__(self, other):
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return other / self

    def __floordiv__(self, other):
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        if other.numerator == 0:
            raise ZeroDivisionError("Floor division by zero")
        q = (self.numerator * other.denominator) // (self.denominator * other.numerator)
        return Rational(q)

    def __mod__(self, other):
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        if other.numerator == 0:
            raise ZeroDivisionError("Modulo by zero")
        return self - other * (self // other)

    def __pow__(self, other):
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        if other.denominator != 1:
            raise TypeError("Exponent must be an integer")
        exp = other.numerator
        if exp == 0:
            return Rational(1)
        if exp < 0:
            if self.numerator == 0:
                raise ZeroDivisionError("Zero cannot be raised to a negative power")
            return Rational(self.denominator ** (-exp), self.numerator ** (-exp))
        return Rational(self.numerator ** exp, self.denominator ** exp)

    def __neg__(self):
        return Rational(-self.numerator, self.denominator)

    def __abs__(self):
        return Rational(abs(self.numerator), self.denominator)

    # --- Comparison ---

    def __eq__(self, other):
        if isinstance(other, Rational):
            return self.numerator == other.numerator and self.denominator == other.denominator
        if isinstance(other, Complex):
            return Complex(self, Rational(0)) == other
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Rational):
            return self.numerator * other.denominator < other.numerator * self.denominator
        return NotImplemented

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        if isinstance(other, Rational):
            return other < self
        return NotImplemented

    def __ge__(self, other):
        return self == other or self > other

    def __repr__(self):
        if self.denominator == 1:
            return str(self.numerator)
        return f"{self.numerator}/{self.denominator}"

    def __hash__(self):
        return hash((self.numerator, self.denominator))


class Complex(Scalar):
    def __init__(self, re: Rational, im: Rational):
        self.re = re
        self.im = im

    def _coerce(self, other):
        if isinstance(other, Matrix):
            raise TypeError("Complex and Matrix are incompatible types")
        if isinstance(other, Rational):
            return Complex(other, Rational(0))
        if isinstance(other, Complex):
            return other
        return None

    # --- Arithmetic ---

    def __add__(self, other):
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return Complex(self.re + other.re, self.im + other.im)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return Complex(self.re - other.re, self.im - other.im)

    def __rsub__(self, other):
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return other - self

    def __mul__(self, other):
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return Complex(
            self.re * other.re - self.im * other.im,
            self.re * other.im + self.im * other.re,
        )

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        denom = other.re * other.re + other.im * other.im
        if denom == Rational(0):
            raise ZeroDivisionError("Division by zero")
        return Complex(
            (self.re * other.re + self.im * other.im) / denom,
            (self.im * other.re - self.re * other.im) / denom,
        )

    def __rtruediv__(self, other):
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return other / self

    def __neg__(self):
        return Complex(-self.re, -self.im)

    # --- Comparison ---

    def __eq__(self, other):
        if isinstance(other, Complex):
            return self.re == other.re and self.im == other.im
        if isinstance(other, Rational):
            return self.re == other and self.im == Rational(0)
        return NotImplemented

    def __repr__(self):
        return f"Complex({self.re} + {self.im}i)"

    def __hash__(self):
        return hash((self.re, self.im))


class Matrix:
    def __init__(self, rows: list[list]):
        if not rows or not rows[0]:
            raise ValueError("Matrix cannot be empty")
        n_cols = len(rows[0])
        if not all(len(r) == n_cols for r in rows):
            raise ValueError("All matrix rows must have the same length")
        self.rows = rows
        self.n_rows = len(rows)
        self.n_cols = n_cols

    def _check_same_size(self, other: Matrix, op: str):
        if self.n_rows != other.n_rows or self.n_cols != other.n_cols:
            raise TypeError(
                f"Matrix size mismatch for '{op}': "
                f"{self.n_rows}×{self.n_cols} vs {other.n_rows}×{other.n_cols}"
            )

    def __add__(self, other):
        if isinstance(other, Matrix):
            self._check_same_size(other, "+")
            return Matrix([
                [self.rows[i][j] + other.rows[i][j] for j in range(self.n_cols)]
                for i in range(self.n_rows)
            ])
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Matrix):
            self._check_same_size(other, "-")
            return Matrix([
                [self.rows[i][j] - other.rows[i][j] for j in range(self.n_cols)]
                for i in range(self.n_rows)
            ])
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (Rational, Complex)):
            return Matrix([
                [self.rows[i][j] * other for j in range(self.n_cols)]
                for i in range(self.n_rows)
            ])
        if isinstance(other, Matrix):
            self._check_same_size(other, "*")
            return Matrix([
                [self.rows[i][j] * other.rows[i][j] for j in range(self.n_cols)]
                for i in range(self.n_rows)
            ])
        return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, (Rational, Complex)):
            return self * other
        return NotImplemented

    def __matmul__(self, other):
        if isinstance(other, Matrix):
            if self.n_cols != other.n_rows:
                raise TypeError(
                    f"Matrix multiplication size mismatch: "
                    f"{self.n_rows}×{self.n_cols} ** {other.n_rows}×{other.n_cols}"
                )
            return Matrix([
                [
                    sum(
                        (self.rows[i][k] * other.rows[k][j] for k in range(self.n_cols)),
                        Rational(0),
                    )
                    for j in range(other.n_cols)
                ]
                for i in range(self.n_rows)
            ])
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, Matrix):
            return (self.n_rows == other.n_rows and self.n_cols == other.n_cols
                    and all(
                        self.rows[i][j] == other.rows[i][j]
                        for i in range(self.n_rows)
                        for j in range(self.n_cols)
                    ))
        return NotImplemented

    def __repr__(self):
        return f"Matrix({self.rows})"


class Irrational(Scalar):
    """Represents number + coeff * √radicand.
    number and coeff may be Rational or Complex; radicand is always a positive Rational.
    """

    def __init__(self, number, coeff, radicand: Rational):
        if radicand == Rational(0):
            raise ValueError("Irrational radicand cannot be zero — use Rational instead")
        if coeff == Rational(0):
            raise ValueError("Irrational coeff cannot be zero — use Rational instead")
        # Negative radicand: √(-r) = i * √r — absorb sign into coeff
        if radicand < Rational(0):
            radicand = -radicand
            coeff = coeff * Complex(Rational(0), Rational(1))
        # Normalize: factor perfect squares out of radicand.
        # √(p/q) = √(p*q) / q  →  factor_sqrt(p*q) = (c, r)  →  coeff *= c/q, radicand = r
        p = radicand.numerator
        q = radicand.denominator
        c, r = factor_sqrt(p * q)
        self.number = number
        self.coeff = coeff * Rational(c, q)
        self.radicand = Rational(r)

    # --- helpers ---

    def _check_radicand(self, other: "Irrational", op: str):
        if self.radicand != other.radicand:
            raise TypeError(
                f"Cannot {op} irrationals with different radicands "
                f"(√{self.radicand} vs √{other.radicand})"
            )

    @staticmethod
    def _coerce_scalar(other):
        if isinstance(other, int):
            return Rational(other)
        if isinstance(other, (Rational, Complex)):
            return other
        return None

    # --- Arithmetic ---

    def __add__(self, other):
        s = self._coerce_scalar(other)
        if s is not None:
            return Irrational(self.number + s, self.coeff, self.radicand)
        if isinstance(other, Irrational):
            self._check_radicand(other, "add")
            new_coeff = self.coeff + other.coeff
            new_number = self.number + other.number
            if new_coeff == Rational(0):
                return new_number
            return Irrational(new_number, new_coeff, self.radicand)
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        s = self._coerce_scalar(other)
        if s is not None:
            return Irrational(self.number - s, self.coeff, self.radicand)
        if isinstance(other, Irrational):
            self._check_radicand(other, "subtract")
            new_coeff = self.coeff - other.coeff
            new_number = self.number - other.number
            if new_coeff == Rational(0):
                return new_number
            return Irrational(new_number, new_coeff, self.radicand)
        return NotImplemented

    def __rsub__(self, other):
        s = self._coerce_scalar(other)
        if s is not None:
            return Irrational(s - self.number, -self.coeff, self.radicand)
        return NotImplemented

    def __mul__(self, other):
        s = self._coerce_scalar(other)
        if s is not None:
            new_coeff = self.coeff * s
            new_number = self.number * s
            if new_coeff == Rational(0):
                return new_number
            return Irrational(new_number, new_coeff, self.radicand)
        if isinstance(other, Irrational):
            self._check_radicand(other, "multiply")
            # (a + b√r) * (c + d√r) = (ac + bd*r) + (ad + bc)√r
            a, b, r = self.number, self.coeff, self.radicand
            c, d = other.number, other.coeff
            new_number = a * c + b * d * r
            new_coeff = a * d + b * c
            if new_coeff == Rational(0):
                return new_number
            return Irrational(new_number, new_coeff, self.radicand)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        s = self._coerce_scalar(other)
        if s is not None:
            if s == Rational(0):
                raise ZeroDivisionError("Division by zero")
            return Irrational(self.number / s, self.coeff / s, self.radicand)
        if isinstance(other, Irrational):
            self._check_radicand(other, "divide")
            # (a + b√r) / (c + d√r) — multiply by conjugate (c - d√r)
            # numerator: (a + b√r)(c - d√r) = (ac - bd*r) + (bc - ad)√r
            # denominator: c^2 - d^2 * r
            a, b, r = self.number, self.coeff, self.radicand
            c, d = other.number, other.coeff
            denom = c * c - d * d * r
            if denom == Rational(0):
                raise ZeroDivisionError("Division by zero")
            new_number = (a * c - b * d * r) / denom
            new_coeff = (b * c - a * d) / denom
            if new_coeff == Rational(0):
                return new_number
            return Irrational(new_number, new_coeff, self.radicand)
        return NotImplemented

    def __rtruediv__(self, other):
        s = self._coerce_scalar(other)
        if s is not None:
            # s / (a + b√r) — multiply by conjugate (a - b√r)
            # = s*(a - b√r) / (a^2 - b^2*r)
            a, b, r = self.number, self.coeff, self.radicand
            denom = a * a - b * b * r
            if denom == Rational(0):
                raise ZeroDivisionError("Division by zero")
            new_number = (s * a) / denom
            new_coeff = (-s * b) / denom
            if new_coeff == Rational(0):
                return new_number
            return Irrational(new_number, new_coeff, self.radicand)
        return NotImplemented

    def __neg__(self):
        return Irrational(-self.number, -self.coeff, self.radicand)

    # --- Comparison ---

    def __eq__(self, other):
        if isinstance(other, Irrational):
            return (self.number == other.number
                    and self.coeff == other.coeff
                    and self.radicand == other.radicand)
        return NotImplemented

    def __hash__(self):
        return hash((self.number, self.coeff, self.radicand))

    # --- Display ---

    @staticmethod
    def _fmt_scalar(val) -> str:
        """Format a Rational or Complex value for inline display."""
        if isinstance(val, Complex):
            if val.re == Rational(0):
                if val.im == Rational(1):
                    return "i"
                if val.im == Rational(-1):
                    return "-i"
                return f"{val.im}i"
            if val.im == Rational(0):
                return repr(val.re)
            return f"({val.re} + {val.im}i)"
        return repr(val)

    def __repr__(self):
        rad_str = f"√{self.radicand}"
        c_str = self._fmt_scalar(self.coeff)
        if c_str == "1":
            sqrt_str = rad_str
        elif c_str == "-1":
            sqrt_str = f"-{rad_str}"
        else:
            sqrt_str = f"{c_str} * {rad_str}"

        n_str = self._fmt_scalar(self.number)
        if n_str == "0":
            return sqrt_str
        # determine sign of coeff for pretty +/-
        coeff_positive = (
            (isinstance(self.coeff, Rational) and self.coeff > Rational(0))
            or (isinstance(self.coeff, Complex) and self.coeff.re > Rational(0))
        )
        if coeff_positive:
            return f"{n_str} + {sqrt_str}"
        return f"{n_str} - {sqrt_str[1:]}"  # strip leading '-'


class Function:
    def __init__(self, param: str, body):
        self.param = param
        self.body = body

    def call(self, arg, evaluator):
        """Evaluate body with param bound to arg."""
        return evaluator.evaluate_with(self.body, {self.param: arg})

    def __repr__(self):
        return f"Function({self.param} → {self.body})"

    def __eq__(self, other):
        if isinstance(other, Function):
            return self.param == other.param and self.body == other.body
        return False


class BuiltinFunction(Function):
    def __init__(self, name: str, fn):
        self.name = name
        self._fn = fn

    def call(self, arg, evaluator=None):
        return self._fn(arg)

    def __repr__(self):
        return f"BuiltinFunction({self.name})"

    def __eq__(self, other):
        if isinstance(other, BuiltinFunction):
            return self.name == other.name
        return False