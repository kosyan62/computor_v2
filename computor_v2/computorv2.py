from computor_v2.parsing.parser import parser
from computor_v2.store import Store
from computor_v2.dispatcher import Dispatcher
from computor_v2.errors import ComputorError


class ComputorV2:
    def __init__(self):
        self.store = Store()
        self.dispatcher = Dispatcher(self.store)

    def add_input(self, text: str):
        try:
            node = parser.parse(text)
            if node is None:
                return
            output = self.dispatcher.dispatch(node)
            if output is not None:
                print(output)
        except ComputorError as e:
            print(f"Error: {e}")
        except (SyntaxError, ValueError) as e:
            print(f"Syntax error: {e}")
