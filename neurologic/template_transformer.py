import logging
import os
from itertools import product
import lark
from lark import Lark, Transformer, Tree
from lark.lexer import Token
from lark.tree import Visitor

import neurologic
from neurologic import lark_utils
from neurologic.config import FINAL_PREFIX, VARIANT_PREFIX, neurologic_parser
from neurologic.lark_utils import TreeSubstituter, TokenRenamer

logger = logging.getLogger(__name__)


class RuleSpecializationTransformer(Transformer):
    @staticmethod
    def weighted_rule_with_metadata(children):
        weighted_rule_without_metadata = children[0]
        weight = weighted_rule_without_metadata["weight"]
        rule = weighted_rule_without_metadata["rule"]
        metadata = children[1]
        specialization_variables = [variable[0] for variable in metadata.find_data("specialization_variable")]
        other_metadata = [value for value in metadata.children if value.data != "specialization_variable"]
        member_formulas = list(rule.find_data("member_formula"))
        variable_constants = {}
        for specialization_variable in specialization_variables:
            for member_formula in member_formulas:
                if member_formula["term_list"][0] == specialization_variable:
                    variable_constants[specialization_variable] = member_formula["term_list"][1].children
        assert len(variable_constants) == len(list(specialization_variables))
        variable_substitutions = []
        for variable, values in variable_constants.items():
            variable_substitutions.append([(variable, value) for value in values])
        rules = []
        stripped_rule = Tree('rule',
                             [child for child in rule.children if len(list(child.find_data("member_formula"))) == 0])
        for substitutions in product(*variable_substitutions):
            new_rule = stripped_rule
            for variable, value in substitutions:
                new_rule = TreeSubstituter(variable, value).transform(new_rule)
            rules.append(new_rule)
        rules = [Tree("weighted_rule_without_metadata", [weight, rule]) for rule in rules]
        if other_metadata:
            rules = [Tree("weighted_rule_with_metadata", [rule, Tree('metadata', other_metadata)]) for rule in rules]
        if specialization_variables:
            return rules
        else:
            return Tree("weighted_rule_with_metadata", children)

    @staticmethod
    def rule_file(lines):
        output = []
        for line in lines:
            if isinstance(line, list):
                output += [child for child in line]
            else:
                output.append(line)
        return Tree('rule_file', output)


lark.tree.Visitor.__default__ = lambda self, item: item

grouped_name = {
    "weighted_rule": ["weighted_rule_without_metadata", "weighted_rule_with_metadata"],
    "special_formula": ["member_formula", "builtin_formula"],
    "atomic_formula": ["special_formula", "normal_atomic_formula"],
}
name_to_group_name = {name: group for group, names in grouped_name.items() for name in names}


class DFSTransformer:
    def transform(self, root):
        if type(root) != Tree:
            return root
        transformed_children = []
        for child in root.children:
            transformed_children.append(self.transform(child))
        if hasattr(self, root.data):
            f = getattr(self, root.data)
        elif root.data in name_to_group_name and hasattr(self, name_to_group_name[root.data]):
            f = getattr(self, name_to_group_name[root.data])
        else:
            f = self.default
        return f(Tree(root.data, transformed_children))

    def default(self, root):
        return root


class AtomicFormulaEraser(Transformer):
    def __init__(self, target):
        self.target = target

    def rule(self, children):
        return Tree("rule", list(filter(lambda x: x != self.target, children)))


class RangePredicateTransformer:
    @staticmethod
    def transform(root):
        for ind, line in enumerate(root.children[:]):
            range_preds = line.find_pred(
                lambda root: root.data == "normal_atomic_formula" and root["PREDICATE"].value == "range")
            for range_pred in range_preds:
                variable = range_pred["term_list"][0]
                start = range_pred["term_list"][1].value
                end = range_pred["term_list"][2].value
                try:
                    substitution = Tree('constant_list',
                                        [Token("CONSTANT", str(i)) for i in range(int(start), int(end) + 1)])
                except ValueError:
                    assert type(start) == str and type(end) == str
                    substitution = Tree('constant_list',
                                        [Token("CONSTANT", chr(i)) for i in range(ord(start), ord(end)+1)])
                root.children[ind] = AtomicFormulaEraser(range_pred).transform(root.children[ind])
                root.children[ind] = TreeSubstituter(variable, substitution).transform(root.children[ind])
        return root


class LambdaKappaTransformer(DFSTransformer):
    def __init__(self):
        self.rule_variants = {}

    def weighted_rule_without_metadata(self, weighted_rule_without_metadata):
        # Transform weighted_rule_without_metadata to 2 rules
        output = []
        weight = weighted_rule_without_metadata["weight"]
        rule = weighted_rule_without_metadata["rule"]
        head = rule["head"]
        head_predicate = head["PREDICATE"]
        self.rule_variants.setdefault(head_predicate, 0)
        new_name = VARIANT_PREFIX + str(self.rule_variants[head_predicate]) + "_" + head_predicate.value
        self.rule_variants[head_predicate] += 1
        renamed_head = TokenRenamer("PREDICATE", head_predicate.value, new_name).transform(head)
        tail = rule["body"]
        # Add Lambda rule
        output.append(Tree('rule', [renamed_head, *tail]))
        # Add Kappa rule
        output.append(Tree('weighted_rule_without_metadata', [weight, Tree('rule', [head, renamed_head])]))
        return output

    def weighted_rule_with_metadata(self, root):
        children = root.children[0]
        head = root.children[0][0]["head"]
        arity = len(head["term_list"].children)
        children.append(Tree('predicate_metadata', [head["PREDICATE"], str(arity), root["metadata"]]))
        return children

    @staticmethod
    def rule_file(root):
        output = []
        for line in root.children:
            if isinstance(line, list):
                output += [child for child in line]
            else:
                output.append(line)
        return Tree('rule_file', output)


class LambdaKappaJoiner:
    @staticmethod
    def transform(root):
        rule_variants = {}
        for line in root.children[:]:
            child = line
            if child.data == "rule" and child["head"]["PREDICATE"].value.startswith(VARIANT_PREFIX):
                rule_variants[child["head"]] = child["body"]
                root.children.remove(line)
        for rule_variant, rule_body in rule_variants.items():
            for line in root.children:
                child = line
                if child.data == "weighted_rule_without_metadata":
                    rule = child['rule']
                    body = rule['body']
                    if body == rule_variant:
                        rule.children = [rule['head'], *rule_body]
        return root


class FixZeroArity(Transformer):
    def _get_func(self, name):
        if name in ["predicate_metadata", "predicate_offset"]:
            return lambda children: Tree(name,
                                         [children[0], Token("INT", str(max(int(children[1].value), 1))), children[2]])
        else:
            return super()._get_func(name)

    @staticmethod
    def normal_atomic_formula(children):
        predicate = children[0]
        term_list = children[1]
        if len(term_list.children) == 0:
            term_list = Tree('term_list', [Token('CONSTANT', 'a')])
        return Tree('normal_atomic_formula', [predicate, term_list])


class ReduceFinalKappa:
    @staticmethod
    def transform(root):
        output = root.children
        for name, arity in list_all_predicates(root):
            terms = ",".join(["__X" + str(i) for i in range(arity)])
            rule = f"<1.0> finalKappa(a) :- {name}({terms}),{FINAL_PREFIX}{name}({terms}). [identity]"
            output.append(neurologic_parser.parse(rule).children[0])
        rule = f"finalKappa/1 [identity]"
        output.append(neurologic_parser.parse(rule).children[0])
        return Tree(root.data, output)


def list_all_predicates(root):
    atomic_formulas = root.find_data("normal_atomic_formula")
    predicates = set()
    for atomic_formula in atomic_formulas:
        predicate_name = atomic_formula["PREDICATE"].value
        predicate_arity = len(atomic_formula["term_list"].children)
        predicates.add((predicate_name, predicate_arity))
    return predicates


class FixedOffsetTransformer:
    @staticmethod
    def transform(root):
        output = root.children
        for name, arity in list_all_predicates(root):
            output.append(
                Tree('predicate_offset', [Token("PREDICATE", name), str(arity),
                                          Tree('fixed_weight', [Token("SIGNED_NUMBER", '0.0')])]))
        return Tree(root.data, output)


class ToCodeTransformer(Transformer):
    def _get_func(self, name):
        if name in ["atomic_formula", "initial_weight", "meaningful_line", "term", "metadata_value", "special_formula",
                    "weighted_rule"]:
            return lambda x: x[0]
        elif name in ["weighted_rule_without_metadata", "weighted_fact", "weighted_rule_with_metadata"]:
            return lambda x: x[0] + " " + x[1]
        elif name in ["normal_atomic_formula", "builtin_formula"]:
            return lambda children: children[0] + children[1]
        else:
            return super()._get_func(name)

    @staticmethod
    def term_list(children):
        return "(" + ",".join(children) + ")"

    @staticmethod
    def rule(children):
        return children[0] + " :- " + ",".join(children[1:]) + "."

    @staticmethod
    def fixed_weight(children):
        return "<" + children[0] + ">"

    @staticmethod
    def specialization_variable(children):
        return "^" + children[0]

    @staticmethod
    def metadata(children):
        return "[" + ",".join(children) + "]"

    @staticmethod
    def predicate_metadata(children):
        return children[0] + "/" + children[1] + " " + children[2]

    @staticmethod
    def predicate_offset(children):
        return children[0] + "/" + children[1] + " " + children[2]

    @staticmethod
    def fact(children):
        return children[0] + "."

    @staticmethod
    def weighted_conjunction(children):
        return children[0] + " " + ",".join(children[1:]) + "."

    @staticmethod
    def rule_file(children):
        return "\n".join(children)


def transform(text):
    logger.debug(f"Transforming code: {text}")
    tree = neurologic_parser.parse(text)
    range_transformed = RangePredicateTransformer().transform(tree)
    unfolded_specialization = RuleSpecializationTransformer().transform(range_transformed)
    fixed_arity = FixZeroArity().transform(unfolded_specialization)
    reduced_final_kappa = ReduceFinalKappa().transform(fixed_arity)
    fixed_offset = FixedOffsetTransformer().transform(reduced_final_kappa)
    lambda_kappa = LambdaKappaTransformer().transform(fixed_offset)
    transformed_code = ToCodeTransformer().transform(lambda_kappa)
    logger.debug(f"Transformed code: {transformed_code}")
    return transformed_code


def transform_result(text):
    tree = neurologic_parser.parse(text)
    logger.debug(f"Transforming code: {text}")
    joined_kappa_lambda = LambdaKappaJoiner.transform(tree)
    transformed_code = ToCodeTransformer().transform(joined_kappa_lambda)
    logger.debug(f"Transformed code: {transformed_code}")
    return transformed_code
