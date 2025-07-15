from computor_v2.parsing.AST import FunctionCallNode, TokenNode, NumberNode
from computor_v2.parsing.parser import parser
from logging import getLogger, StreamHandler

logger = getLogger(__name__)
logger.addHandler(StreamHandler())


def test_debug():
    """This test can be used to debug parser"""

    test_data = ("max(1, 2, 3)", FunctionCallNode('max', [NumberNode(1.0), NumberNode(2.0), NumberNode(3.0)],))
    ret = parser.parsedebug(test_data[0], debug=logger)
    assert ret == test_data[1]
