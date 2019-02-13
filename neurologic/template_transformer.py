import logging
from collections import OrderedDict
from itertools import product
from orderedset import OrderedSet
from lark import Transformer, Tree
from lark.lexer import Token

from neurologic.config import FINAL_PREFIX, VARIANT_PREFIX, neurologic_parser
from neurologic.lark_utils import TreeSubstituter, TokenRenamer, has_metadata, has_weight

logger = logging.getLogger(__name__)

grouped_name = {
    "weighted_rule": ["weighted_rule_without_metadata", "weighted_rule_with_metadata"],
    "special_formula": ["member_formula", "builtin_formula"],
    "atomic_formula": ["special_formula", "normal_atomic_formula"],
}
name_to_group_name = {name: group for group, names in grouped_name.items() for name in names}


class DFSTransformer:
    """
    DepthFirstSearchTransformer
    Similar to :class:`lark.Transformer` but instead of passing only children to function,
    DFSTransformer passes the root of the subtrees.
    """

    def transform(self, root):
        if type(root) != Tree:
            return root
        transformed_children = []
        for child in root.children:
            transformed_children.append(self.transform(child))
        f = self._call_userfunc(root.data)
        return f(Tree(root.data, transformed_children))

    def _call_userfunc(self, name, new_children=None):
        if hasattr(self, name):
            f = getattr(self, name)
        elif name in name_to_group_name and hasattr(self, name_to_group_name[name]):
            f = getattr(self, name_to_group_name[name])
        else:
            f = self.default
        return f

    @staticmethod
    def default(root):
        return root


class RuleSpecializationTransformer(DFSTransformer):
    """
    RuleSpecializationTransformer search for and transform (specialize) rule to multiple specialized rules.
    Example:
    INPUT:
    `0.0 predicate(constant) :- predicate2(SpecVariable),member(SpecVariable,[a,b,c]). [^SpecVariable]`
    OUTPUT:
    `0.0 predicate(constant) :- predicate2(a).
     0.0 predicate(constant) :- predicate2(b).
     0.0 predicate(constant) :- predicate2(c).`
    """

    @staticmethod
    def rule(root):
        rule = root
        if not has_metadata(root):
            return root
        metadata = root["metadata"]
        specialization_variables = [variable[0] for variable in metadata.find_data("specialization_variable")]
        other_metadata = [value for value in metadata.children if value.data != "specialization_variable"]
        member_formulas = list(rule.find_data("member_formula"))
        variable_constants = OrderedDict()
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
        if other_metadata:
            stripped_rule["metadata"] = Tree("metadata", other_metadata)
        else:
            del stripped_rule["metadata"]

        for substitutions in product(*variable_substitutions):
            new_rule = stripped_rule
            for variable, value in substitutions:
                new_rule = TreeSubstituter(variable, value).transform(new_rule)
            rules.append(new_rule)
        if specialization_variables:
            return rules
        else:
            return root

    @staticmethod
    def rule_file(root):
        output = []
        for line in root.children:
            if isinstance(line, list):
                output += [child for child in line]
            else:
                output.append(line)
        return Tree('rule_file', output)


class AtomicFormulaEraser(Transformer):
    def __init__(self, target):
        self.target = target

    def rule(self, children):
        return Tree("rule", list(filter(lambda x: x != self.target, children)))


class RangePredicateTransformer:
    """
    Substitution Transformer to handle special range predicate.
    Range predicate has form `range(-VariableName,+start,+end)` with both start and end inclusive.
    Transformer will substitute every occurence of `VariableName` with list that has constants from `start` to `end`.
    Start and end can be either numbers or letters.
    """

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
                                        [Token("CONSTANT", chr(i)) for i in range(ord(start), ord(end) + 1)])
                root.children[ind] = AtomicFormulaEraser(range_pred).transform(root.children[ind])
                root.children[ind] = TreeSubstituter(variable, substitution).transform(root.children[ind])
        return root


class LambdaKappaTransformer(DFSTransformer):
    """
    Transform new Prolog like representation to Lambda Kappa representation used in LRNN.
    Example:
    INPUT:
    `0.0 happy(Person) :- friends(Person),family(Person).`
    OUTPUT:
    `0.0 happy(Person) :- __Var0_happy(Person).`: Kappa rule
    `__Var0_happy(Person) :- friends(Person),family(Person).`: Lambda rule
    """

    def __init__(self):
        self.rule_variants = OrderedDict()

    def rule(self, rule):
        # Transform rule to lambda kappa rules
        output = []
        weight = rule["weight"]
        head = rule["head"]
        head_predicate = head["PREDICATE"]
        self.rule_variants.setdefault(head_predicate, 0)
        new_predicate_name = VARIANT_PREFIX + str(self.rule_variants[head_predicate]) + "_" + head_predicate.value
        self.rule_variants[head_predicate] += 1
        renamed_head = TokenRenamer("PREDICATE", head_predicate.value, new_predicate_name).transform(head)
        tail = rule["body"]
        # Add Lambda rule
        output.append(Tree('rule', [renamed_head, *tail]))
        # Add Kappa rule
        output.append(Tree('rule', [weight, head, renamed_head]))
        if has_metadata(rule):
            head = rule["head"]
            arity = len(head["term_list"].children)
            output.append(Tree('predicate_metadata', [new_predicate_name, str(arity), rule["metadata"]]))
        return output

    @staticmethod
    def rule_file(root):
        output = []
        for line in root.children:
            if isinstance(line, list):
                output += [child for child in line]
            else:
                output.append(line)
        return Tree('rule_file', output)

    @staticmethod
    def restore(root):
        rule_variants = OrderedDict()
        for line in root.children[:]:
            child = line
            if child.data == "rule" and not has_weight(child) and child["head"]["PREDICATE"].value.startswith(
                    VARIANT_PREFIX):
                rule_variants[child["head"]] = child["body"]
                root.children.remove(line)
        for rule_variant, rule_body in rule_variants.items():
            for line in root.children:
                child = line
                if child.data == "rule" and has_weight(child):
                    body = child['body'][0]
                    if body == rule_variant:
                        child.children = [child["weight"], child['head'], *rule_body]
        return root


class FixZeroArity(DFSTransformer):
    """
    Workaround for missing zero arity predicates.
    Each predicate that has zero arity will be converted to predicate of arity 1 with constant a__.
    """
    dummy_constant = Token('CONSTANT', 'a__')

    def _call_userfunc(self, root, new_children=None):
        if root in ["predicate_metadata", "predicate_offset"]:
            return lambda children: Tree(root,
                                         [children[0], Token("INT", str(max(int(children[1].value), 1))), children[2]])
        else:
            return super()._call_userfunc(root, new_children)

    @staticmethod
    def normal_atomic_formula(formula):
        predicate = formula.children[0]
        term_list = formula.children[1]
        if len(term_list.children) == 0:
            term_list = Tree('term_list', [FixZeroArity.dummy_constant])
        return Tree('normal_atomic_formula', [predicate, term_list])

    @staticmethod
    def restore(root):
        class RestoreZeroArity(DFSTransformer):
            @staticmethod
            def normal_atomic_formula(formula):
                if len(formula["term_list"].children) == 1 and formula["term_list"][0] == FixZeroArity.dummy_constant:
                    del formula["term_list"][0]
                return formula

        return RestoreZeroArity().transform(root)


class ReduceFinalKappa:
    """
    Workaround to be able to resolve and end up with every predicate instead of just predicate named finalKappa.
    """

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

    @staticmethod
    def restore(root):
        for ind, line in enumerate(root.children[:]):
            try:
                next(line.find_pred(
                    lambda x: x.data == "normal_atomic_formula" and x["PREDICATE"].value == "finalKappa"))
                root.children.remove(line)
            except StopIteration:
                pass
        return root


def list_all_predicates(root):
    atomic_formulas = root.find_data("normal_atomic_formula")
    predicates = OrderedSet()
    for atomic_formula in atomic_formulas:
        predicate_name = atomic_formula["PREDICATE"].value
        predicate_arity = len(atomic_formula["term_list"].children)
        predicates.add((predicate_name, predicate_arity))
    return predicates


class FixedOffsetTransformer:
    """
    Fix offset of every predicate to zero.
    """

    @staticmethod
    def transform(root):
        output = root.children
        for name, arity in list_all_predicates(root):
            output.append(
                Tree('predicate_offset', [Token("PREDICATE", name), str(arity),
                                          Tree('fixed_weight', [Token("SIGNED_NUMBER", '0.0')])]))
        return Tree(root.data, output)

    @staticmethod
    def restore(root):
        for line in root.children[:]:
            if line.data == "predicate_offset":
                root.children.remove(line)
        return root


class ToCodeTransformer(DFSTransformer):
    """
    Convert the tree representation of code back to text.
    """

    def _call_userfunc(self, name, new_children=None):
        if name in ["initial_weight", "metadata_value"]:
            return lambda x: x.children[0]
        elif name in ["normal_atomic_formula", "builtin_formula", "member_formula"]:
            return lambda root: root.children[0] + root.children[1]
        else:
            return super()._call_userfunc(name, new_children)

    @staticmethod
    def member_term_list(root):
        return ToCodeTransformer.term_list(root)

    @staticmethod
    def constant_list(root):
        return ToCodeTransformer.metadata(root)

    @staticmethod
    def term_list(root):
        return "(" + ",".join(root.children) + ")"

    @staticmethod
    def rule(root):
        weight_part = ToCodeTransformer.get_weight_part(root)
        if "[" in root.children[-1]:
            metadata_part = " " + root.children[-1]
        else:
            metadata_part = ""

        return weight_part + root[1 if weight_part else 0] + " :- " + ",".join(
            root[(2 if weight_part else 1):(-1 if metadata_part else None)]) + "." + metadata_part

    @staticmethod
    def get_weight_part(root):
        if ToCodeTransformer.has_weight(root):
            weight_part = root.children[0] + " "
        else:
            weight_part = ""
        return weight_part

    @staticmethod
    def has_weight(root):
        try:
            float(root.children[0].strip("<>"))  # check if is a number
            return True
        except:
            return False

    @staticmethod
    def fixed_weight(root):
        return "<" + root.children[0] + ">"

    @staticmethod
    def specialization_variable(root):
        return "^" + root.children[0]

    @staticmethod
    def metadata(root):
        return "[" + ",".join(root.children) + "]"

    @staticmethod
    def predicate_metadata(root):
        return root.children[0] + "/" + root.children[1] + " " + root.children[2]

    @staticmethod
    def predicate_offset(root):
        return root.children[0] + "/" + root.children[1] + " " + root.children[2]

    @staticmethod
    def fact(root):
        weight_part = ToCodeTransformer.get_weight_part(root)
        return weight_part + root.children[1 if ToCodeTransformer.has_weight(root) else 0] + "."

    @staticmethod
    def weighted_conjunction(root):
        return root.children[0] + " " + ",".join(root.children[1:]) + "."

    @staticmethod
    def rule_file(root):
        return "\n".join(root.children)


def transform_specialization(text: str) -> str:
    tree = neurologic_parser.parse(text)
    range_transformed = RangePredicateTransformer().transform(tree)
    unfolded_specialization = RuleSpecializationTransformer().transform(range_transformed)
    transformed_code = ToCodeTransformer().transform(unfolded_specialization)
    return transformed_code


def transform(text: str) -> str:
    """
    Parse input template, run all transformation on it and return the transformed text representation of it.
    """
    logger.debug(f"Transforming code: {text}")
    tree = neurologic_parser.parse(text)
    range_transformed = RangePredicateTransformer().transform(tree)
    unfolded_specialization = RuleSpecializationTransformer().transform(range_transformed)
    logger.debug(f"Code after handling special predicates:\n\n{ToCodeTransformer().transform(unfolded_specialization)}")
    fixed_arity = FixZeroArity().transform(unfolded_specialization)
    reduced_final_kappa = ReduceFinalKappa().transform(fixed_arity)
    fixed_offset = FixedOffsetTransformer().transform(reduced_final_kappa)
    lambda_kappa = LambdaKappaTransformer().transform(fixed_offset)
    transformed_code = ToCodeTransformer().transform(lambda_kappa)
    logger.debug(f"Transformed code: {transformed_code}")
    return transformed_code


def transform_result(text):
    """
    Parse learned template, run all transformation on it and return the transformed text representation of it.
    """
    tree = neurologic_parser.parse(text)
    logger.debug(f"Transforming code: {text}")
    joined_kappa_lambda = LambdaKappaTransformer.restore(tree)
    removed_offset = FixedOffsetTransformer().restore(joined_kappa_lambda)
    removed_final_kappa = ReduceFinalKappa().restore(removed_offset)
    fixed_arity = FixZeroArity().restore(removed_final_kappa)
    transformed_code = ToCodeTransformer().transform(fixed_arity)
    logger.debug(f"Transformed code: {transformed_code}")
    return transformed_code
