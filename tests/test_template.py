import logging

from neurologic.template_transformer import transform

input_text = r"""
0.0 winner(Group1,Group2) :- nice(jenda),_member(Group1,[1,2,3]),_member(Group2,[a,b,c]). [lukasiewicz,^Group1,^Group2]
0.0 winner() :- nice(jenda). [lukasiewicz]
"""
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    result = transform(input_text)