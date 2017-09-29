from neurologic.examples_transformer import transform

example = """
3 score() :- card(0,2,spades),card(1,3,spades).
"""
example_result = """3 card(0,2,spades),card(1,3,spades),__finalscore(a__)."""


def test_example_transformation():
    assert transform(example) == example_result