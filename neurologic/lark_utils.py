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


def patch_tree(named_children):
    import lark

    def get_item(self, item):
        return self.children[named_children[self.data][item] if type(item) == str else item]

    def set_item(self, item, value):
        self.children[named_children[self.data][item] if type(item) == str else item] = value

    lark.tree.Tree.__getitem__ = get_item
    lark.tree.Tree.__setitem__ = set_item

named_children = {
    "rule": {"head": 0, "body": slice(1, None, None)},
    "weighted_rule_without_metadata": {"weight": 0, "rule": 1},
    "weighted_rule_with_metadata": {"weighted_rule_without_metadata": 0, "metadata": 1},
    "normal_atomic_formula": {"PREDICATE": 0, "term_list": 1},
    "predicate_metadata": {"PREDICATE": 0, "ARITY": 1, "metadata": 2},
    "predicate_offset": {"PREDICATE": 0, "ARITY": 1, "offset": 2},
    "member_formula": {"PREDICATE": 0, "term_list": 1},
}