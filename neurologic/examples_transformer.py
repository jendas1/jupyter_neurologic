import logging
import os

from lark import Lark, Transformer, Tree
from lark.lexer import Token

from neurologic.lark_utils import patch_tree
from neurologic import lark_utils
from neurologic.config import FINAL_PREFIX
from neurologic.template_transformer import ToCodeTransformer, FixZeroArity

neurologic_grammar = open(os.path.join(os.path.dirname(__file__), "neurologic_grammar.g"), 'r').read()
neurologic_parser = Lark(neurologic_grammar, start='rule_file')

logger = logging.getLogger(__name__)

patch_tree(lark_utils.named_children)


class ExampleToOldVersion(Transformer):
    @staticmethod
    def weighted_rule_without_metadata(children):
        weight = children[0]
        rule = children[1]
        head_formula = rule['head']
        head_formula["PREDICATE"] = Token("PREDICATE", FINAL_PREFIX + head_formula["PREDICATE"].value)
        return Tree('weighted_conjunction', [weight, *rule["body"], head_formula])

    @staticmethod
    def weighted_rule(children):
        return children[0]


def transform(text):
    logger.debug(f"Transforming code: {text}")
    tree = neurologic_parser.parse(text)
    fixed_zero_arity = FixZeroArity().transform(tree)
    old_version = ExampleToOldVersion().transform(fixed_zero_arity)
    transformed_code = ToCodeTransformer().transform(old_version)
    logger.debug(f"Transformed code: {transformed_code}")
    return transformed_code
