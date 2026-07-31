import abc
from abc import ABC


class Node(ABC):

    @abc.abstractmethod
    def __init__(self, name, value):
        self.name = name
        self.value = value

    @abc.abstractmethod
    def __repr__(self): ...

    @abc.abstractmethod
    def __eq__(self, other): ...

    @abc.abstractmethod
    def child_nodes(self) -> list: ...

    def _label(self) -> str:
        return repr(self)

    def print_tree(self, _pfx="", _last=True):
        connector = "└── " if _last else "├── "
        print(_pfx + (connector if _pfx else "") + self._label())
        children = self.child_nodes()
        new_pfx = _pfx + ("    " if (_last or not _pfx) else "│   ")
        for i, child in enumerate(children):
            child.print_tree(new_pfx, i == len(children) - 1)


class StatementNode(Node):
    name = "Statement"

    def __init__(self, left, operation, right):
        self.left = left
        self.operation = operation
        self.right = right

    def __repr__(self):
        return f"Statement({self.left} {self.operation} {self.right})"

    def __eq__(self, other):
        return False

    def child_nodes(self) -> list:
        children = []
        if isinstance(self.left, Node):
            children.append(self.left)
        if isinstance(self.right, Node):
            children.append(self.right)
        return children


class UnaryMinusNode(Node):
    name = "UnaryMinus"

    def __init__(self, operand):
        super().__init__(self.name, "-")
        self.operand = operand

    def __repr__(self):
        return f"(-{self.operand})"

    def __eq__(self, other):
        if isinstance(other, UnaryMinusNode):
            return self.operand == other.operand
        return False

    def child_nodes(self) -> list:
        return [self.operand]

    def _label(self) -> str:
        return "[-]"


class UnaryPlusNode(Node):
    name = "UnaryPlus"

    def __init__(self, operand):
        super().__init__(self.name, "+")
        self.operand = operand

    def __repr__(self):
        return f"(+{self.operand})"

    def __eq__(self, other):
        if isinstance(other, UnaryPlusNode):
            return self.operand == other.operand
        return False

    def child_nodes(self) -> list:
        return [self.operand]

    def _label(self) -> str:
        return "[+]"


class BinaryOperationNode(Node):
    name = "BinaryOperation"

    def __init__(self, left, op, right):
        super().__init__(self.name, op)
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"

    def __eq__(self, other):
        if isinstance(other, BinaryOperationNode):
            return (
                self.op == other.op
                and self.left == other.left
                and self.right == other.right
            )
        return False

    def child_nodes(self) -> list:
        return [self.left, self.right]

    def _label(self) -> str:
        return f"[{self.op}]"


class NumberNode(Node):
    name = "Number"

    def __init__(self, value: str):
        super().__init__(self.name, value)

    def __repr__(self):
        return f"Number({self.value})"

    def __eq__(self, other):
        if isinstance(other, NumberNode):
            return self.value == other.value
        return False

    def child_nodes(self) -> list:
        return []

    def _label(self) -> str:
        return self.value


class VariableNode(Node):
    name = "Variable"

    def __init__(self, value):
        super().__init__(self.name, value)

    def __repr__(self):
        return f"Variable({self.value})"

    def __eq__(self, other):
        if isinstance(other, VariableNode):
            return self.value == other.value
        return False

    def child_nodes(self) -> list:
        return []

    def _label(self) -> str:
        return self.value


class FunctionCallNode(Node):
    name = "FunctionCall"

    def __init__(self, func_name, args):
        super().__init__(self.name, func_name)
        self.func_name = func_name
        self.args = args

    def __repr__(self):
        return f"FunctionCall({self.func_name}:{self.args})"

    def __eq__(self, other):
        if isinstance(other, FunctionCallNode):
            return (
                self.func_name == other.func_name
                and len(self.args) == len(other.args)
                and all(a == b for a, b in zip(self.args, other.args))
            )
        return False

    def child_nodes(self) -> list:
        return self.args

    def _label(self) -> str:
        return f"call {self.func_name}"


class MatrixNode(Node):
    name = "Matrix"

    def __init__(self, value):
        super().__init__(self.name, value)

    def __repr__(self):
        return f"Matrix({self.value})"

    def __eq__(self, other):
        if isinstance(other, MatrixNode):
            return self.value == other.value
        return False

    def child_nodes(self) -> list:
        return [node for row in self.value for node in row]

    def _label(self) -> str:
        rows = len(self.value)
        cols = max((len(r) for r in self.value), default=0)
        return f"Matrix[{rows}×{cols}]"


class FunctionDefinitionNode(StatementNode):
    def __init__(self, name, args, expression):
        if isinstance(args, VariableNode):
            args = [args]
        elif isinstance(args, list):
            if not all(isinstance(x, VariableNode) for x in args):
                raise ValueError("Wrong arguments type in FunctionDefinitionNode")
        else:
            raise ValueError("Wrong arguments type in FunctionDefinitionNode")
        self.name = name
        self.args_count = len(args)
        self.args = args
        self.expression = expression
        super().__init__(f"{self.name}({','.join([a.value for a in args])})", "def", expression)

    def __repr__(self):
        return f"FunctionDefinitionNode({self.name}({self.args_count} args): {self.expression})"

    def __eq__(self, other):
        if isinstance(other, FunctionDefinitionNode):
            return (
                self.name == other.name
                and self.args_count == other.args_count
                and self.expression == other.expression
                and all(a == b for a, b in zip(self.args, other.args))
            )
        return False

    def child_nodes(self) -> list:
        return self.args + [self.expression]

    def _label(self) -> str:
        params = ", ".join(a.value for a in self.args)
        return f"def {self.name}({params})"


class Equality(StatementNode):
    operation = "="

    def __init__(self, left, right):
        self.left = left
        self.right = right
        super().__init__(left, self.operation, right)

    def __repr__(self):
        return f"Equality({self.left} = {self.right})"

    def __eq__(self, other):
        if isinstance(other, Equality):
            return self.left == other.left and self.right == other.right
        return False

    def _label(self) -> str:
        if isinstance(self.left, VariableNode):
            return f"= (assign {self.left.value})"
        return "= (equation)"


class QueryNode(StatementNode):
    """expr = ?  — вычислить/показать значение выражения"""

    def __init__(self, expr):
        self.expr = expr
        super().__init__(expr, "=", "?")

    def __repr__(self):
        return f"Query({self.expr})"

    def __eq__(self, other):
        if isinstance(other, QueryNode):
            return self.expr == other.expr
        return False

    def child_nodes(self) -> list:
        return [self.expr]

    def _label(self) -> str:
        return "? (query)"


class SolveNode(StatementNode):
    """lhs = rhs ?  — решить уравнение"""

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        super().__init__(lhs, "=?", rhs)

    def __repr__(self):
        return f"Solve({self.lhs} = {self.rhs})"

    def __eq__(self, other):
        if isinstance(other, SolveNode):
            return self.lhs == other.lhs and self.rhs == other.rhs
        return False

    def child_nodes(self) -> list:
        return [self.lhs, self.rhs]

    def _label(self) -> str:
        return "? (solve)"


class ComparisonNode(StatementNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
        super().__init__(left, operator, right)

    def __repr__(self):
        return f"Comparison({self.left} {self.operator} {self.right})"

    def __eq__(self, other):
        if isinstance(other, ComparisonNode):
            return (
                self.left == other.left
                and self.operator == other.operator
                and self.right == other.right
            )
        return False

    def _label(self) -> str:
        return f"[{self.operator}]"