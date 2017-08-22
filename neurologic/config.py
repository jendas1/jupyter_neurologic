import os

from lark import Lark

from neurologic.lark_utils import patch_tree, named_children

FINAL_PREFIX = "__final"
VARIANT_PREFIX = "__Var"

neurologic_grammar = open(os.path.join(os.path.dirname(__file__), "neurologic_grammar.g"), 'r').read()
neurologic_parser = Lark(neurologic_grammar, start='rule_file')

patch_tree(named_children)


def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)

    wrapper.has_run = False
    return wrapper
