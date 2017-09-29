import os

from lark import Tree
from lark.lexer import Token

from neurologic.response_visualizer import transform_response, resolve_inout

from neurologic import neurologic_parser, ToCodeTransformer, response_visualizer


def test_response_visualizer_dummy():
    pass
    #


def test_response_transformer():
    tree = neurologic_parser.parse(response_template_input)
    transformed_tree = transform_response(tree)
    transformed_template = ToCodeTransformer().transform(transformed_tree)
    assert transformed_template == response_template_output


def test_resolve_inout():
    tree = neurologic_parser.parse(response_template_input)
    transformed_tree = transform_response(tree)
    points = resolve_inout(transformed_tree)
    assert points == points_and_coordinates


if __name__ == "__main__":
    response_visualizer.plot_response("../sample_tasks/poker_response.pl", "../outputs/poker/")[10000, 0, 0]

response_template_input = \
    "cardFromGroup(Group,0) :- card(0,2,spades),range(RangeGroup,2,5),member(Group,RangeGroup). [^Group]"

response_template_output = """\
cardFromGroup(2,0) :- card(0,2,spades).
cardFromGroup(3,0) :- card(0,2,spades).
cardFromGroup(4,0) :- card(0,2,spades).
cardFromGroup(5,0) :- card(0,2,spades)."""

points_and_coordinates = {(Tree("normal_atomic_formula", [Token("PREDICATE", 'card'), Tree("term_list",
                                                                                           [Token("CONSTANT", '0'),
                                                                                            Token("CONSTANT", '2'),
                                                                                            Token("CONSTANT",
                                                                                                  'spades')])]),): {
    Tree("normal_atomic_formula",
         [Token("PREDICATE", 'cardFromGroup'), Tree("term_list", [Token("CONSTANT", '4'), Token("CONSTANT", '0')])]),
    Tree("normal_atomic_formula",
         [Token("PREDICATE", 'cardFromGroup'), Tree("term_list", [Token("CONSTANT", '3'), Token("CONSTANT", '0')])]),
    Tree("normal_atomic_formula",
         [Token("PREDICATE", 'cardFromGroup'), Tree("term_list", [Token("CONSTANT", '2'), Token("CONSTANT", '0')])]),
    Tree("normal_atomic_formula",
         [Token("PREDICATE", 'cardFromGroup'), Tree("term_list", [Token("CONSTANT", '5'), Token("CONSTANT", '0')])])}}
