class Node:
    def __init__(self, name, children=None, leaf=None):
        self.name = name
        if children:
            self.children = children
        else:
            self.children = []
        self.leaf = leaf

    def __repr__(self):
        return f"{self.name}({self.leaf})"

    def print_tree(self, indent=0):
        print(" " * indent + str(self))
        for child in self.children:
            child.print_tree(indent + 4)


class BinaryOperationNode(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
        super().__init__("BinaryOperation", [left, right], op)

    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"

class NumberNode(Node):
    def __init__(self, value):
        super().__init__("Number", children=[], leaf=value)

    def __repr__(self):
        return f"Number({self.leaf})"


class TokenNode(Node):
    def __init__(self, name, value=None):
        super().__init__("Token", children=[], leaf=name)
        self.value = value

    def __repr__(self):
        token = f"Token({self.leaf}"
        if self.value:
            token += f" <{self.value}>)"
        else:
            token += ")"
        return token


class FunctionCallNode(Node):
    def __init__(self, name, args):
        super().__init__("FunctionCall", children=[], leaf=name)

    def __repr__(self):
        return f"FunctionCall({self.leaf})"


class MatrixNode(Node):
    def __init__(self, matrix):
        super().__init__("Matrix", children=[], leaf=matrix)

    def __repr__(self):
        return f"Matrix({self.leaf})"


