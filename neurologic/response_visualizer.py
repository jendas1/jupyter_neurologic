import os
from collections import OrderedDict
from functools import lru_cache

import holoviews as hv
import jnius_config
from lark import Tree
from lark.lexer import Token

from neurologic import ToCodeTransformer, RangePredicateTransformer, RuleSpecializationTransformer
from neurologic.common import weights_from_ser
from neurologic.config import neurologic_parser
from neurologic.examples_transformer import transform_from_tree

jnius_config.set_classpath(os.path.join(os.path.dirname(__file__), "neurologic.jar"))
import jnius

jInt = jnius.autoclass('java.lang.Integer')
jLong = jnius.autoclass('java.lang.Long')
jFloat = jnius.autoclass('java.lang.Float')
jDouble = jnius.autoclass('java.lang.Double')
jString = jnius.autoclass('java.lang.String')
Playground = jnius.autoclass('lrnn.Playground')
Playground.init(["-r", "./.rules_raw.pl"])
memoize = lru_cache(maxsize=None)


def resolve_inout(tree: Tree):
    """
    :return: {tuple("<normal_atomic_formula>"): set("<normal_atomic_formula>")}
    """
    points = {}
    for rule in tree.children:
        point = points.get(tuple(rule["body"]), set())
        point.add(rule["head"])
        points[tuple(rule["body"])] = point
    return points


def number_formulas(transformed_tree: Tree):
    counter = 0
    formula_number = OrderedDict()
    for rule in transformed_tree.children:
        formula = rule["head"]
        if formula not in formula_number:
            formula_number[formula] = counter
            counter += 1
    return formula_number


def _get_outputs(points, weights):
    """
    :param points:
    :param weights:
    :return: {tuple(<normal_atomic_formula>): {<normal_atomic_formula>: <int>}}
    """
    Playground.setSharedWeights(weights)
    for point, dimensions in points.items():
        points[point] = {}
        for i, dimension in enumerate(dimensions):
            example_text = transform_from_tree(Tree('rule', [
                Tree("initial_weight", [Token("SIGNED_NUMBER", '0.0')]), dimension, *point]))
            example = memoize(Playground.createExample)(example_text)
            value = Playground.evaluateExample(example)
            points[point][dimension] = value
    return points


def NdPoints(data, labels, **kwargs):
    tick_labels = []
    for index, dimension in enumerate(kwargs["kdims"]):
        tick_labels.append((index, dimension.label))
    plot = hv.Curve([])(plot={"xticks": tick_labels})
    for coords, label in zip(data, labels):
        translated_coords = []
        for ind, value in enumerate(coords):
            if ind is not None:
                translated_coords.append((ind, value))
        plot *= hv.Curve(translated_coords, label=label)
        plot *= hv.Points(translated_coords, label=label)
    return plot


def _get_coords(points, formula_number):
    coords = {}
    for point, dimensions in points.items():
        point_coords = [None] * len(formula_number)
        for dim, value in dimensions.items():
            point_coords[formula_number[dim]] = value
        coords[point] = point_coords
    return coords


def _plot_response(points, formula_number, output_folder):
    def _plot_step(step, restart, fold):
        weights = memoize(weights_from_ser)(output_folder, restart, fold)
        current_weights = weights.T[step].tolist()
        evaluated_points = _get_outputs(points, current_weights)
        point_coords = _get_coords(evaluated_points, formula_number)
        labels = [ToCodeTransformer().transform(Tree("weighted_conjunction", ["", *point_coord])) for point_coord in
                  point_coords]
        dimensions = [hv.Dimension(ToCodeTransformer().transform(formula)) for formula in formula_number.keys()]
        return NdPoints(point_coords.values(), labels, kdims=dimensions)

    # TODO : Get ranges from config file in output folder
    return hv.DynamicMap(_plot_step, kdims=[hv.Dimension("Epoch", range=(0, 1000)),
                                            hv.Dimension("Restart", range=(0, 9)),
                                            hv.Dimension("Fold", range=(0, 3))])


def transform_response(tree: Tree) -> Tree:
    """
    Execute only the Range and RuleSpecializationTransformed on the tree.
    """
    range_transformed = RangePredicateTransformer().transform(tree)
    unfolded_specialization = RuleSpecializationTransformer().transform(range_transformed)
    return unfolded_specialization


def plot_response(response_file, output_folder) -> hv.DynamicMap:
    tree = neurologic_parser.parse(open(response_file, 'r').read())
    transformed_tree = transform_response(tree)
    points = resolve_inout(transformed_tree)
    formula_number = number_formulas(transformed_tree)
    return _plot_response(points, formula_number, output_folder)
