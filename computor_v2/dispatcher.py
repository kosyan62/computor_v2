from __future__ import annotations
from computor_v2.parsing.AST import (
    Node, Equality, FunctionDefinitionNode, QueryNode, SolveNode, VariableNode,
)
from computor_v2.store import Store
from computor_v2.interpreter import Interpreter
from computor_v2.normalizer import Normalizer
from computor_v2.solver import PolynomialSolver, SolveResult
from computor_v2.types import Function
from computor_v2.errors import ComputorTypeError, ComputorNameError


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
        interp = Interpreter(self.store)
        value = interp.evaluate(node.right)
        self.store.set(node.left.value, value)
        return str(value)

    def _handle_func_def(self, node: FunctionDefinitionNode) -> str:
        param = node.args[0].value
        self.store.set(node.name, Function(param, node.expression))
        simplified = Normalizer(self.store).simplify(node.expression, param)
        return f"{node.name}({param}) = {simplified}"

    def _handle_query(self, node: QueryNode) -> str:
        interp = Interpreter(self.store)
        value = interp.evaluate(node.expr)
        return str(value)

    def _handle_solve(self, node: SolveNode) -> str:
        # lhs must be a function call: f(x) = rhs ?
        from computor_v2.parsing.AST import FunctionCallNode
        if not isinstance(node.lhs, FunctionCallNode):
            raise ComputorTypeError("Solve requires a function call on the left side")

        func_name = node.lhs.func_name
        param = node.lhs.args[0].value if node.lhs.args else "x"

        func = self.store.get(func_name)
        if not isinstance(func, Function):
            raise ComputorTypeError(f"'{func_name}' is not a function")

        interp = Interpreter(self.store)
        rhs_value = interp.evaluate(node.rhs)

        from computor_v2.parsing.AST import BinaryOperationNode, NumberNode
        lhs_minus_rhs = BinaryOperationNode(
            func.body, "-", NumberNode(str(rhs_value))
        )

        norm = Normalizer(self.store)
        poly = norm.to_polynomial(lhs_minus_rhs, param)
        result = PolynomialSolver.solve(poly)

        return self._format_solve_result(result, poly)

    def _handle_expr(self, node: Node) -> str:
        interp = Interpreter(self.store)
        value = interp.evaluate(node)
        return str(value)

    def _format_solve_result(self, result: SolveResult, poly) -> str:
        lines = [f"Polynomial degree: {poly.degree}"]

        if result.count == 0:
            lines.append("No solution.")
        elif result.count == float("inf"):
            lines.append("Infinite solutions: any value is a solution.")
        elif result.count == 1:
            lines.append("One solution:")
            lines.append(f"x = {result.solutions[0]}")
        else:
            lines.append(f"{result.count} solutions:")
            for sol in result.solutions:
                lines.append(f"x = {sol}")

        return "\n".join(lines)
