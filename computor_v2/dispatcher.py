from __future__ import annotations
from computor_v2.parsing.AST import (
    Node, Equality, FunctionDefinitionNode, QueryNode, SolveNode,
    VariableNode, FunctionCallNode,
)
from computor_v2.store import Store
from computor_v2.interpreter import Interpreter
from computor_v2.normalizer import Normalizer
from computor_v2.solver import PolynomialSolver
from computor_v2.types import Function
from computor_v2.errors import ComputorTypeError
from computor_v2.formatter import fmt, fmt_ast, fmt_solve


class Dispatcher:
    def __init__(self, store: Store):
        self.store = store

    def dispatch(self, node: Node) -> str:
        if isinstance(node, FunctionDefinitionNode):
            return self._handle_func_def(node)
        if isinstance(node, Equality) and isinstance(node.left, VariableNode):
            return self._handle_assign(node)
        if isinstance(node, QueryNode):
            return self._handle_query(node)
        if isinstance(node, SolveNode):
            return self._handle_solve(node)
        return self._handle_expr(node)

    def _handle_assign(self, node: Equality) -> str:
        value = Interpreter(self.store).evaluate(node.right)
        self.store.set(node.left.value, value)
        return fmt(value)

    def _handle_func_def(self, node: FunctionDefinitionNode) -> str:
        param = node.args[0].value
        self.store.set(node.name, Function(param, node.expression))
        simplified = Normalizer(self.store).simplify(node.expression, param)
        return f"{node.name}({param}) = {fmt_ast(simplified)}"

    def _handle_query(self, node: QueryNode) -> str:
        value = Interpreter(self.store).evaluate(node.expr)
        return fmt(value)

    def _handle_expr(self, node: Node) -> str:
        value = Interpreter(self.store).evaluate(node)
        return fmt(value)

    def _handle_solve(self, node: SolveNode) -> str:
        if not isinstance(node.lhs, FunctionCallNode):
            raise ComputorTypeError("Solve requires a function call on the left side")
        func_name = node.lhs.func_name
        param = node.lhs.args[0].value if node.lhs.args else "x"
        func = self.store.get(func_name)
        if not isinstance(func, Function):
            raise ComputorTypeError(f"'{func_name}' is not a function")
        rhs_value = Interpreter(self.store).evaluate(node.rhs)
        poly = Normalizer(self.store).to_polynomial_for_solve(func.body, rhs_value, param)
        result = PolynomialSolver.solve(poly)
        return fmt_solve(result, poly, var=param)
