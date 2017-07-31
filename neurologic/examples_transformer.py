from itertools import product
import logging
from lark import Lark, Transformer, Tree
from lark.lexer import Token
import os

neurologic_grammar = open(os.path.join(os.path.dirname(__file__), "neurologic_grammar.g"), 'r').read()
neurologic_parser = Lark(neurologic_grammar, start='rule_file')

logger = logging.getLogger(__name__)

