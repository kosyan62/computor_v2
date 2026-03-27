import abc
from abc import ABC


class Node(ABC):
    """
    Represents a base abstract node with a name, value, and child nodes.

    This abstract base class is designed to serve as a foundation for creating
    various types of nodes, each with a unique name, a corresponding value, and an
    optional list of child nodes. It enforces the implementation of specific
    methods (`__repr__` and `__eq__`) in any concrete subclass, ensuring
    consistent behavior. It also supports tree-structured data representation
    through its `print_tree` method.

    Attributes:
        name (str): The name or identifier of the node.
        value: The value or payload associated with the node.
        children (list): A list of child nodes that are connected to the current
            node. Defaults to an empty list.
    """

    @abc.abstractmethod
    def __init__(self, name, value, children=None):
        self.name = name
        self.value = value
        self.children = children if children else []

    @abc.abstractmethod
    def __repr__(self):
        raise NotImplementedError

    @abc.abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

    def print_tree(self, indent=0):
        print("  " * indent + str(self))
        for child in self.children:
            child.print_tree(indent + 1)


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

    def print_tree(self, indent=0):
        # print tree for left and for right
        print("Left part: ")
        self.left.print_tree(indent)
        print("Right part after operation " + self.operation + ": ")
        self.right.print_tree(indent)

class UnaryMinusNode(Node):
    name = "UnaryMinus"

    def __init__(self, operand):
        super().__init__(self.name, "-", [operand])
        self.operand = operand

    def __repr__(self):
        return f"(-{self.operand})"

    def __eq__(self, other):
        if isinstance(other, UnaryMinusNode):
            return self.operand == other.operand
        return False


class UnaryPlusNode(Node):
    name = "UnaryPlus"

    def __init__(self, operand):
        super().__init__(self.name, "+", [operand])
        self.operand = operand

    def __repr__(self):
        return f"(+{self.operand})"

    def __eq__(self, other):
        if isinstance(other, UnaryPlusNode):
            return self.operand == other.operand
        return False


class BinaryOperationNode(Node):
    name = "BinaryOperation"

    def __init__(self, left, op, right):
        super().__init__(self.name, op, [left, right])
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


class FunctionCallNode(Node):
    name = "FunctionCall"

    def __init__(self, function_name, args):
        super().__init__(self.name, function_name)
        self.args = args

    def __repr__(self):
        return f"FunctionCall({self.value}:{self.args})"

    def __eq__(self, other):
        if isinstance(other, FunctionCallNode):
            return (
                self.value == other.value
                and len(self.args) == len(other.args)
                and all(a == b for a, b in zip(self.args, other.args))
            )
        return False


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


class FunctionDefinitionNode(StatementNode):
    def __init__(self, name, args, expression):
        if isinstance(args, VariableNode):
            args = [args]
        elif isinstance(args, list):
            if not all([isinstance(x, VariableNode) for x in args]):
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


class QueryNode(StatementNode):
    """expr = ? — вычислить/показать значение выражения"""

    def __init__(self, expr):
        self.expr = expr
        super().__init__(expr, "=", "?")

    def __repr__(self):
        return f"Query({self.expr})"

    def __eq__(self, other):
        if isinstance(other, QueryNode):
            return self.expr == other.expr
        return False


class SolveNode(StatementNode):
    """funcCall(x) = rhs ?  — решить уравнение"""

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
