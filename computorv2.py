from parsing.parser import parser


class ComputorV2:
    def __init__(self):
        self.parser = parser

    def add_input(self, text):
        result = parser.parse(text)
        if result:
            result.print_tree()