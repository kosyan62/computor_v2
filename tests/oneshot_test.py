from computor_v2.parsing.parser import parser
from computor_v2.store import Store
from computor_v2.interpreter import Interpreter

R"""
Этот файл — для ручной отладки. Запуск:
    pytest tests/oneshot_test.py -s
"""


def evaluate(expr: str, store: Store = None):
    store = store or Store()
    node = parser.parse(expr)
    return Interpreter(store).evaluate(node)


def test_debug():
    store = Store()
    interp = Interpreter(store)

    cases = [
        "2 + 3",
        "10 / 4",
        "2 ^ 8",
        "sqrt(9)",
        "sqrt(2)",
        "2 * i",
        "i * i",
    ]

    for expr in cases:
        node = parser.parse(expr)
        result = interp.evaluate(node)
        print(f"  {expr!r:20} => {result}")