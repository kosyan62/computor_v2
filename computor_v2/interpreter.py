from __future__ import annotations
from computor_v2.parsing.AST import (
    Node, NumberNode, VariableNode, UnaryMinusNode, UnaryPlusNode,
    BinaryOperationNode, FunctionCallNode, MatrixNode,
)
from computor_v2.types import Rational, Matrix, Function
from computor_v2.store import Store
from computor_v2.errors import (
    ComputorTypeError, ComputorArgumentError,
    ComputorRecursionError, ComputorValueError,
)

_OPS = {"+", "-", "*", "/", "%", "//", "^", "**"}


class Interpreter:
    def __init__(self, store: Store):
        self._store = store
        self._call_stack: set[str] = set()

    def evaluate(self, node: Node, bindings: dict = None):
        if bindings is None:
            bindings = {}
        return self._eval(node, bindings)

    def _eval(self, node: Node, bindings: dict):
        if isinstance(node, NumberNode):
            return Rational.from_str(str(node.value))

        if isinstance(node, VariableNode):
            key = node.value.lower()
            if key in {k.lower() for k in bindings}:
                for k, v in bindings.items():
                    if k.lower() == key:
                        return v
            return self._store.get(node.value)

        if isinstance(node, UnaryMinusNode):
            return -self._eval(node.operand, bindings)

        if isinstance(node, UnaryPlusNode):
            return self._eval(node.operand, bindings)

        if isinstance(node, BinaryOperationNode):
            return self._eval_binop(node, bindings)

        if isinstance(node, FunctionCallNode):
            return self._eval_funcall(node, bindings)

        if isinstance(node, MatrixNode):
            rows = [
                [self._eval(cell, bindings) for cell in row]
                for row in node.value
            ]
            return Matrix(rows)

        raise ComputorTypeError(f"Cannot evaluate node: {type(node).__name__}")

    def _eval_binop(self, node: BinaryOperationNode, bindings: dict):
        if node.op not in _OPS:
            raise ComputorTypeError(f"Unknown operator: '{node.op}'")
        left = self._eval(node.left, bindings)
        right = self._eval(node.right, bindings)
        try:
            match node.op:
                case "+":  return left + right
                case "-":  return left - right
                case "*":  return left * right
                case "/":  return left / right
                case "%":  return left % right
                case "//": return left // right
                case "^":  return left ** right
                case "**": return left @ right
        except TypeError as e:
            raise ComputorTypeError(str(e)) from e
        except ZeroDivisionError as e:
            raise ComputorValueError(str(e)) from e

    def _eval_funcall(self, node: FunctionCallNode, bindings: dict):
        func = self._store.get(node.func_name)
        if not isinstance(func, Function):
            raise ComputorTypeError(f"'{node.func_name}' is not a function")

        if len(node.args) != 1:
            raise ComputorArgumentError(
                f"'{node.func_name}' expects 1 argument, got {len(node.args)}"
            )

        if node.func_name in self._call_stack:
            raise ComputorRecursionError(
                f"Recursive call detected: '{node.func_name}'"
            )

        arg = self._eval(node.args[0], bindings)
        self._call_stack.add(node.func_name)
        try:
            return func.call(arg, self)
        finally:
            self._call_stack.discard(node.func_name)