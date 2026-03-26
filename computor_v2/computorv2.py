from computor_v2.parsing.parser import parser


class ComputorV2:
    def __init__(self):
        self.parser = parser

    def add_input(self, text):
        try:
            result = parser.parse(text)
            if result:
                result.print_tree()
        except (SyntaxError, ValueError) as e:
            print(f"Error: {e}")
