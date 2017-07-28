from itertools import product
import logging
from lark import Lark, Transformer, Tree
from lark.lexer import Token
import os

neurologic_grammar = open(os.path.join(os.path.dirname(__file__), "neurologic_grammar.g"), 'r').read()
neurologic_parser = Lark(neurologic_grammar, start='rule_file')

logger = logging.getLogger(__name__)


class TokenRenamer:
    def __init__(self, token_type, old_val, new_val):
        self.token_type = token_type
        self.old_val = old_val
        self.new_val = new_val

    def transform(self, root):
        if isinstance(root, Token):
            if root.type == self.token_type and root.value == self.old_val:
                root = Token(root.type, self.new_val)
            return root
        else:
            return Tree(root.data, [self.transform(child) for child in root.children])


class TreeSubstituter:
    def __init__(self, target, replacement):
        self.target = target
        self.replacement = replacement

    def transform(self, root):
        if root == self.target:
            return self.replacement
        elif isinstance(root, Token):
            return root
        else:
            return Tree(root.data, [self.transform(child) for child in root.children])


class RuleSpecializationTransformer(Transformer):
    @staticmethod
    def weighted_rule_with_metadata(children):
        weighted_rule_without_metadata = children[0]
        weight = weighted_rule_without_metadata.children[0]
        rule = weighted_rule_without_metadata.children[1]
        metadata = children[1]
        specialization_variables = [variable.children[0] for variable in metadata.find_data("specialization_variable")]
        other_metadata = [value for value in metadata.children if value.data != "specialization_variable"]
        member_formulas = list(rule.find_data("member_formula"))
        variable_constants = {}
        for specialization_variable in specialization_variables:
            for member_formula in member_formulas:
                if member_formula.children[1].children[0] == specialization_variable:
                    variable_constants[specialization_variable] = member_formula.children[1].children[1].children
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
            if isinstance(line.children[0].children[0], list):
                output += [Tree('meaningful_line', [Tree('weighted_rule', [child])]) for child in
                           line.children[0].children[0]]
            else:
                output.append(line)
        return Tree('rule_file', output)


class LambdaKappaTransformer(Transformer):
    def __init__(self):
        self.rule_variants = {}

    def weighted_rule(self, items):
        item = items[0]
        has_metadata = item.data == 'weighted_rule_with_metadata'
        if has_metadata:
            weighted_rule_without_metadata = item.children[0]
        else:
            weighted_rule_without_metadata = item
        # Transform weighted_rule_without_metadata to 2 rules
        output = []
        weight = weighted_rule_without_metadata.children[0]
        rule = weighted_rule_without_metadata.children[1]
        head = rule.children[0]
        head_predicate = next(head.scan_values(lambda x: type(x) == Token and x.type == "PREDICATE"))
        self.rule_variants.setdefault(head_predicate, 0)
        new_name = "__Var" + str(self.rule_variants[head_predicate]) + "_" + head_predicate.value
        self.rule_variants[head_predicate] += 1
        renamed_head = TokenRenamer("PREDICATE", head_predicate.value, new_name).transform(head)
        tail = rule.children[1:]
        # Add Kappa/Lambda
        output.append(Tree('rule', [renamed_head, *tail]))
        # Add Lambda/Kappa
        output.append(Tree('weighted_rule_without_metadata', [weight, Tree('rule', [head, renamed_head])]))

        if has_metadata:
            arity = len(head.children[0].children) - 1
            metadata = item.children[1]
            output.append(Tree('predicate_metadata', [Token("PREDICATE", new_name), str(arity), metadata]))
        return output

    @staticmethod
    def rule_file(lines):
        output = []
        for line in lines:
            if isinstance(line.children[0], list):
                output += [Tree('meaningful_line', [child]) for child in line.children[0]]
            else:
                output.append(line)
        return Tree('rule_file', output)


class LambdaKappaJoiner:
    @staticmethod
    def transform(root):
        rule_variants = {}
        for line in root.children[:]:
            child = line.children[0]
            if child.data == "rule" and child.children[0].children[0].children[0].value.startswith("__Var"):
                rule_variants[child.children[0]] = child.children[1:]
                root.children.remove(line)
        for rule_variant, rule_body in rule_variants.items():
            for line in root.children:
                child = line.children[0]
                if child.data == "weighted_rule":
                    rule = child.children[0].children[1]
                    body = rule.children[1]
                    if body == rule_variant:
                        rule.children = [rule.children[0], *rule_body]
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
            rule = f"<1.0> finalKappa(a) :- {name}({terms}),final{name}({terms}). [identity]"
            output.append(neurologic_parser.parse(rule).children[0])
        rule = f"finalKappa/1 [identity]"
        output.append(neurologic_parser.parse(rule).children[0])
        return Tree(root.data, output)


def list_all_predicates(root):
    atomic_formulas = root.find_data("normal_atomic_formula")
    predicates = set()
    for atomic_formula in atomic_formulas:
        predicate_name = atomic_formula.children[0].value
        predicate_arity = len(atomic_formula.children[1].children)
        predicates.add((predicate_name, predicate_arity))
    return predicates


class FixedOffsetTransformer:
    @staticmethod
    def transform(root):
        output = root.children
        for name, arity in list_all_predicates(root):
            output.append(
                Tree('meaningful_line', [
                    Tree('predicate_offset', [Token("PREDICATE", name), str(arity),
                                              Tree('fixed_weight', [Token("SIGNED_NUMBER", '0.0')])])]))
        return Tree(root.data, output)


class ToCodeTransformer(Transformer):
    def _get_func(self, name):
        if name in ["atomic_formula", "initial_weight", "meaningful_line", "term", "metadata_value", "special_formula", "weighted_rule"]:
            return lambda x: x[0]
        elif name in ["weighted_rule_without_metadata", "weighted_fact"]:
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
    def rule_file(children):
        return "\n".join(children)


def transform(text):
    logger.debug(f"Transforming code: {text}")
    tree = neurologic_parser.parse(text)
    unfolded_specialization = RuleSpecializationTransformer().transform(tree)
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


input_text = r"""
0.0 winner(Group1,Group2) :- nice(jenda),_member(Group1,[1,2,3]),_member(Group2,[a,b,c]). [lukasiewicz,^Group1,^Group2]
0.0 winner() :- nice(jenda). [lukasiewicz]
"""
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    result = transform(input_text)
