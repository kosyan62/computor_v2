import logging
from computor_v2.parsing.parser import parser
from computor_v2.store import Store
from computor_v2.dispatcher import Dispatcher
from computor_v2.errors import ComputorError
from computor_v2.formatter import fmt, fmt_ast
from computor_v2.types import Function

logger = logging.getLogger("computor_v2")


class ComputorV2:
    def __init__(self):
        self.store = Store()
        self.dispatcher = Dispatcher(self.store)

    def add_input(self, text: str):
        try:
            cmd = text.strip().lower()

            if cmd == "vars":
                self._cmd_vars()
                return

            if cmd.startswith("plot ") or cmd == "plot":
                self._cmd_plot(text.strip())
                return

            logger.debug("Input: %r", text)
            node = parser.parse(text)
            if node is None:
                return
            logger.debug("AST: %s", type(node).__name__)
            output = self.dispatcher.dispatch(node)
            if output is not None:
                logger.debug("Result: %r", output)
                print(output)
        except ComputorError as e:
            logger.debug("ComputorError: %s", e)
            print(f"Error: {e}")
        except (SyntaxError, ValueError) as e:
            logger.debug("ParseError: %s", e)
            print(f"Syntax error: {e}")

    def _cmd_vars(self):
        user = self.store.user_vars()
        if not user:
            print("No variables defined.")
            return
        for name, val in sorted(user.items()):
            if isinstance(val, Function):
                print(f"{name}({val.param}) = {fmt_ast(val.body)}")
            else:
                print(f"{name} = {fmt(val)}")

    def _cmd_plot(self, text: str):
        from computor_v2.plotter import plot_function
        from computor_v2.errors import ComputorNameError

        parts = text.split()
        if len(parts) < 2:
            print("Usage: plot <function> [x_min x_max]")
            return

        func_name = parts[1]
        x_min, x_max = -10.0, 10.0
        if len(parts) >= 4:
            try:
                x_min, x_max = float(parts[2]), float(parts[3])
            except ValueError:
                print("Error: x_min and x_max must be numbers")
                return

        try:
            val = self.store.get(func_name)
        except ComputorNameError:
            print(f"Error: '{func_name}' is not defined")
            return

        if not isinstance(val, Function):
            print(f"Error: '{func_name}' is not a function")
            return

        try:
            plot_function(val, func_name, self.store, x_min, x_max)
            print(f"Plotting {func_name}(x) on [{x_min}, {x_max}]")
        except ComputorError as e:
            print(f"Error: {e}")