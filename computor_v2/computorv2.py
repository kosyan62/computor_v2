from computor_v2.parsing.parser import parser
from computor_v2.parsing.AST import (
    Equality, FunctionDefinitionNode, QueryNode, SolveNode, VariableNode,
)
from computor_v2.store import Store
from computor_v2.interpreter import Interpreter
from computor_v2.errors import ComputorError
from computor_v2.types import Function


class ComputorV2:
    def __init__(self):
        self.store = Store()

    def add_input(self, text: str):
        try:
            result = parser.parse(text)
            if result is None:
                return
            output = self._dispatch(result)
            if output is not None:
                print(output)
        except ComputorError as e:
            print(f"Error: {e}")
        except (SyntaxError, ValueError) as e:
            print(f"Syntax error: {e}")

    def _dispatch(self, node):
        interp = Interpreter(self.store)

        if isinstance(node, FunctionDefinitionNode):
            self.store.set(node.name, Function(node.args[0].value, node.expression))
            return f"{node.name}({node.args[0].value}) = {node.expression}"

        if isinstance(node, Equality) and isinstance(node.left, VariableNode):
            value = interp.evaluate(node.right)
            self.store.set(node.left.value, value)
            return str(value)

        if isinstance(node, QueryNode):
            value = interp.evaluate(node.expr)
            return str(value)

        # bare expression — вычислить и показать
        value = interp.evaluate(node)
        return str(value)