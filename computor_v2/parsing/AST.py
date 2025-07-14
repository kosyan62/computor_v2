import abc
from abc import ABC


class Node(ABC):
    @abc.abstractmethod
    def __init__(self, name, value, children=None):
        self.value = value
        self.children = children if children else []

    def print_tree(self, indent=0):
        print("  " * indent + str(self))
        for child in self.children:
            child.print_tree(indent + 1)


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

    def __init__(self, value):
        super().__init__(self.name, value)

    def __repr__(self):
        return f"Number({self.value})"

    def __eq__(self, other):
        if isinstance(other, NumberNode):
            return self.value == other.value
        return False


class TokenNode(Node):
    name = "Token"

    def __init__(self, value):
        super().__init__(self.name, value)

    def __repr__(self):
        token = f"Token({self.name}"
        if self.value:
            token += f" <{self.value}>)"
        else:
            token += ")"
        return token

    def __eq__(self, other):
        if isinstance(other, TokenNode):
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
            return self.value == other.value and self.args == other.args
        return False


def __repr__(self):
    return f"FunctionDefinition({self.value})"


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


class FunctionDefinition:
    def __init__(self, name, args, expression):
        self.name = name
        self.args_count = len(args)
        self.args = args
        self.expression = expression


class Equality:
    def __init__(self, left, right):
        self.left = left
        self.right = right


class Unequality:
    def __init__(self, left, sign, right):
        self.left = left
        self.right = right
