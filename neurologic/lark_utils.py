import typing

from lark import Tree
from lark.lexer import Token


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


def patch_tree(named_children: typing.Dict[str, typing.Dict[str, typing.Union[typing.Callable, int, slice]]]):
    """
    Patch :class:`lark.Tree` so it supports named indexing of children.
    :param named_children: Dictionary with tree names as keys and
                           inner dictionary with children names and its indexes as values.
    """
    import lark

    def get_index(self, item):
        if type(item) == str:
            index = named_children[self.data][item]
            if callable(index):
                index = index(self)
            return index
        else:
            return item

    def get_item(self, item):
        return self.children[get_index(self, item)]

    def set_item(self, item, value):
        self.children[get_index(self, item)] = value

    def del_item(self, item):
        del self.children[get_index(self, item)]

    lark.tree.Tree.__getitem__ = get_item
    lark.tree.Tree.__setitem__ = set_item
    lark.tree.Tree.__delitem__ = del_item


def has_weight(rule_root):
    return rule_root.children[0].data in ["fixed_weight", "initial_weight"]


def has_metadata(rule_root):
    return rule_root.children[-1].data == "metadata"


named_children = {
    "rule": {"weight": lambda root: 0 if has_weight(root) else None,
             "head": lambda root: 1 if has_weight(root) else 0,
             "body": lambda root: slice(2 if has_weight(root) else 1, -1 if has_metadata(root) else None, None),
             "metadata": lambda root: -1 if has_metadata(root) else None},
    "normal_atomic_formula": {"PREDICATE": 0, "term_list": 1},
    "predicate_metadata": {"PREDICATE": 0, "ARITY": 1, "metadata": 2},
    "predicate_offset": {"PREDICATE": 0, "ARITY": 1, "offset": 2},
    "member_formula": {"PREDICATE": 0, "term_list": 1},
}
