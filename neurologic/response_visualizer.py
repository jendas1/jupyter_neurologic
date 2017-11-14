# View response of the evidence (input) to various predicates throughout learning
import json
import logging
import os
import re
from collections import OrderedDict
from functools import lru_cache

import holoviews as hv
import jnius_config
from IPython.core.display import display_svg
from lark import Tree
from lark.lexer import Token

from neurologic import ToCodeTransformer, RangePredicateTransformer, RuleSpecializationTransformer, \
    examples_transformer, has_weight
from neurologic.common import _task_dimensions, _svg_from_dot
from neurologic.config import neurologic_parser
from neurologic.examples_transformer import transform_from_tree
from neurologic.weights import weights_from_ser

jnius_config.set_classpath(os.path.join(os.path.dirname(__file__), "neurologic.jar"))
import jnius

jInt = jnius.autoclass('java.lang.Integer')
jLong = jnius.autoclass('java.lang.Long')
jFloat = jnius.autoclass('java.lang.Float')
jDouble = jnius.autoclass('java.lang.Double')
jString = jnius.autoclass('java.lang.String')
Playground = jnius.autoclass('lrnn.Playground')

memoize = lru_cache(maxsize=None)



def init(output_folder):
    settings = json.load(open(os.path.join(output_folder, "settings.json")))
    global_settings = json.load(open(os.path.join(output_folder, "global.json")))
    # Developer note: Update the initialization code if underlying java program changes
    Playground.init(["-r", os.path.join(output_folder, "rules.pl"),
                     "-ac", settings["activations"],
                     "-gr", settings["grounding"],
                     "-tt", global_settings["taskType"],
                     "-out", os.path.join(output_folder, "response_visualizer", "")])


def resolve_inout(transformed_template: Tree):
    """
    Get points and their coordinate names from the template. Returns dictionary (list) of point names as keys and their
    coordinates as values.
    :return: {tuple("<normal_atomic_formula>"): set("<normal_atomic_formula>")}
    """
    points = {}
    for rule in transformed_template.children:
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


create_remember_example = memoize(Playground.createExample)


def _get_outputs(points, weights):
    """
    Compute output value (response) for each point and each of its dimension (target predicate).
    :return: {tuple(<normal_atomic_formula>): {<normal_atomic_formula>: <int>}}
    """
    Playground.setSharedWeights(weights)
    for point, dimensions in points.items():
        points[point] = {}
        for i, dimension in enumerate(dimensions):
            example_text = transform_from_tree(Tree('rule', [
                Tree("initial_weight", [Token("SIGNED_NUMBER", '0.0')]), dimension, *point]))
            example = create_remember_example(example_text)
            value = Playground.evaluateExample(example)
            logging.debug(f"Evaluating {example_text}. Response {value}.")
            points[point][dimension] = value
    return points


def NdPoints(data, labels, **kwargs) -> hv.core.overlay.Overlay:
    """
    N-dimensional points
    HoloViews like method for plotting multidimensional data.
    Visualizing multidimensional data is done using parallel coordinates.
    For more info see https://en.wikipedia.org/wiki/Parallel_coordinates .
    """
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


weights_remember_from_ser = memoize(weights_from_ser)


def _plot_response(points, formula_number, output_folder):
    def _plot_step(step, restart, fold):
        weights = weights_remember_from_ser(output_folder, restart, fold)
        current_weights = weights.T[step].tolist()
        evaluated_points = _get_outputs(points, current_weights)
        point_coords = _get_coords(evaluated_points, formula_number)
        labels = [ToCodeTransformer().transform(Tree("weighted_conjunction", ["", *point_coord])) for point_coord in
                  point_coords]
        dimensions = [hv.Dimension(ToCodeTransformer().transform(formula)) for formula in formula_number.keys()]
        return NdPoints(point_coords.values(), labels, kdims=dimensions)

    dimensions = _task_dimensions(output_folder)
    return hv.DynamicMap(_plot_step, kdims=dimensions)


def display_neural_network_of_example(example, step, output_folder, restart, fold):
    init(output_folder)
    image_file = _neural_network_from_example(example, fold, output_folder, restart, step)
    dot_file = re.sub(r".(\w)+$",".dot",image_file)
    svg_data = _svg_from_dot(dot_file)
    return display_svg(svg_data,raw=True)


def _neural_network_from_example(example, fold, output_folder, restart, step):
    example_tree = neurologic_parser.parse(example)
    rule = example_tree[0]
    if not has_weight(rule):
        rule.children.insert(0, Tree("initial_weight", [Token("SIGNED_NUMBER", "0.0")]))
    raw_example = examples_transformer.transform_from_tree(rule)
    print(raw_example)
    name = raw_example.split(" ")[1].strip(".")
    weights = weights_remember_from_ser(output_folder, restart, fold)
    current_weights = weights.T[step].tolist()
    Playground.setSharedWeights(current_weights)
    example = Playground.createExample(raw_example)
    return Playground.drawExample(example, name)


def transform_response(tree: Tree) -> Tree:
    """
    Execute only the Range and RuleSpecializationTransformed on the tree.
    """
    range_transformed = RangePredicateTransformer().transform(tree)
    unfolded_specialization = RuleSpecializationTransformer().transform(range_transformed)
    return unfolded_specialization


def plot_response(response_file: str, output_folder: str) -> hv.DynamicMap:
    init(output_folder)
    tree = neurologic_parser.parse(open(response_file, 'r').read())
    transformed_tree = transform_response(tree)
    points = resolve_inout(transformed_tree)
    formula_number = number_formulas(transformed_tree)
    return _plot_response(points, formula_number, output_folder)
