from __future__ import annotations
from computor_v2.parsing.AST import (
    Node, Equality, FunctionDefinitionNode, QueryNode, SolveNode,
    VariableNode, FunctionCallNode, BinaryOperationNode,
    UnaryMinusNode, UnaryPlusNode,
)
from computor_v2.store import Store
from computor_v2.interpreter import Interpreter
from computor_v2.normalizer import Normalizer
from computor_v2.solver import PolynomialSolver
from computor_v2.types import Function
from computor_v2.errors import ComputorTypeError, ComputorSolverError, ComputorNameError
from computor_v2.formatter import fmt, fmt_ast, fmt_solve, fmt_polynomial


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
        from computor_v2.errors import ComputorArgumentError
        if not node.args:
            raise ComputorArgumentError("Function must have exactly one parameter")
        if len(node.args) > 1:
            raise ComputorArgumentError("Function must have exactly one parameter")
        param = node.args[0].value
        self.store.set(node.name, Function(param, node.expression))
        simplified = Normalizer(self.store).simplify(node.expression, param)
        return f"{node.name}({param}) = {fmt_ast(simplified)}"

    def _handle_query(self, node: QueryNode) -> str:
        try:
            value = Interpreter(self.store).evaluate(node.expr)
            return fmt(value)
        except ComputorNameError:
            if not self._has_func_call_with_free_arg(node.expr):
                raise
            return self._symbolic_query(node.expr)

    def _symbolic_query(self, expr: Node) -> str:
        """Inline function calls symbolically, then format as polynomial or AST."""
        inlined = self._symbolic_inline(expr)
        free = set()
        self._collect_free_vars(inlined, free)
        if len(free) == 1:
            var = next(iter(free))
            try:
                poly = Normalizer(self.store).to_polynomial(inlined, var)
                return fmt_polynomial(poly, var)
            except Exception:
                pass
        simplified = Normalizer(self.store).simplify(inlined, next(iter(free)) if len(free) == 1 else "")
        return fmt_ast(simplified)

    def _has_func_call_with_free_arg(self, node: Node) -> bool:
        """True if any function call in node has a free-variable argument."""
        if isinstance(node, FunctionCallNode):
            for arg in node.args:
                free = set()
                self._collect_free_vars(arg, free)
                if free:
                    return True
        if isinstance(node, BinaryOperationNode):
            return (self._has_func_call_with_free_arg(node.left)
                    or self._has_func_call_with_free_arg(node.right))
        if isinstance(node, (UnaryMinusNode, UnaryPlusNode)):
            return self._has_func_call_with_free_arg(node.operand)
        return False

    def _symbolic_inline(self, node: Node) -> Node:
        """Recursively replace function calls with their expanded body."""
        if isinstance(node, FunctionCallNode):
            try:
                func = self.store.get(node.func_name)
            except Exception:
                return node
            if isinstance(func, Function):
                inlined_arg = self._symbolic_inline(node.args[0])
                return self._substitute_ast(func.body, func.param, inlined_arg)
            return node
        if isinstance(node, BinaryOperationNode):
            return BinaryOperationNode(
                self._symbolic_inline(node.left), node.op, self._symbolic_inline(node.right)
            )
        if isinstance(node, UnaryMinusNode):
            return UnaryMinusNode(self._symbolic_inline(node.operand))
        if isinstance(node, UnaryPlusNode):
            return UnaryPlusNode(self._symbolic_inline(node.operand))
        return node

    def _substitute_ast(self, node: Node, param: str, value: Node) -> Node:
        """Replace all VariableNode(param) with value in node."""
        if isinstance(node, VariableNode) and node.value.lower() == param.lower():
            return value
        if isinstance(node, BinaryOperationNode):
            return BinaryOperationNode(
                self._substitute_ast(node.left, param, value),
                node.op,
                self._substitute_ast(node.right, param, value),
            )
        if isinstance(node, UnaryMinusNode):
            return UnaryMinusNode(self._substitute_ast(node.operand, param, value))
        if isinstance(node, UnaryPlusNode):
            return UnaryPlusNode(self._substitute_ast(node.operand, param, value))
        if isinstance(node, FunctionCallNode):
            new_args = [self._substitute_ast(a, param, value) for a in node.args]
            return FunctionCallNode(node.func_name, new_args)
        return node

    def _handle_expr(self, node: Node) -> str:
        value = Interpreter(self.store).evaluate(node)
        return fmt(value)

    def _handle_solve(self, node: SolveNode) -> str:
        if isinstance(node.lhs, FunctionCallNode):
            return self._solve_function(node)
        return self._solve_expression(node)

    def _solve_function(self, node: SolveNode) -> str:
        func_name = node.lhs.func_name
        param = node.lhs.args[0].value if node.lhs.args else "x"
        func = self.store.get(func_name)
        if not isinstance(func, Function):
            raise ComputorTypeError(f"'{func_name}' is not a function")
        rhs_value = Interpreter(self.store).evaluate(node.rhs)
        poly = Normalizer(self.store).to_polynomial_for_solve(func.body, rhs_value, param)
        result = PolynomialSolver.solve(poly)
        return fmt_solve(result, poly, var=param)

    def _solve_expression(self, node: SolveNode) -> str:
        var = self._find_free_variable(node.lhs)
        if var is None:
            raise ComputorSolverError("No free variable found in equation to solve")
        rhs_value = Interpreter(self.store).evaluate(node.rhs)
        poly = Normalizer(self.store).to_polynomial_for_solve(node.lhs, rhs_value, var)
        result = PolynomialSolver.solve(poly)
        return fmt_solve(result, poly, var=var)

    def _find_free_variable(self, node: Node) -> str:
        """Return the single free variable name (not in store) in the AST."""
        free = set()
        self._collect_free_vars(node, free)
        if len(free) == 0:
            raise ComputorSolverError("No free variable found in equation to solve")
        if len(free) > 1:
            raise ComputorSolverError(
                f"Ambiguous equation: multiple free variables {sorted(free)}"
            )
        return next(iter(free))

    def _collect_free_vars(self, node: Node, free: set) -> None:
        if isinstance(node, VariableNode):
            try:
                self.store.get(node.value)
            except Exception:
                free.add(node.value)
        elif isinstance(node, (UnaryMinusNode, UnaryPlusNode)):
            self._collect_free_vars(node.operand, free)
        elif isinstance(node, BinaryOperationNode):
            self._collect_free_vars(node.left, free)
            self._collect_free_vars(node.right, free)
        elif isinstance(node, FunctionCallNode):
            for arg in node.args:
                self._collect_free_vars(arg, free)
