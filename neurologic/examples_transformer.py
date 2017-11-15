import logging

from lark import Transformer, Tree
from lark.lexer import Token

from neurologic import lark_utils
from neurologic.config import FINAL_PREFIX, neurologic_parser
from neurologic.lark_utils import patch_tree
from neurologic.template_transformer import ToCodeTransformer, FixZeroArity, DFSTransformer

logger = logging.getLogger(__name__)

patch_tree(lark_utils.named_children)


class ExampleToOldVersion(DFSTransformer):
    """
    New Version: Rule
    `1.0 target_predicate(constant1) :- evidence_predicate(constant2),evidence_predicate(constant3).`
    Old Version: Conjunction
    `1.0 evidence_predicate(constant2),evidence_predicate(constant3),__finaltarget_predicate(constant1).`
    """
    @staticmethod
    def rule(root):
        weight = root["weight"]
        rule = root
        head_formula = rule['head']
        head_formula["PREDICATE"] = Token("PREDICATE", FINAL_PREFIX + head_formula["PREDICATE"].value)
        return Tree('weighted_conjunction', [weight, *rule["body"], head_formula])


def transform_from_tree(tree):
    fixed_zero_arity = FixZeroArity().transform(tree)
    old_version = ExampleToOldVersion().transform(fixed_zero_arity)
    transformed_code = ToCodeTransformer().transform(old_version)
    return transformed_code


def transform(text):
    logger.debug(f"Transforming code: {text}")
    tree = neurologic_parser.parse(text)
    transformed_code = transform_from_tree(tree)
    logger.debug(f"Transformed code: {transformed_code}")
    return transformed_code
