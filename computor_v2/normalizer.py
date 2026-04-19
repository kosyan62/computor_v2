from __future__ import annotations
from computor_v2.parsing.AST import (
    Node, NumberNode, VariableNode, UnaryMinusNode, UnaryPlusNode,
    BinaryOperationNode, FunctionCallNode,
)
from computor_v2.types import Rational
R = Rational
from computor_v2.store import Store
from computor_v2.errors import ComputorSolverError, ComputorNameError
from computor_v2.polynomial import Polynomial


class Normalizer:
    def __init__(self, store: Store):
        self._store = store

    def simplify(self, node: Node, param: str) -> Node:
        """Fold numeric sub-expressions and Rational store vars, leave param as-is."""
        if self._is_literal(node, param):
            val = self._eval_literal(node)
            return NumberNode(str(val) if val.denominator == 1 else f"{val.numerator}/{val.denominator}")

        if isinstance(node, UnaryMinusNode):
            inner = self.simplify(node.operand, param)
            return UnaryMinusNode(inner)

        if isinstance(node, UnaryPlusNode):
            return self.simplify(node.operand, param)

        if isinstance(node, BinaryOperationNode):
            left = self.simplify(node.left, param)
            right = self.simplify(node.right, param)
            return BinaryOperationNode(left, node.op, right)

        return node

    def _is_literal(self, node: Node, param: str = "") -> bool:
        """True if node contains only numbers, ops, and Rational store variables (not param)."""
        if isinstance(node, NumberNode):
            return True
        if isinstance(node, VariableNode):
            if node.value.lower() == param.lower():
                return False
            try:
                val = self._store.get(node.value)
                return isinstance(val, R)
            except Exception:
                return False
        if isinstance(node, FunctionCallNode):
            return False
        if isinstance(node, (UnaryMinusNode, UnaryPlusNode)):
            return self._is_literal(node.operand, param)
        if isinstance(node, BinaryOperationNode):
            return self._is_literal(node.left, param) and self._is_literal(node.right, param)
        return False

    def _eval_literal(self, node: Node) -> Rational:
        """Evaluate a literal-only node to Rational."""
        if isinstance(node, NumberNode):
            return Rational.from_str(str(node.value))
        if isinstance(node, VariableNode):
            val = self._store.get(node.value)
            return val  # guaranteed Rational by _is_literal
        if isinstance(node, UnaryMinusNode):
            return -self._eval_literal(node.operand)
        if isinstance(node, UnaryPlusNode):
            return self._eval_literal(node.operand)
        if isinstance(node, BinaryOperationNode):
            left = self._eval_literal(node.left)
            right = self._eval_literal(node.right)
            match node.op:
                case "+":  return left + right
                case "-":  return left - right
                case "*":  return left * right
                case "/":  return left / right
                case "^":  return left ** right
                case "%":  return left % right
                case "//": return left // right
        raise ComputorSolverError(f"Cannot evaluate literal node: {node}")

    def to_polynomial(self, node: Node, var: str) -> Polynomial:
        """Convert AST with one free variable to Polynomial."""
        coeffs = self._to_poly(node, var.lower())
        return Polynomial(coeffs)

    def to_polynomial_for_solve(self, body: Node, rhs_value, param: str) -> Polynomial:
        """Return Polynomial for (body - rhs_value), used by Dispatcher._handle_solve."""
        if not isinstance(rhs_value, R):
            raise ComputorSolverError(
                f"Right-hand side must be a rational number, got {type(rhs_value).__name__}"
            )
        node = BinaryOperationNode(body, "-", NumberNode(str(rhs_value)))
        return self.to_polynomial(node, param)

    def _to_poly(self, node: Node, var: str) -> dict[int, R]:
        if isinstance(node, NumberNode):
            return {0: Rational.from_str(str(node.value))}

        if isinstance(node, VariableNode):
            key = node.value.lower()
            if key == var:
                return {1: R(1)}
            # look up in store — must be Rational coefficient
            try:
                val = self._store.get(node.value)
            except ComputorNameError:
                raise ComputorSolverError(
                    f"Cannot solve: '{node.value}' is undefined"
                )
            if not isinstance(val, Rational):
                raise ComputorSolverError(
                    f"Cannot use non-rational variable '{node.value}' in polynomial"
                )
            return {0: val}

        if isinstance(node, UnaryMinusNode):
            return {k: -v for k, v in self._to_poly(node.operand, var).items()}

        if isinstance(node, UnaryPlusNode):
            return self._to_poly(node.operand, var)

        if isinstance(node, BinaryOperationNode):
            return self._eval_binop_poly(node, var)

        raise ComputorSolverError(
            f"Cannot convert {type(node).__name__} to polynomial"
        )

    def _eval_binop_poly(self, node: BinaryOperationNode, var: str) -> dict[int, R]:
        match node.op:
            case "+":
                return _poly_add(self._to_poly(node.left, var), self._to_poly(node.right, var))
            case "-":
                return _poly_sub(self._to_poly(node.left, var), self._to_poly(node.right, var))
            case "*":
                return _poly_mul(self._to_poly(node.left, var), self._to_poly(node.right, var))
            case "^":
                base = self._to_poly(node.left, var)
                exp_poly = self._to_poly(node.right, var)
                if set(exp_poly.keys()) - {0}:
                    raise ComputorSolverError("Exponent must be constant in polynomial")
                exp = exp_poly.get(0, R(0))
                if exp.denominator != 1 or exp.numerator < 0:
                    raise ComputorSolverError("Exponent must be a non-negative integer")
                return _poly_pow(base, exp.numerator)
            case _:
                raise ComputorSolverError(f"Operator '{node.op}' not supported in polynomial")


def _poly_add(a: dict, b: dict) -> dict:
    result = dict(a)
    for k, v in b.items():
        result[k] = result.get(k, R(0)) + v
    return result


def _poly_sub(a: dict, b: dict) -> dict:
    return _poly_add(a, {k: -v for k, v in b.items()})


def _poly_mul(a: dict, b: dict) -> dict:
    result = {}
    for ka, va in a.items():
        for kb, vb in b.items():
            k = ka + kb
            result[k] = result.get(k, R(0)) + va * vb
    return result


def _poly_pow(poly: dict, n: int) -> dict:
    result = {0: R(1)}
    for _ in range(n):
        result = _poly_mul(result, poly)
    return result