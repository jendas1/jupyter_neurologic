import logging

from neurologic.template_transformer import transform

input_text = r"""
0.0 winner(Group1,Group2) :- nice(jenda),range(Group1Range,1,3),_member(Group1,Group1Range)
                                        ,range(Group2Range,a,c),_member(Group2,Group2Range). [lukasiewicz,^Group1,^Group2]
0.0 winner() :- nice(jenda). [lukasiewicz]
"""
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    result = transform(input_text)